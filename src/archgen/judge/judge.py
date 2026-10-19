"""LLM의 의미 검증 응답을 공통 Finding으로 반환한다."""

import json
import logging
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError

from archgen.domain.brief import InterviewBrief, load_seniority_criteria
from archgen.domain.nfr import NFRExport
from archgen.domain.research import ResearchResult
from archgen.harness.findings import Finding, FindingCode, Severity
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
_LOGGER = logging.getLogger(__name__)


class _JudgeFinding(Finding):
    code: Literal[
        FindingCode.LEVEL_AMBIGUOUS,
        FindingCode.CRITERION_UNSCORABLE,
        FindingCode.LEVEL_NOT_PROGRESSIVE,
        FindingCode.NFR_REQUIREMENT_AMBIGUOUS,
        FindingCode.NFR_NOT_GROUNDED,
        FindingCode.TARGET_VALUE_FABRICATED,
    ]
    source: Literal["judge"] = "judge"


class JudgeResponse(BaseModel):
    findings: list[_JudgeFinding]


def judge_export(
    brief: InterviewBrief,
    research: ResearchResult,
    export: NFRExport,
    llm: Callable[[list[dict[str, str]]], str],
) -> list[Finding]:
    messages = [
        {
            "role": "system",
            "content": _ENV.get_template("system.md.j2").render(
                schema=json.dumps(JudgeResponse.model_json_schema(), ensure_ascii=False),
                seniority_criteria=load_seniority_criteria(),
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "brief": asdict(brief),
                    "research": research.model_dump(mode="json"),
                    "export": export.model_dump(mode="json"),
                },
                ensure_ascii=False,
            ),
        },
    ]
    raw = llm(messages)
    if not isinstance(raw, str):
        raise TypeError("Judge LLM 응답은 JSON 문자열이어야 한다.")
    try:
        return JudgeResponse.model_validate_json(raw).findings
    except ValidationError as error:
        message = "Judge 응답 스키마 위반으로 의미 검증을 건너뛰었다."
        _LOGGER.warning("%s %s", message, error)
        return [
            Finding(
                code=FindingCode.JUDGE_RESPONSE_INVALID,
                severity=Severity.WARN,
                path="judge.response",
                message=message,
                source="judge",
            )
        ]
