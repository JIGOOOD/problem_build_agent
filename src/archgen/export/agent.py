"""보존 문서 전체에서 NFR·목표·trade-off를 선정한다."""

import json
import logging
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from archgen.domain.brief import InterviewBrief, load_seniority_criteria
from archgen.domain.catalog import NFRCatalog
from archgen.domain.nfr import NFRExport, NFRSelection, Rubric
from archgen.domain.research import ResearchResult
from archgen.export.language import check_language
from archgen.harness.findings import Finding, FindingCode, Severity
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
_LOGGER = logging.getLogger(__name__)
MAX_INPUT_TOKENS = 13_000


def rubric_repair_findings(findings: Sequence[Finding]) -> list[Finding]:
    """선정 결과는 루브릭 생성의 고정 입력이므로 보완할 수 있는 오류만 전달한다."""
    immutable = ("confirmed_nfrs", "tradeoffs", "scope", "excluded_nfrs")
    repairable = []
    for finding in findings:
        root = finding.path.removeprefix("export.").split(".", 1)[0].split("[", 1)[0]
        if finding.severity == Severity.ERROR and (
            root not in immutable or finding.code == FindingCode.NFR_NOT_COVERED
        ):
            repairable.append(finding)
    return repairable


@dataclass(frozen=True)
class SelectionResult:
    status: Literal["selected", "candidate_not_found", "insufficient_evidence"]
    selection: NFRSelection
    reason: str | None = None


def select_nfrs(
    brief: InterviewBrief,
    research: ResearchResult,
    llm: Callable[[list[dict[str, str]]], str],
    *,
    catalog: NFRCatalog,
    count_tokens: Callable[[list[dict[str, str]]], int],
) -> SelectionResult:
    if not research.documents:
        reason = "보존 문서가 없어 NFR 선정을 중단한다."
        _LOGGER.warning(reason)
        return SelectionResult(
            "candidate_not_found", NFRSelection(confirmed_nfrs=[], tradeoffs=[]), reason
        )
    messages = [
        {
            "role": "system",
            "content": _ENV.get_template("selection_system.md.j2").render(
                catalog=catalog.to_prompt_block(),
                schema=json.dumps(NFRSelection.model_json_schema(), ensure_ascii=False),
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"brief": asdict(brief), "research": research.model_dump(mode="json")},
                ensure_ascii=False,
            ),
        },
    ]
    selection = _generate(messages, llm, count_tokens, NFRSelection)
    if len(selection.confirmed_nfrs) < 2:
        reason = f"최종 NFR {len(selection.confirmed_nfrs)}개: 최소 2개에 필요한 근거가 부족하다."
        _LOGGER.warning(reason)
        return SelectionResult("insufficient_evidence", selection, reason)
    return SelectionResult("selected", selection)


def generate_rubric(
    brief: InterviewBrief,
    research: ResearchResult,
    selection: NFRSelection,
    llm: Callable[[list[dict[str, str]]], str],
    *,
    count_tokens: Callable[[list[dict[str, str]]], int],
    previous: NFRExport | None = None,
    findings: Sequence[Finding] = (),
) -> NFRExport:
    payload = {
        "brief": asdict(brief),
        "research": research.model_dump(mode="json"),
        "selection": selection.model_dump(mode="json"),
    }
    if previous is not None:
        payload["previous"] = previous.model_dump(mode="json", include={"rubric"})
        payload["findings"] = [finding.model_dump(mode="json") for finding in findings]
    messages = [
        {
            "role": "system",
            "content": _ENV.get_template("rubric_system.md.j2").render(
                schema=json.dumps(Rubric.model_json_schema(), ensure_ascii=False),
                seniority_criteria=load_seniority_criteria(),
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        },
    ]
    rubric = _generate(messages, llm, count_tokens, Rubric)
    return NFRExport(**selection.model_dump(), rubric=rubric)


def _generate(messages, llm, count_tokens, schema):
    for attempt in range(3):
        response = _call_llm(messages, llm, count_tokens)
        result = schema.model_validate_json(response)
        errors = check_language(result.model_dump(mode="json"))
        if not errors:
            return result
        feedback = "\n".join(errors)
        if attempt == 2:
            raise ValueError(
                f"언어 검증 실패: 최대 2회 재생성 후에도 위반했습니다.\n{feedback}"
            )
        _LOGGER.warning("언어 검증 위반으로 재생성 (%s/2): %s", attempt + 1, feedback)
        messages = [
            *messages,
            {"role": "assistant", "content": response},
            {
                "role": "user",
                "content": feedback + "\n위 문제를 고쳐 전체 JSON을 다시 반환하세요.",
            },
        ]


def _call_llm(messages, llm, count_tokens):
    input_tokens = count_tokens(messages)
    if input_tokens > MAX_INPUT_TOKENS:
        reason = (
            f"전체 입력 {input_tokens:,}토큰 / 제한 {MAX_INPUT_TOKENS:,}토큰: "
            f"{input_tokens - MAX_INPUT_TOKENS:,}토큰 초과로 생성을 중단한다."
        )
        _LOGGER.warning(reason)
        raise ValueError(reason)
    return llm(messages)
