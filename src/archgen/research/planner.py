"""Research Planner 프롬프트를 조립한다. 스펙은 docs/nfr-design.md의 Research Planner."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.research import (
    CANDIDATES_MAX,
    CANDIDATES_MIN,
    MAX_QUERIES,
    ResearchPlan,
)
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
# 입력 목록의 한 항목이 한 줄을 차지하도록 줄바꿈·연속 공백을 접는다.
_ENV.filters["one_line"] = lambda text: " ".join(text.split())


Message = dict[str, str]
# 메시지를 받아 응답 원문(JSON 문자열)을 돌려준다. 테스트에서는 정해 둔 응답을 돌려주는 Fake로 바꾼다.
PlannerLLM = Callable[[list[Message]], str]


class PlannerError(RuntimeError):
    """재시도까지 했는데도 응답이 ResearchPlan 규칙을 지키지 않았다."""


def build_planner_messages(brief: InterviewBrief, catalog: NFRCatalog) -> list[Message]:
    """system(바뀌지 않는 지시) + user(실행마다 바뀌는 입력).

    system이 brief와 무관해야 API 프롬프트 캐시를 탄다. 개수 제약은 ResearchPlan과 같은 상수를 쓴다.
    """
    system = _ENV.get_template("planner_system.md.j2").render(
        catalog_block=catalog.to_prompt_block(),
        candidates_min=CANDIDATES_MIN,
        candidates_max=CANDIDATES_MAX,
        max_queries=MAX_QUERIES,
    )
    user = _ENV.get_template("planner_user.md.j2").render(brief=brief)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def plan_research(
    brief: InterviewBrief, catalog: NFRCatalog, llm: PlannerLLM
) -> ResearchPlan:
    """응답을 ResearchPlan으로 검증한다. 어기면 이유를 알려주고 한 번만 더 묻는다.

    LLM 호출 자체의 예외(네트워크 등)는 응답 내용 문제가 아니라서 재시도하지 않고 그대로 올린다.
    """
    messages = build_planner_messages(brief, catalog)
    first = _text(llm(messages))
    try:
        return ResearchPlan.model_validate_json(first)
    except ValidationError as error:
        first_error = error
        retry = [
            *messages,
            {"role": "assistant", "content": first},
            {"role": "user", "content": _feedback(error)},
        ]
    second = _text(llm(retry))
    try:
        return ResearchPlan.model_validate_json(second)
    except ValidationError as error:
        raise PlannerError(
            "재시도 후에도 ResearchPlan 규칙을 어겼다.\n"
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
