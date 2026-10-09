"""Research Agent의 초기 조사 계획을 생성하고 검증한다."""

import json
import logging
from collections.abc import Callable
from pathlib import Path

from langchain_core.utils.function_calling import convert_to_json_schema
from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.research import (
    CANDIDATES_MAX,
    CANDIDATES_MIN,
    MAX_QUERIES,
    InitialResearchPlan,
)
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
_ENV.filters["one_line"] = lambda text: " ".join(text.split())
_LOGGER = logging.getLogger(__name__)


Message = dict[str, str]
InitialPlanLLM = Callable[[list[Message]], str]


class ResearchPlanError(RuntimeError):
    """재시도 후에도 초기 조사 계획이 검증을 통과하지 못했다."""


def bind_initial_research_model(model):
    """초기 계획의 필드 구조를 API에 전달하고 지원 제공자만 사용한다."""
    return model.bind(
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "InitialResearchPlan",
                "strict": True,
                "schema": convert_to_json_schema(InitialResearchPlan, strict=True),
            },
        },
        extra_body={"provider": {"require_parameters": True}},
    )


def build_initial_research_messages(
    brief: InterviewBrief, catalog: NFRCatalog
) -> list[Message]:
    system = _ENV.get_template("initial_system.md.j2").render(
        topic=brief.topic,
        catalog_block=catalog.to_research_prompt_block(),
        candidates_min=CANDIDATES_MIN,
        candidates_max=CANDIDATES_MAX,
        max_queries=MAX_QUERIES,
        initial_plan_schema=json.dumps(
            InitialResearchPlan.model_json_schema(), ensure_ascii=False, indent=2
        ),
    )
    user = _ENV.get_template("initial_user.md.j2").render(brief=brief)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _call_llm(llm: InitialPlanLLM, messages: list[Message]) -> str:
    for index, message in enumerate(messages):
        if set(message) != {"role", "content"}:
            raise ValueError(f"messages.{index}: 키는 정확히 role, content여야 한다.")
    return _text(llm(messages))


def plan_initial_research(
    brief: InterviewBrief, catalog: NFRCatalog, llm: InitialPlanLLM
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
        _LOGGER.error(
            "초기 조사 계획 재시도 실패. LLM 응답 원문:\n[1차]\n%s\n[2차]\n%s",
            first,
            second,
        )
        raise ResearchPlanError(
            "재시도 후에도 InitialResearchPlan 규칙을 어겼다.\n"
            f"[1차]\n{_feedback(first_error)}\n[2차]\n{_feedback(error)}"
        ) from error


def _text(response: object) -> str:
    """응답 원문은 문자열이어야 한다. 아니면 모델 실수가 아니라 연결부 버그라 재시도하지 않는다."""
    if not isinstance(response, str):
        raise TypeError(f"LLM 응답 원문은 문자열이어야 한다: {type(response).__name__}")
    return response


def _feedback(error: ValidationError) -> str:
    """무엇이 어디서 틀렸는지. 모델이 고칠 수 있도록 위치와 이유를 함께 준다."""
    lines = [
        f"- {'.'.join(str(part) for part in item['loc']) or '(전체)'}: {item['msg']}"
        for item in error.errors()
    ]
    return (
        "직전 응답이 ResearchPlan 규칙을 어겼다.\n"
        + "\n".join(lines)
        + "\n위 문제를 고쳐 같은 형식의 JSON 전체를 다시 출력하라."
    )
