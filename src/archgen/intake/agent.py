"""입력 주제에 범위 확인 질문이 필요한지 판단한다."""

import json
from collections.abc import Callable, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, StrictBool, StringConstraints, model_validator

from archgen.config import bind_structured_model, build_chat_model, response_text
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ScopeJudgment(BaseModel):
    applies: StrictBool
    reason: Text


class ScopeDraft(BaseModel):
    title: Text
    scope: Text
    focus: Text


class ScopeDecision(BaseModel):
    multiple_domains: ScopeJudgment
    unclear_core_function: ScopeJudgment
    nfr_depends_on_scope: ScopeJudgment
    question: Text | None
    draft: ScopeDraft | None

    @model_validator(mode="after")
    def _require_question_or_draft(self) -> Self:
        if (self.question is None) == (self.draft is None):
            raise ValueError("question 또는 draft 중 정확히 하나가 필요하다.")
        return self


def assess_scope(
    brief: InterviewBrief | Seniority,
    llm: Callable[[list[dict[str, str]]], str] | None = None,
    *,
    history: Sequence[dict[str, str]] = (),
) -> ScopeDecision:
    """세 기준을 판단하고 질문 또는 사용자 확인을 받을 초안을 반환한다."""
    messages = [
        {
            "role": "system",
            "content": _ENV.get_template("system.md.j2").render(
                schema=json.dumps(ScopeDecision.model_json_schema(), ensure_ascii=False)
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"brief": asdict(brief)}
                if isinstance(brief, InterviewBrief)
                else {"seniority": brief},
                ensure_ascii=False,
            ),
        },
        *[dict(message) for message in history],
    ]
    if llm is None:
        model = bind_structured_model(
            build_chat_model("small", timeout=60, max_retries=0, reasoning_effort="none"),
            ScopeDecision,
        )
        raw = response_text(model.invoke(messages))
    else:
        raw = llm(messages)
    if not isinstance(raw, str):
        raise TypeError("범위 판단 LLM 응답은 JSON 문자열이어야 한다.")
    return ScopeDecision.model_validate_json(raw)
