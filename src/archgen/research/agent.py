"""Research Agent의 초기 조사 계획을 생성하고 검증한다."""

import logging
from pathlib import Path

from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.research import (
    CANDIDATES_MAX,
    CANDIDATES_MIN,
    MAX_QUERIES,
    InitialResearchPlan,
)
from archgen.research.planner import Message, PlannerError, PlannerLLM, _feedback, _text
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
_ENV.filters["one_line"] = lambda text: " ".join(text.split())
_LOGGER = logging.getLogger(__name__)


def build_initial_research_messages(
    brief: InterviewBrief, catalog: NFRCatalog
) -> list[Message]:
    system = _ENV.get_template("initial_system.md.j2").render(
        catalog_block=catalog.to_prompt_block(),
        candidates_min=CANDIDATES_MIN,
        candidates_max=CANDIDATES_MAX,
        max_queries=MAX_QUERIES,
    )
    user = _ENV.get_template("initial_user.md.j2").render(brief=brief)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _call_llm(llm: PlannerLLM, messages: list[Message]) -> str:
    for index, message in enumerate(messages):
        if set(message) != {"role", "content"}:
            raise ValueError(f"messages.{index}: 키는 정확히 role, content여야 한다.")
    return _text(llm(messages))


def plan_initial_research(
    brief: InterviewBrief, catalog: NFRCatalog, llm: PlannerLLM
) -> InitialResearchPlan:
    """응답을 정리해 검증하고, 위반 이유를 알려 한 번만 재시도한다."""
    messages = build_initial_research_messages(brief, catalog)
    first = _call_llm(llm, messages)
    try:
        return InitialResearchPlan.model_validate_json(first)
    except ValidationError as error:
        first_error = error
        _LOGGER.warning(
            "초기 조사 계획 응답 위반으로 1회 재시도한다: %s", _feedback(error)
        )
        retry = [
            *messages,
            {"role": "assistant", "content": first},
            {"role": "user", "content": _feedback(error)},
        ]
    second = _call_llm(llm, retry)
    try:
        return InitialResearchPlan.model_validate_json(second)
    except ValidationError as error:
        raise PlannerError(
            "재시도 후에도 InitialResearchPlan 규칙을 어겼다.\n"
            f"[1차]\n{_feedback(first_error)}\n[2차]\n{_feedback(error)}"
        ) from error
