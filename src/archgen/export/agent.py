"""보존 문서 전체에서 NFR·목표·trade-off를 선정한다."""

import json
import logging
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.nfr import NFRExport, NFRSelection, Rubric
from archgen.domain.research import ResearchResult
from archgen.harness.findings import Finding
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
_LOGGER = logging.getLogger(__name__)
MAX_INPUT_TOKENS = 10_000


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
    selection = NFRSelection.model_validate_json(_call_llm(messages, llm, count_tokens))
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
                schema=json.dumps(Rubric.model_json_schema(), ensure_ascii=False)
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        },
    ]
    rubric = Rubric.model_validate_json(_call_llm(messages, llm, count_tokens))
    return NFRExport(**selection.model_dump(), rubric=rubric)


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
