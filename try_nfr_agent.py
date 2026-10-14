"""실행: uv run python try_nfr_agent.py [M4의 result.json 경로].

경로 생략 시 최신 M4 결과를 사용한다. 주제·notes는 M4 기록에서 복원하며
--topic / --notes / --seniority로 지정할 수도 있다. 기존 .env의 small 모델을 쓴다.
.archgen/nfr-agent/<실행>/에 run.log, LLM 입출력, selection.json,
nfr_export.json, 검사 결과, 검증을 통과한 nfr_rubric.md를 저장한다.
입력 10K 제한은 o200k_base 추정값이며 API의 실제 토큰 사용량은 응답에 따로 남긴다.
"""

import argparse
import json
import logging
import tempfile
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread

from langchain_core.messages import convert_to_messages

from archgen.config import build_chat_model, response_text
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.domain.research import ResearchResult
from archgen.export.agent import generate_rubric, select_nfrs
from archgen.harness.checks import (
    check_criteria_count,
    check_cross_ref,
    check_levels,
    check_weight_sum,
)
from archgen.harness.findings import Severity
from archgen.harness.runner import Runner
from archgen.paths import CATALOG_DIR, PROJECT_ROOT
from archgen.render.post_render import check_rendered
from archgen.render.renderer import render_rubric
from try_research import llm_deadline, save_json

_LOGGER = logging.getLogger("archgen.export.manual")


def _brief(source, topic, seniority, notes):
    saved = {}
    trace = source.parent / "step-01-llm.json"
    if trace.exists():
        for message in json.loads(trace.read_text()).get("messages", []):
            if message.get("role") == "user":
                for line in message.get("content", "").splitlines():
                    if line.startswith("- 주제: "):
                        saved["topic"] = line.removeprefix("- 주제: ")
                    if line.startswith("- 사용자 중점 요구사항: "):
                        saved["notes"] = line.removeprefix("- 사용자 중점 요구사항: ")
    log = source.parent / "run.log"
    if "topic" not in saved and log.exists():
        for line in log.read_text().splitlines():
            if line.startswith("주제: "):
                saved["topic"] = line.removeprefix("주제: ")
                break
    if not (topic or saved.get("topic")):
        raise ValueError("M4 기록에서 주제를 찾지 못했습니다. --topic을 지정하세요.")
    return InterviewBrief(seniority, topic or saved["topic"], notes or saved.get("notes"))


def run(
    research_path=None,
    *,
    topic=None,
    seniority=Seniority.MIDDLE,
    notes=None,
    log_root=None,
    llm_timeout=300,
):
    log_root = Path(log_root) if log_root else PROJECT_ROOT / ".archgen" / "nfr-agent"
    log_root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(
        tempfile.mkdtemp(
            prefix=datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S-"), dir=log_root
        )
    )
    logger = logging.getLogger("archgen.export")
    old_level = logger.level
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(run_dir / "run.log", encoding="utf-8"),
    ]
    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        _LOGGER.info("실행 로그: %s", run_dir)
        if research_path is None:
            results = list(
                (PROJECT_ROOT / ".archgen" / "research-agent").glob("*/result.json")
            )
            if not results:
                raise ValueError(
                    "저장된 M4 result.json이 없습니다. 먼저 try_research_agent.py를 실행하세요."
                )
            research_path = max(results, key=lambda p: p.stat().st_mtime_ns)
        source = Path(research_path).resolve()
        research = ResearchResult.model_validate_json(source.read_text(encoding="utf-8"))
        brief = _brief(source, topic, seniority, notes)
        save_json(
            run_dir / "input.json",
            {
                "source": str(source),
                "brief": asdict(brief),
                "research": research.model_dump(mode="json"),
            },
        )
        _LOGGER.info(
            "M4 입력: %s | 주제: %s | 연차: %s | 후보 %d개 · 문서 %d개",
            source,
            brief.topic,
            brief.seniority,
            len(research.nfr_candidates),
            len(research.documents),
        )
        model = build_chat_model(
            "small", timeout=llm_timeout, max_retries=0, tiktoken_model_name="gpt-4o"
        )
        json_model = model.bind(response_format={"type": "json_object"})
        _LOGGER.info(
            "모델: %s | 입력 제한: 10K | 토큰 수는 o200k_base 추정값", model.model_name
        )
        calls = 0

        def count_tokens(messages):
            save_json(run_dir / f"llm-{calls + 1:02d}-input.json", messages)
            count = model.get_num_tokens_from_messages(convert_to_messages(messages))
            _LOGGER.info("LLM %02d 입력: %s 토큰(추정)", calls + 1, f"{count:,}")
            return count

        def call_llm(messages):
            nonlocal calls
            calls += 1
            call = calls
            started = time.monotonic()
            stopped = Event()

            def heartbeat():
                while not stopped.wait(30):
                    _LOGGER.info(
                        "LLM %02d 응답 대기 %.0f초", call, time.monotonic() - started
                    )

            progress = Thread(target=heartbeat, daemon=True)
            progress.start()
            _LOGGER.info("LLM %02d 요청 시작 (상한 %g초)", call, llm_timeout)
            try:
                with llm_deadline(llm_timeout):
                    response = json_model.invoke(messages)
                save_json(
                    run_dir / f"llm-{call:02d}-response.json",
                    response.model_dump(mode="json"),
                )
                _LOGGER.info(
                    "LLM %02d 응답 완료 %.1f초 | 사용량: %s",
                    call,
                    time.monotonic() - started,
                    response.usage_metadata,
                )
                return response_text(response)
            finally:
                stopped.set()
                progress.join()

        _LOGGER.info("NFR 선정 시작")
        selected = select_nfrs(
            brief,
            research,
            call_llm,
            catalog=load_catalog(CATALOG_DIR),
            count_tokens=count_tokens,
        )
        save_json(
            run_dir / "selection.json",
            asdict(selected) | {"selection": selected.selection.model_dump(mode="json")},
        )
        _LOGGER.info(
            "NFR 선정: %s | %s",
            selected.status,
            ", ".join(n.kind for n in selected.selection.confirmed_nfrs),
        )
        if selected.status != "selected":
            raise RuntimeError(selected.reason)
        _LOGGER.info("루브릭 생성 시작")
        checks = Runner(
            [
                check_weight_sum,
                check_criteria_count,
                check_levels,
                check_cross_ref({d.id for d in research.documents}),
            ]
        )
        export, findings = None, []
        for attempt in range(3):
            export = generate_rubric(
                brief,
                research,
                selected.selection,
                call_llm,
                count_tokens=count_tokens,
                previous=export,
                findings=findings,
            )
            save_json(
                run_dir / f"nfr_export-{attempt}.json", export.model_dump(mode="json")
            )
            save_json(run_dir / "nfr_export.json", export.model_dump(mode="json"))
            findings = checks.run(export)
            save_json(
                run_dir / f"findings-{attempt}.json",
                [f.model_dump(mode="json") for f in findings],
            )
            _LOGGER.info("하네스 검증 %d: Finding %d개", attempt, len(findings))
            if not any(f.severity == Severity.ERROR for f in findings):
                break
            for finding in findings:
                _LOGGER.warning("%s %s: %s", finding.code, finding.path, finding.message)
            if attempt == 2:
                raise RuntimeError("2회 재생성 후에도 하네스 오류가 남았습니다.")
            _LOGGER.info("루브릭 재생성 %d/2", attempt + 1)
        md = render_rubric(export, brief)
        post = check_rendered(md, export, brief)
        save_json(
            run_dir / "post-render-findings.json",
            [f.model_dump(mode="json") for f in post],
        )
        if any(f.severity == Severity.ERROR for f in post):
            raise RuntimeError("렌더 검증 실패. post-render-findings.json을 확인하세요.")
        (run_dir / "nfr_rubric.md").write_text(md, encoding="utf-8")
        _LOGGER.info("완료: %s", run_dir / "nfr_rubric.md")
        return run_dir
    except BaseException as error:
        save_json(
            run_dir / "error.json", {"type": type(error).__name__, "message": str(error)}
        )
        _LOGGER.exception("실행 실패")
        raise
    finally:
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(old_level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="M4 결과 → NFR 확정 → 루브릭 생성·검증·저장"
    )
    parser.add_argument(
        "research_path", nargs="?", type=Path, help="생략하면 최신 M4 결과 사용"
    )
    parser.add_argument("--topic", help="저장된 M4 주제 대신 사용할 주제")
    parser.add_argument("--seniority", choices=list(Seniority), default=Seniority.MIDDLE)
    parser.add_argument("--notes")
    parser.add_argument("--llm-timeout", type=float, default=300)
    args = parser.parse_args()
    if args.llm_timeout <= 0:
        parser.error("--llm-timeout은 0보다 커야 합니다.")
    run(
        args.research_path,
        topic=args.topic,
        seniority=Seniority(args.seniority),
        notes=args.notes,
        llm_timeout=args.llm_timeout,
    )
