import json
from pathlib import Path

import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import NFRCatalog, load_catalog
from archgen.domain.research import ResearchPlan
from archgen.paths import CATALOG_DIR
from archgen.research.planner import (
    Message,
    PlannerError,
    build_planner_messages,
    plan_research,
)

BRIEF = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간 채팅 시스템 설계")
# deepseek-v4-pro가 Planner 프롬프트에 실제로 낸 응답
REAL_RESPONSE = (Path(__file__).parent / "fixtures" / "planner_response.json").read_text(
    encoding="utf-8"
)


def broken_response() -> str:
    """후보가 2개뿐인 응답. JSON으로는 맞지만 코드로 채울 수 없는 위반이라 재시도 대상이다."""
    raw = json.loads(REAL_RESPONSE)
    raw["nfr_candidates"] = raw["nfr_candidates"][:2]
    kept = {candidate["kind"] for candidate in raw["nfr_candidates"]}
    for query in raw["search_queries"]:
        query["related_nfrs"] = [r for r in query["related_nfrs"] if r in kept]
    return json.dumps(raw, ensure_ascii=False)


class FakeLLM:
    """정해 둔 응답을 차례로 돌려주고, 받은 메시지를 기록한다."""

    def __init__(self, *responses: str | Exception) -> None:
        self.responses = list(responses)
        self.calls: list[list[Message]] = []

    def __call__(self, messages: list[Message]) -> str:
        self.calls.append(messages)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def catalog() -> NFRCatalog:
    return load_catalog(CATALOG_DIR)


def test_a_valid_response_is_parsed_in_one_call(catalog: NFRCatalog) -> None:
    llm = FakeLLM(REAL_RESPONSE)

    plan = plan_research(BRIEF, catalog, llm)

    assert plan == ResearchPlan.model_validate_json(REAL_RESPONSE)
    assert llm.calls == [build_planner_messages(BRIEF, catalog)]


@pytest.mark.parametrize(
    "first",
    [broken_response(), "죄송하지만 JSON을 만들 수 없습니다.", '{"topic_summary": "잘림'],
)
def test_a_rejected_response_is_retried_once_with_the_reason(
    catalog: NFRCatalog, first: str
) -> None:
    """규칙 위반이든 깨진 JSON이든, 무엇이 틀렸는지 알려주고 한 번 더 묻는다."""
    llm = FakeLLM(first, REAL_RESPONSE)

    plan = plan_research(BRIEF, catalog, llm)

    assert plan == ResearchPlan.model_validate_json(REAL_RESPONSE)
    original = build_planner_messages(BRIEF, catalog)
    retry = llm.calls[1]
    assert retry[: len(original)] == original
    assert retry[len(original)] == {"role": "assistant", "content": first}
    assert retry[-1]["role"] == "user"
    assert len(retry) == len(original) + 2


def test_the_retry_message_says_what_was_wrong(catalog: NFRCatalog) -> None:
    """어느 필드가 틀렸는지 알려줘야 모델이 고칠 수 있다."""
    llm = FakeLLM(broken_response(), REAL_RESPONSE)

    plan_research(BRIEF, catalog, llm)

    assert "nfr_candidates" in llm.calls[1][-1]["content"]


def test_a_second_rejection_gives_up_after_exactly_two_calls(
    catalog: NFRCatalog,
) -> None:
    """재시도는 1회뿐이다. 계속 돌리면 비용만 쓰고 같은 실수를 반복한다."""
    llm = FakeLLM(broken_response(), broken_response(), REAL_RESPONSE)

    with pytest.raises(PlannerError):
        plan_research(BRIEF, catalog, llm)
    assert len(llm.calls) == 2


def test_a_failing_llm_call_is_not_retried(catalog: NFRCatalog) -> None:
    """네트워크 오류는 응답 내용 문제가 아니라서 '규칙을 고쳐라' 재시도로 풀리지 않는다."""
    llm = FakeLLM(TimeoutError("응답 없음"), REAL_RESPONSE)

    with pytest.raises(TimeoutError):
        plan_research(BRIEF, catalog, llm)
    assert len(llm.calls) == 1


def test_a_response_the_code_can_fix_is_not_retried(catalog: NFRCatalog) -> None:
    """표기 흔들림·중복 후보·없는 후보 참조는 코드가 정리한다. LLM을 다시 부르지 않는다."""
    raw = json.loads(REAL_RESPONSE)
    raw["nfr_candidates"][2]["kind"] = "Fault Tolerance"
    raw["nfr_candidates"][4] = {"kind": "latency", "reason": "중복"}
    raw["search_queries"][0]["related_nfrs"] = ["throughput"]
    llm = FakeLLM(json.dumps(raw, ensure_ascii=False), REAL_RESPONSE)

    plan_research(BRIEF, catalog, llm)

    assert len(llm.calls) == 1


@pytest.mark.parametrize("not_text", [None, [{"type": "text", "text": "{}"}]])
def test_a_non_text_response_fails_without_a_retry(
    catalog: NFRCatalog, not_text: object
) -> None:
    """None이나 블록 목록은 모델 실수가 아니라 LLM 연결부 버그다. 재시도해도 같으니 바로 실패한다."""
    llm = FakeLLM(not_text, REAL_RESPONSE)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        plan_research(BRIEF, catalog, llm)
    assert len(llm.calls) == 1


def test_planner_error_keeps_both_failure_reasons(catalog: NFRCatalog) -> None:
    """처음에 무엇이 틀렸고, 고치라고 했더니 무엇이 또 틀렸는지 둘 다 남긴다."""
    llm = FakeLLM(broken_response(), "JSON이 아니다")

    with pytest.raises(PlannerError) as caught:
        plan_research(BRIEF, catalog, llm)

    message = str(caught.value)
    assert "nfr_candidates" in message
    assert "Invalid JSON" in message
