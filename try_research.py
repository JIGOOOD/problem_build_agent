"""M4-1 초기 조사 계획과 M4-2 검색을 실제 API로 실행한다."""

import json
import logging
import os
import signal
import sys
import tempfile
import time
import traceback
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread

from tavily import TavilyClient

from archgen.config import build_chat_model
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.paths import CATALOG_DIR, PROJECT_ROOT
from archgen.research.agent import bind_initial_research_model, plan_initial_research
from archgen.retrieval.search import SearchTool


class _LLMDeadlineExceeded(BaseException):
    """SDK의 예외 처리와 무관하게 대기 중인 호출을 중단한다."""


@contextmanager
def llm_deadline(seconds: float):
    """Linux/WSL 메인 스레드에서 LLM 호출의 실제 경과 시간을 제한한다."""
    original_handler = signal.getsignal(signal.SIGALRM)

    def stop_call(signum, frame):
        raise _LLMDeadlineExceeded

    signal.signal(signal.SIGALRM, stop_call)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    except _LLMDeadlineExceeded:
        raise TimeoutError(
            f"LLM 호출이 실제 경과 시간 {seconds:g}초를 초과했습니다."
        ) from None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, original_handler)


def save_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main(run_dir: Path) -> None:
    model = bind_initial_research_model(
        build_chat_model("small", timeout=300, max_retries=0)
    )
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not tavily_key:
        raise RuntimeError(".env에 TAVILY_API_KEY를 설정해 주세요.")

    call_count = 0

    def call_llm(messages):
        nonlocal call_count
        call_count += 1
        request_messages = [dict(message) for message in messages]
        request_messages[0]["content"] += (
            "\n반드시 유효한 JSON 객체 하나만 출력하라. "
            "Markdown 코드 블록이나 설명을 붙이지 마라."
        )
        started = time.monotonic()
        record = {"status": "running", "tier": "small", "messages": request_messages}
        response_path = run_dir / f"llm-{call_count:02d}.json"
        save_json(response_path, record)
        try:
            with llm_deadline(60):
                response = model.invoke(request_messages)
        except BaseException as error:
            record.update(
                status="error",
                seconds=time.monotonic() - started,
                error_type=type(error).__name__,
                error=str(error),
            )
            save_json(response_path, record)
            raise
        record.update(
            status="completed",
            seconds=time.monotonic() - started,
            content=response.content,
            finish_reason=response.response_metadata.get("finish_reason"),
            usage=response.usage_metadata,
        )
        save_json(response_path, record)
        print(f"LLM 호출 완료: {time.monotonic() - started:.2f}초", flush=True)
        if not response.content:
            print(
                f"빈 응답: finish_reason={response.response_metadata.get('finish_reason')}, "
                f"usage={response.usage_metadata}",
                flush=True,
            )
        return response.content

    brief = InterviewBrief(
        topic="실시간 채팅 서비스",  # 원하는 주제로 변경한다.
        seniority=Seniority.MIDDLE,
    )

    print("M4-1: 초기 조사 계획 생성 중...", flush=True)
    started = time.monotonic()
    plan = plan_initial_research(
        brief=brief,
        catalog=load_catalog(CATALOG_DIR),
        llm=call_llm,
    )
    save_json(run_dir / "plan.json", plan.model_dump())
    print(f"M4-1 완료: {time.monotonic() - started:.2f}초", flush=True)
    print(plan.model_dump_json(indent=2), flush=True)

    # 같은 인스턴스를 사용해야 쿼리 간 URL 중복이 제거된다.
    search = SearchTool(TavilyClient(api_key=tavily_key))
    searches = []
    save_json(run_dir / "searches.json", searches)
    for index, query in enumerate(plan.search_queries, start=1):
        query_id = f"query-{index}"
        print(f"\nM4-2: {query_id} / {query.related_nfr or '주제'}", flush=True)
        print(f"검색어: {query.query}", flush=True)
        started = time.monotonic()
        results = search.search(query.query, query_id=query_id)
        searches.append(
            {
                "query_id": query_id,
                "query": query.query,
                "related_nfr": query.related_nfr,
                "seconds": time.monotonic() - started,
                "results": results
                if isinstance(results, str)
                else [result.model_dump() for result in results],
            }
        )
        save_json(run_dir / "searches.json", searches)
        print(f"검색 완료: {time.monotonic() - started:.2f}초", flush=True)
        if isinstance(results, str):
            print(results, flush=True)
        else:
            print(f"검색 결과: {len(results)}개", flush=True)
            for result in results:
                print(result.model_dump_json(), flush=True)


class Tee:
    def __init__(self, terminal, log_file):
        self.terminal = terminal
        self.log_file = log_file

    def write(self, text):
        self.log_file.write(text)
        self.log_file.flush()
        return self.terminal.write(text)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()


def run(*, log_root: Path | None = None) -> Path:
    log_root = (
        log_root if log_root is not None else PROJECT_ROOT / ".archgen" / "research"
    )
    log_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S-")
    run_dir = Path(tempfile.mkdtemp(prefix=timestamp, dir=log_root))
    total_started = time.monotonic()
    stopped = Event()

    def show_elapsed() -> None:
        while not stopped.wait(5):
            print(f"[실행 중] {time.monotonic() - total_started:.1f}초 경과", flush=True)

    with (
        (run_dir / "run.log").open("w", encoding="utf-8") as log_file,
        redirect_stdout(Tee(sys.stdout, log_file)),
        redirect_stderr(Tee(sys.stderr, log_file)),
    ):
        logger = logging.getLogger("archgen.research.agent")
        handler = logging.StreamHandler(sys.stderr)
        original_propagate = logger.propagate
        logger.addHandler(handler)
        logger.propagate = False
        print(f"실행 로그: {run_dir}", flush=True)
        progress = Thread(target=show_elapsed, daemon=True)
        progress.start()
        try:
            main(run_dir)
        except BaseException:
            traceback.print_exc(file=log_file)
            raise
        finally:
            stopped.set()
            progress.join()
            print(
                f"\n전체 실행 시간: {time.monotonic() - total_started:.2f}초", flush=True
            )
            logger.removeHandler(handler)
            logger.propagate = original_propagate
            handler.close()
    return run_dir


if __name__ == "__main__":
    run()
