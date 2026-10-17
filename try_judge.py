"""실행: uv run python try_judge.py — 골든 루브릭의 Judge 오탐 확인.

실제 large 모델을 호출한다. .archgen/judge/<실행>/에 입출력과 Finding을 남긴다.
Finding이 하나라도 있으면 통과시키지 않고 사람이 근거를 확인하도록 중단한다.
"""

import logging
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import yaml

from archgen.config import bind_structured_model, build_chat_model, response_text
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRExport
from archgen.domain.research import Document, ResearchResult
from archgen.judge.judge import JudgeResponse, judge_export
from archgen.paths import GOLDEN_DIR, PROJECT_ROOT
from try_research import llm_deadline, save_json


def run(*, log_root=None):
    root = Path(log_root) if log_root else PROJECT_ROOT / ".archgen" / "judge"
    root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(
        tempfile.mkdtemp(prefix=datetime.now(UTC).strftime("%Y%m%d-%H%M%S-"), dir=root)
    )
    logger = logging.getLogger("archgen.judge")
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
        logger.info("골든 Judge 검증: %s", run_dir)
        raw = yaml.safe_load((GOLDEN_DIR / "chat.yaml").read_text(encoding="utf-8"))
        brief = InterviewBrief(Seniority(raw["target_level"]), raw["topic"])
        export = NFRExport.model_validate(
            {k: raw[k] for k in ("confirmed_nfrs", "tradeoffs", "rubric")}
        )
        research = ResearchResult(
            topic_summary=brief.topic,
            nfr_candidates=[],
            documents=[
                Document(
                    id=d["id"],
                    title=d["title"],
                    url=d["url"],
                    content="\n\n".join(d["quotes"]),
                )
                for d in raw["documents"]
            ],
        )
        save_json(
            run_dir / "input.json",
            {
                "brief": asdict(brief),
                "research": research.model_dump(mode="json"),
                "export": export.model_dump(mode="json"),
            },
        )
        model = build_chat_model("large", timeout=300, max_retries=0)
        bound = bind_structured_model(model, JudgeResponse)

        def llm(messages):
            save_json(run_dir / "llm-input.json", messages)
            logger.info("Judge 요청 시작: %s", model.model_name)
            with llm_deadline(300):
                response = bound.invoke(messages)
            save_json(run_dir / "llm-response.json", response.model_dump(mode="json"))
            logger.info("Judge 응답 완료: %s", response.usage_metadata)
            return response_text(response)

        findings = judge_export(brief, research, export, llm)
        save_json(
            run_dir / "findings.json", [f.model_dump(mode="json") for f in findings]
        )
        save_json(
            run_dir / "status.json",
            {"passed": not findings, "findings_count": len(findings)},
        )
        for finding in findings:
            logger.warning(
                "%s %s %s: %s",
                finding.severity,
                finding.code,
                finding.path,
                finding.message,
            )
        if findings:
            raise RuntimeError(
                f"골든 산출물에 Finding {len(findings)}개: 오탐 여부를 검토해야 한다."
            )
        logger.info("골든 Judge 검증 통과: Finding 0개")
        return run_dir
    except Exception as error:
        save_json(
            run_dir / "error.json", {"type": type(error).__name__, "message": str(error)}
        )
        logger.exception("Judge 검증 실패")
        raise
    finally:
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(old_level)


if __name__ == "__main__":
    run()
