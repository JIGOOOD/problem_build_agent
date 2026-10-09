"""실행: uv run python try_research_agent.py '실시간 채팅 서비스'"""

import argparse
import json
import logging
import os
import sys
import tempfile
import time
import traceback
from collections import Counter, defaultdict
from contextlib import closing, redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread

from langchain_core.messages.utils import message_chunk_to_message
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import PrivateAttr
from tavily import TavilyClient

from archgen.config import build_chat_model
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.paths import CATALOG_DIR, PROJECT_ROOT
from archgen.research.runner import run_research
from archgen.retrieval.crawler import FetchTool, HttpFetcher, create_fetch_client
from archgen.retrieval.search import SearchTool
from try_research import Tee, llm_deadline, save_json

DEFAULT_LLM_TIMEOUT = 600


class RawTraceChatOpenAI(ChatOpenAI):
    """LangChain이 제공자 전용 필드를 버리기 전에 메타데이터를 관찰한다."""

    _raw_observer = PrivateAttr(default=None)

    def _convert_chunk_to_generation_chunk(
        self, chunk, default_chunk_class, base_generation_info
    ):
        # JSON schema 모드는 SDK가 원본 청크를 {type: "chunk", chunk: ...}로 감싼다.
        raw = chunk.get("chunk", chunk)
        if self._raw_observer is not None and "choices" in raw:
            self._raw_observer(raw)
        return super()._convert_chunk_to_generation_chunk(
            chunk, default_chunk_class, base_generation_info
        )


class TraceDisplay:
    """검색 결과의 실제 query_id와 rank로 도구 호출의 소속을 표시한다."""

    def __init__(self):
        self.queries = {}
        self.urls = {}
        self.documents = {}

    def set_plan(self, plan):
        self.queries = {
            f"query-{i}": query for i, query in enumerate(plan["search_queries"], start=1)
        }
        print("\n[조사 계획]", flush=True)
        for query_id, query in self.queries.items():
            print(
                f"  {query_id} | {query['related_nfr'] or '주제'} | {query['query']}",
                flush=True,
            )

    def context(self, call):
        args = call["args"]
        if call["name"] == "search" or (call["name"] == "fetch" and "query_id" in args):
            source = {"query_id": args.get("query_id")}
        elif call["name"] == "fetch":
            source = self.urls.get(args.get("url"), {"url": args.get("url")})
        else:
            source = self.documents.get(args.get("doc_id"), {})
        return {
            **source,
            "related_nfr": self.queries.get(source.get("query_id"), {}).get(
                "related_nfr"
            ),
        }

    def remember(self, call, content):
        try:
            value = json.loads(content)
        except (ValueError, TypeError):
            return
        if call["name"] == "search" and isinstance(value, list):
            for result in value:
                self.urls.setdefault(
                    result["url"],
                    {key: result[key] for key in ("query_id", "rank", "url")},
                )
        elif call["name"] == "fetch" and isinstance(value, list):
            for item in value:
                result = item["result"]
                if isinstance(result, dict) and "doc_id" in result:
                    self.documents[result["doc_id"]] = self.urls.get(item["url"], {})

    def detail(self, call, content):
        args = call["args"]
        try:
            value = json.loads(content)
        except (ValueError, TypeError):
            return "폐기" if content == "버림" else "실패", str(content)
        if isinstance(value, list):
            query = self.queries.get(args.get("query_id"), {}).get("query", "미확인")
            return "성공", f"검색 결과: {len(value)}개 · 검색어: {query}"
        if call["name"] == "fetch":
            return "성공", f"본문 {len(value['sentences'])}문장 · {value['url']}"
        indices = value["selected_indices"]
        selection = (
            f"문장: {indices}"
            if len(indices) <= 6
            else f"선택 문장 {len(set(indices))}개"
        )
        return (
            "성공",
            f"쿼리 누적 문서: {value['kept_documents']}개 · {selection} · {value['content_chars']}/2000자 · 제외 {len(value['skipped_indices'])}문장",
        )

    def batch(self, calls, contents=None):
        """단계 → 쿼리 → URL 순위 순으로 묶고, 긴 원문은 JSON 기록에 둔다."""
        if contents is None:
            for name, count in Counter(call["name"] for call in calls).items():
                unit = "개 쿼리" if name == "fetch" else "건"
                print(f"\n[{name.upper()} 시작] {count}{unit}", flush=True)
            return
        rows = []
        for call, content in zip(calls, contents, strict=True):
            if call["name"] == "fetch" and content.startswith("["):
                for item in json.loads(content):
                    result = item["result"]
                    rows.append(
                        (
                            {"name": "fetch", "args": {"url": item["url"]}},
                            json.dumps(result, ensure_ascii=False)
                            if isinstance(result, dict)
                            else result,
                        )
                    )
            else:
                rows.append((call, content))
        groups = defaultdict(lambda: defaultdict(list))
        for call, content in rows:
            context = self.context(call)
            query_id = context.get("query_id") or "소속 미확인"
            kind = context["related_nfr"] or ("주제" if context.get("query_id") else "-")
            status, detail = self.detail(call, content)
            rank = f"#{context['rank']}" if "rank" in context else "-"
            line = f"    {rank} | {status} | {' '.join(detail.split())}"
            groups[call["name"]][(query_id, kind)].append(
                line if len(line) <= 116 else line[:113] + "..."
            )
        for name, queries in groups.items():
            count = sum(map(len, queries.values()))
            print(
                f"\n[{name.upper()} 결과] {count}건",
                flush=True,
            )
            for (query_id, kind), lines in queries.items():
                print(f"  {query_id} · {kind}", flush=True)
                print("\n".join(lines), flush=True)


class TraceLLM:
    def __init__(self, model, run_dir, timeout, *, debug=False):
        self.model = model
        self.run_dir = run_dir
        self.timeout = timeout
        self.debug = debug
        self.step = 0
        self.tools_bound = False
        self.messages = []
        self.pending_calls = []
        self.display = TraceDisplay()
        self.counts = Counter()
        self.phase = "초기 계획"
        self.phase_started = time.monotonic()
        self.waiting = False
        self.stream_stats = {}
        if isinstance(model, RawTraceChatOpenAI) and debug:
            model._raw_observer = self.record_raw_chunk

    def record_raw_chunk(self, chunk):
        """원문 대신 필드별 크기만 즉시 기록해 중단 시에도 남긴다."""
        choices = []
        for choice in chunk.get("choices", []):
            sizes = {
                key: len(value)
                if isinstance(value, str)
                else len(json.dumps(value, ensure_ascii=False))
                for key, value in (choice.get("delta") or {}).items()
                if value is not None
            }
            choices.append(
                {
                    "index": choice.get("index"),
                    "delta_chars": sizes,
                    "finish_reason": choice.get("finish_reason"),
                }
            )
        record = {
            "seconds": round(time.monotonic() - self.phase_started, 3),
            "fields": sorted(chunk),
            "choices": choices,
            "usage_present": chunk.get("usage") is not None,
        }
        path = self.run_dir / f"step-{self.step:02d}-stream.jsonl"
        with path.open("a", encoding="utf-8") as stream_log:
            stream_log.write(json.dumps(record, ensure_ascii=False) + "\n")

    def bind(self, **kwargs):
        model = self.model.bind(**kwargs)
        return RunnableLambda(lambda messages: self.invoke(messages, model=model))

    def bind_tools(self, tools):
        self.model = self.model.bind_tools(tools)
        self.tools_bound = True
        print("\n[도구 등록] search, fetch, keep", flush=True)
        return self

    def show_tool_results(self):
        if not self.pending_calls:
            return
        results = {
            message["tool_call_id"]: message
            for message in self.messages
            if message["role"] == "tool"
        }
        completed = []
        for call in self.pending_calls:
            if call["id"] in results:
                self.display.remember(call, results[call["id"]]["content"])
        for call in self.pending_calls:
            if call["id"] not in results:
                continue
            message = results[call["id"]]
            completed.append(
                {"call": call, "context": self.display.context(call), "result": message}
            )
        self.display.batch(
            [item["call"] for item in completed],
            [item["result"]["content"] for item in completed],
        )
        save_json(self.run_dir / f"step-{self.step:02d}-tools.json", completed)
        self.pending_calls = []

    def invoke(self, messages, *, model=None):
        self.messages = messages
        self.show_tool_results()
        if self.tools_bound and not self.display.queries:
            self.display.set_plan(json.loads(messages[2]["content"]))
        self.step += 1
        phase = (
            "문서 판정·도구 선택"
            if self.tools_bound
            else "초기 계획 재시도"
            if self.step > 1
            else "초기 계획 생성"
        )
        self.phase = f"LLM {self.step:02d} / {phase}"
        self.phase_started = time.monotonic()
        self.stream_stats = {
            "first_chunk_seconds": None,
            "first_output_seconds": None,
            "chunks_received": 0,
            "output_chars": 0,
        }
        self.waiting = True
        input_chars = sum(len(str(message.get("content", ""))) for message in messages)
        print(
            f"\n[LLM {self.step:02d}] {phase}",
            flush=True,
        )
        if phase == "초기 계획 재시도":
            for line in messages[-1]["content"].splitlines():
                if line.startswith("- "):
                    print(
                        f"  재시도 이유: {line.removeprefix('- ').removeprefix('(전체): ')}",
                        flush=True,
                    )
        path = self.run_dir / f"step-{self.step:02d}-llm.json"
        record = {
            "status": "running",
            "phase": phase,
            "input_chars": input_chars,
            **self.stream_stats,
        }
        if self.debug:
            record["messages"] = messages
        save_json(path, record)
        started = time.monotonic()
        try:
            # runner가 초기 계획과 도구 루프에 각각 바인딩한 모델을 사용한다.
            model = self.model if model is None else model
            with llm_deadline(self.timeout):
                response = self.read_stream(model, messages, record, started)
        except BaseException as error:
            record.update(
                status="error", error_type=type(error).__name__, error=str(error)
            )
            if isinstance(error, TimeoutError):
                print(
                    f"\n[시간 초과] LLM {self.step:02d} · {phase} · 상한 {self.timeout:g}초",
                    flush=True,
                )
                print(f"  요청·오류 기록: {path}", flush=True)
            raise
        else:
            record.update(status="completed", response=response.model_dump(mode="json"))
        finally:
            self.waiting = False
            record.update(self.stream_stats)
            record["seconds"] = time.monotonic() - started
            save_json(path, record)
        first_chunk = record["first_chunk_seconds"]
        first_output = record["first_output_seconds"]
        output_time = f"{first_output:.2f}초" if first_output is not None else "없음"
        print(
            f"  완료 {record['seconds']:.2f}초 | 첫 수신 {first_chunk:.2f}초 | 출력 시작 {output_time}",
            flush=True,
        )
        if self.debug and self.tools_bound and not response.tool_calls:
            print(f"  [종료 응답] {str(response.content)[:300]}", flush=True)
        self.pending_calls = response.tool_calls
        self.counts.update(call["name"] for call in self.pending_calls)
        stages = "/".join(
            dict.fromkeys(call["name"].upper() for call in self.pending_calls)
        )
        self.phase = f"{stages} 실행" if stages else "응답 검증·종료"
        self.phase_started = time.monotonic()
        self.display.batch(self.pending_calls)
        return response

    def read_stream(self, model, messages, record, started):
        combined = None
        try:
            with closing(model.stream(messages, stream_usage=True)) as stream:
                for chunk in stream:
                    elapsed = time.monotonic() - started
                    stats = self.stream_stats
                    if stats["first_chunk_seconds"] is None:
                        stats["first_chunk_seconds"] = elapsed
                        if self.debug:
                            print(f"  수신 시작: {elapsed:.2f}초 (첫 청크)", flush=True)
                    output_chars = len(chunk.text) + sum(
                        len(call.get("args") or "") for call in chunk.tool_call_chunks
                    )
                    if (output_chars or chunk.tool_call_chunks) and stats[
                        "first_output_seconds"
                    ] is None:
                        stats["first_output_seconds"] = elapsed
                        if self.debug:
                            print(
                                f"  출력 시작: {elapsed:.2f}초 (본문·도구 호출)",
                                flush=True,
                            )
                    stats["chunks_received"] += 1
                    stats["output_chars"] += output_chars
                    combined = chunk if combined is None else combined + chunk
            if combined is None:
                raise RuntimeError("LLM 스트림이 응답 없이 종료됐습니다.")
            return message_chunk_to_message(combined)
        except BaseException:
            if combined is not None:
                record["partial_response"] = combined.model_dump(mode="json")
            raise

    def show_elapsed(self, total):
        elapsed = time.monotonic() - self.phase_started
        timing = (
            f"{'첫 청크 대기' if not self.stream_stats['chunks_received'] else '수신 중'} {elapsed:.0f}/{self.timeout:g}초"
            if self.waiting
            else f"진행 {elapsed:.0f}초"
        )
        received = (
            f" | {self.stream_stats['chunks_received']}청크 · 본문/도구 인자 {self.stream_stats['output_chars']}자"
            if self.waiting and self.debug
            else ""
        )
        print(f"  ... {self.phase} | {timing}{received} | 전체 {total:.0f}초", flush=True)


def run(
    topic="실시간 채팅 서비스",
    *,
    notes=None,
    llm_timeout=DEFAULT_LLM_TIMEOUT,
    log_root=None,
    debug=False,
):
    model = build_chat_model(
        "small", model_class=RawTraceChatOpenAI, timeout=llm_timeout, max_retries=0
    )
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not tavily_key:
        raise RuntimeError(".env에 TAVILY_API_KEY를 설정해 주세요.")
    log_root = (
        Path(log_root)
        if log_root is not None
        else PROJECT_ROOT / ".archgen" / "research-agent"
    )
    log_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S-")
    run_dir = Path(tempfile.mkdtemp(prefix=timestamp, dir=log_root))
    llm = TraceLLM(model, run_dir, llm_timeout, debug=debug)
    started = time.monotonic()
    stopped = Event()

    def show_elapsed():
        while not stopped.wait(30):
            llm.show_elapsed(time.monotonic() - started)

    with (
        (run_dir / "run.log").open("w", encoding="utf-8") as log_file,
        redirect_stdout(Tee(sys.stdout, log_file)),
        redirect_stderr(Tee(sys.stderr, log_file)),
    ):
        logger = logging.getLogger("archgen")
        handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(handler)
        progress = Thread(target=show_elapsed, daemon=True)
        progress.start()
        print(f"실행 로그: {run_dir}", flush=True)
        print(
            f"주제: {topic}\n모델: small ({getattr(model, 'model_name', '테스트 모델')})\nLLM 호출별 상한: {llm_timeout:g}초",
            flush=True,
        )
        try:
            with create_fetch_client() as client:
                fetch = FetchTool(HttpFetcher(client))
                result = run_research(
                    InterviewBrief(topic=topic, seniority=Seniority.MIDDLE, notes=notes),
                    load_catalog(CATALOG_DIR),
                    llm,
                    SearchTool(TavilyClient(api_key=tavily_key)),
                    fetch,
                )
            llm.show_tool_results()
            save_json(run_dir / "result.json", result.model_dump())
            print(
                f"\n[결과] 후보 {len(result.nfr_candidates)}개 | 수집 {len(fetch.documents)}개 | 보존 {len(result.documents)}개",
                flush=True,
            )
            print(
                "  도구 요청: "
                + " | ".join(
                    f"{name.upper()} {llm.counts[name]}회"
                    for name in ("search", "fetch", "keep")
                ),
                flush=True,
            )
            for candidate in result.nfr_candidates:
                print(f"  {candidate.kind}: 근거 {len(candidate.doc_ids)}개", flush=True)
            print(f"전체 본문: {run_dir / 'result.json'}", flush=True)
        except BaseException:
            traceback.print_exc(file=log_file)
            raise
        finally:
            stopped.set()
            progress.join()
            llm.show_tool_results()
            if debug:
                save_json(run_dir / "messages.json", llm.messages)
            print(f"\n전체 실행 시간: {time.monotonic() - started:.2f}초", flush=True)
            logger.removeHandler(handler)
            handler.close()
    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Research runner의 실제 도구 호출 흐름을 기록한다."
    )
    parser.add_argument("topic", nargs="?", default="실시간 채팅 서비스")
    parser.add_argument("--notes")
    parser.add_argument(
        "--debug", action="store_true", help="각 LLM 입력과 최종 전체 대화도 저장한다"
    )
    parser.add_argument(
        "--llm-timeout",
        type=float,
        default=DEFAULT_LLM_TIMEOUT,
        help="LLM 호출별 제한 시간(초, 기본 600초)",
    )
    args = parser.parse_args()
    if args.llm_timeout <= 0:
        parser.error("--llm-timeout은 0보다 커야 합니다.")
    try:
        run(args.topic, notes=args.notes, llm_timeout=args.llm_timeout, debug=args.debug)
    except TimeoutError:
        raise SystemExit(1) from None
