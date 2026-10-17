import json
from dataclasses import asdict
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.intake.agent import assess_scope


@pytest.fixture
def answer():
    return {
        "multiple_domains": {"applies": True, "reason": "주문과 결제는 독립 영역이다."},
        "unclear_core_function": {
            "applies": True,
            "reason": "어느 흐름이 핵심인지 미정이다.",
        },
        "nfr_depends_on_scope": {
            "applies": True,
            "reason": "대상 흐름에 따라 목표가 달라진다.",
        },
        "question": "주문 관리, 결제 처리, 두 영역의 연동 중 어디를 설계할까요?",
        "draft": None,
    }


def test_assessment_passes_brief_and_three_rules_and_returns_question(answer):
    brief = InterviewBrief(Seniority.MIDDLE, "주문/결제 시스템")
    llm = Mock(return_value=json.dumps(answer))

    decision = assess_scope(brief, llm)

    assert decision.model_dump() == answer
    llm.assert_called_once()
    system, user = llm.call_args.args[0]
    assert system["role"] == "system" and user["role"] == "user"
    assert json.loads(user["content"]) == {"brief": asdict(brief)}
    for rule in (
        "독립적인 설계 영역",
        "핵심 기능",
        "NFR이 크게 달라지는가",
        "이미",
        "강제로 분리하지",
        "임의로",
        "한국어",
        "사용자 확인",
    ):
        assert rule in system["content"]
    assert "ScopeDecision" in system["content"]


def test_assessment_rejects_non_boolean_judgment(answer):
    answer["multiple_domains"]["applies"] = "true"
    llm = Mock(return_value=json.dumps(answer))

    with pytest.raises(ValidationError, match="multiple_domains.applies"):
        assess_scope(InterviewBrief(Seniority.MIDDLE, "주문/결제"), llm)

    llm.assert_called_once()


@pytest.fixture
def draft():
    return {
        "title": "결제 처리 시스템",
        "scope": "생성된 주문의 결제 요청부터 PG webhook 결과 반영까지. 환불·정산은 제외한다.",
        "focus": "중복 결제 방지와 결제 상태 일관성",
    }


def test_clear_input_returns_draft_even_when_multiple_domains_apply(answer, draft):
    brief = InterviewBrief(
        Seniority.SENIOR,
        "주문 이후 결제 요청부터 PG webhook 상태 반영까지, 중복 결제 방지 중심, 환불·정산 제외",
    )
    answer.update(question=None, draft=draft)
    llm = Mock(return_value=json.dumps(answer))

    decision = assess_scope(brief, llm)

    assert decision.question is None
    assert decision.draft.model_dump() == draft
    assert decision.multiple_domains.applies
    assert json.loads(llm.call_args.args[0][1]["content"])["brief"] == asdict(brief)


@pytest.mark.parametrize(
    "case",
    [
        "no_output",
        "both_outputs",
        "missing_judgment",
        "missing_reason",
        "blank_reason",
        "blank_question",
        "incomplete_draft",
    ],
)
def test_invalid_assessment_never_returns_a_decision(answer, draft, case):
    if case == "no_output":
        answer["question"] = None
    elif case == "both_outputs":
        answer["draft"] = draft
    elif case == "missing_judgment":
        del answer["nfr_depends_on_scope"]
    elif case == "missing_reason":
        del answer["unclear_core_function"]["reason"]
    elif case == "blank_reason":
        answer["multiple_domains"]["reason"] = " \n "
    elif case == "blank_question":
        answer["question"] = " \n "
    else:
        answer.update(question=None, draft={"scope": "결제 요청부터 결과 반영까지"})
    llm = Mock(return_value=json.dumps(answer))

    with pytest.raises(ValidationError):
        assess_scope(InterviewBrief(Seniority.MIDDLE, "주문/결제"), llm)

    llm.assert_called_once()


@pytest.mark.parametrize("response", ["not JSON", "{}", "[]", None, {"question": "질문"}])
def test_malformed_responses_propagate_without_a_ready_fallback(response):
    llm = Mock(return_value=response)
    error = ValidationError if isinstance(response, str) else TypeError

    with pytest.raises(error):
        assess_scope(InterviewBrief(Seniority.MIDDLE, "YouTube"), llm)

    llm.assert_called_once()


def test_default_assessment_uses_configured_small_model_and_strict_schema(
    monkeypatch, answer
):
    from langchain_core.messages import AIMessage

    from archgen.intake import agent

    model = Mock()
    model.bind.return_value.invoke.return_value = AIMessage(content=json.dumps(answer))
    factory = Mock(return_value=model)
    monkeypatch.setattr(agent, "build_chat_model", factory)

    result = assess_scope(InterviewBrief(Seniority.MIDDLE, "주문/결제"))

    assert factory.call_args.args == ("small",)
    assert "model" not in factory.call_args.kwargs
    assert factory.call_args.kwargs["timeout"] > 0
    assert factory.call_args.kwargs["max_retries"] == 0
    assert factory.call_args.kwargs["reasoning_effort"] == "none"
    options = model.bind.call_args.kwargs["response_format"]
    assert options["type"] == "json_schema"
    assert options["json_schema"]["strict"] is True
    assert options["json_schema"]["schema"]["additionalProperties"] is False
    assert result.model_dump() == answer


def test_model_failure_propagates_without_a_draft():
    llm = Mock(side_effect=TimeoutError("범위 판단 시간 초과"))

    with pytest.raises(TimeoutError, match="범위 판단 시간 초과"):
        assess_scope(InterviewBrief(Seniority.MIDDLE, "YouTube"), llm)

    llm.assert_called_once()


@pytest.mark.parametrize("topic", ["", " \n "])
def test_blank_topic_is_rejected_before_model_call(topic):
    llm = Mock()

    with pytest.raises(ValueError, match="주제가 비어"):
        assess_scope(InterviewBrief(Seniority.MIDDLE, topic), llm)

    llm.assert_not_called()


def test_followup_assessment_receives_complete_history_without_changing_it(answer):
    history = [
        {"role": "assistant", "content": json.dumps(answer)},
        {
            "role": "user",
            "content": "결제만, 주문 이후 결제 요청부터 webhook 결과 반영까지",
        },
    ]
    before = json.dumps(history)
    llm = Mock(return_value=json.dumps(answer))

    assess_scope(InterviewBrief(Seniority.MIDDLE, "주문/결제"), llm, history=history)

    assert llm.call_args.args[0][2:] == history
    assert json.dumps(history) == before


def test_seniority_only_input_starts_with_a_service_question(answer):
    answer["question"] = "어떤 서비스나 기능을 설계할까요?"
    llm = Mock(return_value=json.dumps(answer))

    result = assess_scope(Seniority.MIDDLE, llm)

    system, user = llm.call_args.args[0]
    assert json.loads(user["content"]) == {"seniority": "Middle"}
    assert "연차만 있고 대화가 없으면" in system["content"]
    assert result.question == answer["question"]
    assert result.draft is None
