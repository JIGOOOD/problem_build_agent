import json

import pytest
from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import NFRCatalog, load_catalog
from archgen.domain.research import (
    CANDIDATES_MAX,
    CANDIDATES_MIN,
    MAX_QUERIES,
    InitialResearchPlan,
)
from archgen.paths import CATALOG_DIR
from archgen.research import agent
from archgen.research.agent import build_initial_research_messages
from archgen.research.planner import PlannerError

BRIEF = InterviewBrief(topic="실시간 채팅 서비스", seniority=Seniority.MIDDLE)


def initial_response(candidate_count: int = 3) -> dict:
    kinds = [
        "latency",
        "availability",
        "consistency",
        "scalability",
        "fault_tolerance",
        "throughput",
    ][:candidate_count]
    return {
        "topic_summary": "채팅 서비스의 메시지 전달 경로를 조사한다.",
        "nfr_candidates": [
            {"kind": kind, "reason": f"채팅 서비스에서 {kind}가 중요하다."}
            for kind in kinds
        ],
        "search_queries": [
            {"query": "chat service architecture", "related_nfr": None},
            *[{"query": f"chat service {kind}", "related_nfr": kind} for kind in kinds],
        ],
    }


class FakeLLM:
    def __init__(self, *responses: dict) -> None:
        self.responses = list(responses)
        self.calls: list[list[dict[str, str]]] = []

    def __call__(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        return json.dumps(self.responses.pop(0), ensure_ascii=False)


@pytest.fixture
def catalog() -> NFRCatalog:
    return load_catalog(CATALOG_DIR)


@pytest.mark.parametrize("notes", [None, "", " \n ", "메시지 유실 최소화"])
def test_initial_prompt_includes_notes_only_when_provided(
    catalog: NFRCatalog, notes: str | None
) -> None:
    brief = InterviewBrief(
        topic="실시간 채팅 서비스", seniority=Seniority.SENIOR, notes=notes
    )

    messages = build_initial_research_messages(brief, catalog)

    content = "\n".join(message["content"] for message in messages)
    if brief.notes:
        assert brief.notes in content
        assert "사용자 중점 요구사항" in content
    else:
        assert "사용자 중점 요구사항" not in content


def test_initial_prompt_prioritizes_official_sources_when_generating_queries(
    catalog: NFRCatalog,
) -> None:
    messages = build_initial_research_messages(BRIEF, catalog)

    system = messages[0]["content"]
    assert (
        "검색어는 공식 기술 문서와 공식 Engineering / Technical Blog를 우선 찾도록 만든다."
        in system
    )
    assert '"official documentation", "engineering blog"' in system
    assert "출처 검색 표현을 넣어도 주제 맥락과 해당 NFR을 유지한다." in system


def test_initial_prompt_provides_json_schema_with_required_plan_and_query_fields(
    catalog: NFRCatalog,
) -> None:
    messages = build_initial_research_messages(BRIEF, catalog)

    system = messages[0]["content"]
    _, marker, schema_text = system.partition("# 출력 JSON Schema\n\n")
    assert marker
    schema = json.loads(schema_text)
    assert schema == InitialResearchPlan.model_json_schema()
    assert schema["required"] == ["topic_summary", "nfr_candidates", "search_queries"]
    assert schema["$defs"]["InitialSearchQuery"]["required"] == ["query", "related_nfr"]


def test_initial_prompt_excludes_seniority(catalog: NFRCatalog) -> None:
    brief = InterviewBrief(topic="실시간 채팅 서비스", seniority=Seniority.SENIOR)

    messages = build_initial_research_messages(brief, catalog)

    content = "\n".join(message["content"] for message in messages)
    assert str(brief.seniority) not in content


def test_initial_prompt_carries_topic_catalog_and_count_limits(
    catalog: NFRCatalog,
) -> None:
    brief = InterviewBrief(topic="실시간 채팅 서비스", seniority=Seniority.MIDDLE)

    messages = build_initial_research_messages(brief, catalog)

    system, user = (message["content"] for message in messages)
    assert brief.topic in user
    for entry in catalog.entries:
        assert f"- {entry.name}: {' '.join(entry.meaning.split())}" in system
        for condition in entry.important_when:
            assert " ".join(condition.split()) in system
    assert f"{CANDIDATES_MIN}~{CANDIDATES_MAX}개" in system
    assert f"{MAX_QUERIES}개 이하" in system


def test_initial_prompt_catalog_contains_only_name_meaning_and_important_when() -> None:
    catalog = NFRCatalog.model_validate(
        {
            "entries": [
                {
                    "name": "latency",
                    "category": "UNIQUE_CATEGORY",
                    "meaning": "고유한 뜻\n여러 줄",
                    "important_when": ["고유한 조건\n첫 번째", "고유한 조건 두 번째"],
                    "examples": ["제외할 고유한 예시"],
                    "common_tradeoffs": [
                        {
                            "against": "unique_tradeoff",
                            "reason": "제외할 고유한 상충 이유",
                        }
                    ],
                }
            ]
        }
    )

    system = build_initial_research_messages(BRIEF, catalog)[0]["content"]
    catalog_section = system.split("# NFR Catalog\n\n", 1)[1].split("\n\n# 출력", 1)[0]

    assert catalog_section == (
        "- latency: 고유한 뜻 여러 줄\n"
        "  중요한 경우: 고유한 조건 첫 번째; 고유한 조건 두 번째"
    )
    assert "제외할 고유한 예시" not in system
    assert "제외할 고유한 상충 이유" not in system


@pytest.mark.parametrize("candidate_count", [3, 4, 5])
def test_initial_plan_returns_valid_candidates_and_corresponding_queries(
    catalog: NFRCatalog, candidate_count: int
) -> None:
    response = initial_response(candidate_count)
    llm = FakeLLM(response)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.topic_summary == response["topic_summary"]
    assert [candidate.model_dump() for candidate in plan.nfr_candidates] == (
        response["nfr_candidates"]
    )
    assert [query.model_dump() for query in plan.search_queries] == (
        response["search_queries"]
    )
    assert len(llm.calls) == 1


def test_initial_plan_sends_exact_message_keys_and_roles_to_llm(
    catalog: NFRCatalog,
) -> None:
    llm = FakeLLM(initial_response())

    agent.plan_initial_research(BRIEF, catalog, llm)

    assert len(llm.calls) == 1
    messages = llm.calls[0]
    assert [set(message) for message in messages] == [
        {"role", "content"},
        {"role", "content"},
    ]
    assert [message["role"] for message in messages] == ["system", "user"]


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("key", ["role", "content"])
@pytest.mark.parametrize("form", ["uppercase", "spaces", "prefix_suffix"])
def test_initial_plan_rejects_invalid_message_keys_before_calling_llm(
    catalog: NFRCatalog,
    monkeypatch: pytest.MonkeyPatch,
    index: int,
    key: str,
    form: str,
) -> None:
    messages = build_initial_research_messages(BRIEF, catalog)
    replacement = {
        "uppercase": key.upper(),
        "spaces": f" {key} ",
        "prefix_suffix": f"xxx{key}xxx",
    }[form]
    messages[index][replacement] = messages[index].pop(key)
    monkeypatch.setattr(agent, "build_initial_research_messages", lambda *_: messages)
    llm = FakeLLM(initial_response())

    with pytest.raises(ValueError, match="키"):
        agent.plan_initial_research(BRIEF, catalog, llm)

    assert llm.calls == []


def test_initial_plan_keeps_first_duplicate_query_without_retry(
    catalog: NFRCatalog,
) -> None:
    response = initial_response(5)
    expected_queries = list(response["search_queries"])
    response["search_queries"].append(
        {"query": "  CHAT   SERVICE ARCHITECTURE  ", "related_nfr": None}
    )
    llm = FakeLLM(response)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert [query.model_dump() for query in plan.search_queries] == expected_queries
    assert len(llm.calls) == 1


@pytest.mark.parametrize("topic_count", [0, 2])
def test_initial_plan_retries_when_topic_query_count_is_invalid(
    catalog: NFRCatalog, topic_count: int
) -> None:
    invalid = initial_response()
    invalid["search_queries"] = invalid["search_queries"][1:]
    invalid["search_queries"].extend(
        {"query": f"chat architecture overview {index}", "related_nfr": None}
        for index in range(topic_count)
    )
    valid = initial_response()
    llm = FakeLLM(invalid, valid)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.model_dump() == valid
    assert len(llm.calls) == 2
    assert llm.calls[1][:-2] == llm.calls[0]
    assert llm.calls[1][-2] == {
        "role": "assistant",
        "content": json.dumps(invalid, ensure_ascii=False),
    }
    assert llm.calls[1][-1]["role"] == "user"
    assert "주제 쿼리" in llm.calls[1][-1]["content"]


@pytest.mark.parametrize("candidate_count", [0, 2, 6])
def test_initial_plan_retries_when_candidate_count_is_invalid(
    catalog: NFRCatalog, candidate_count: int
) -> None:
    valid = initial_response()
    llm = FakeLLM(initial_response(candidate_count), valid)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.model_dump() == valid
    assert len(llm.calls) == 2
    assert "후보" in llm.calls[1][-1]["content"]


@pytest.mark.parametrize("candidate_count", [2, 5])
def test_initial_plan_deduplicates_normalized_candidates_before_counting(
    catalog: NFRCatalog, candidate_count: int
) -> None:
    response = initial_response(candidate_count)
    expected = initial_response(candidate_count if candidate_count == 5 else 3)
    duplicate = dict(response["nfr_candidates"][-1])
    duplicate["kind"] = duplicate["kind"].replace("_", " ").upper()
    response["nfr_candidates"].append(duplicate)
    llm = FakeLLM(response, expected)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.model_dump() == expected
    assert len(llm.calls) == (1 if candidate_count == 5 else 2)


@pytest.mark.parametrize("candidate_count", [3, 5])
def test_initial_plan_retries_when_candidate_has_multiple_queries(
    catalog: NFRCatalog, candidate_count: int
) -> None:
    invalid = initial_response(candidate_count)
    invalid["search_queries"].append(
        {"query": "chat service API latency SLA", "related_nfr": "LATENCY"}
    )
    valid = initial_response(candidate_count)
    llm = FakeLLM(invalid, valid)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.model_dump() == valid
    assert len(llm.calls) == 2
    assert "latency" in llm.calls[1][-1]["content"]
    assert "2개" in llm.calls[1][-1]["content"]


@pytest.mark.parametrize("missing_query", ["remove", "blank", "duplicate"])
def test_initial_plan_retries_when_candidate_has_no_query_after_cleanup(
    catalog: NFRCatalog, missing_query: str
) -> None:
    invalid = initial_response()
    if missing_query == "remove":
        invalid["search_queries"].pop()
    elif missing_query == "blank":
        invalid["search_queries"][-1]["query"] = "   "
    else:
        invalid["search_queries"][-1]["query"] = invalid["search_queries"][1]["query"]
    valid = initial_response()
    llm = FakeLLM(invalid, valid)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.model_dump() == valid
    assert len(llm.calls) == 2
    assert "consistency" in llm.calls[1][-1]["content"]
    assert "0개" in llm.calls[1][-1]["content"]


@pytest.mark.parametrize(
    ("second_violation", "expected_second_reason"),
    [
        (
            "topic",
            "search_queries: 주제 쿼리는 정확히 1개여야 한다. 현재 0개다.",
        ),
        (
            "candidates",
            "nfr_candidates: 후보는 3~5개여야 한다. 현재 2개다.",
        ),
        (
            "multiple",
            "search_queries: 후보 latency의 쿼리는 1개여야 한다. 현재 2개다.",
        ),
        (
            "missing",
            "search_queries: 후보 consistency의 쿼리는 1개여야 한다. 현재 0개다.",
        ),
    ],
)
def test_initial_plan_raises_planner_error_after_only_one_retry(
    catalog: NFRCatalog, second_violation: str, expected_second_reason: str
) -> None:
    first = initial_response()
    first["search_queries"].pop(0)
    second = initial_response(2 if second_violation == "candidates" else 3)
    if second_violation == "topic":
        second["search_queries"].pop(0)
    elif second_violation == "multiple":
        second["search_queries"].append(
            {"query": "chat API latency SLA", "related_nfr": "latency"}
        )
    elif second_violation == "missing":
        second["search_queries"].pop()
    llm = FakeLLM(first, second, initial_response())

    with pytest.raises(PlannerError) as raised:
        agent.plan_initial_research(BRIEF, catalog, llm)

    assert len(llm.calls) == 2
    assert len(llm.responses) == 1
    _, first_marker, details = str(raised.value).partition("[1차]")
    first_reason, second_marker, second_reason = details.partition("[2차]")
    assert first_marker and second_marker
    assert "search_queries: 주제 쿼리는 정확히 1개여야 한다. 현재 0개다." in first_reason
    assert expected_second_reason in second_reason

    cause = raised.value.__cause__
    assert isinstance(cause, ValidationError)
    errors = cause.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "value_error"
    assert errors[0]["msg"] == f"Value error, {expected_second_reason}"


def test_initial_plan_logs_violation_reason_when_retrying(
    catalog: NFRCatalog, caplog: pytest.LogCaptureFixture
) -> None:
    invalid = initial_response()
    invalid["search_queries"].pop(0)
    llm = FakeLLM(invalid, initial_response())
    caplog.set_level("WARNING", logger="archgen.research.agent")

    agent.plan_initial_research(BRIEF, catalog, llm)

    records = [
        record for record in caplog.records if record.name == "archgen.research.agent"
    ]
    assert len(records) == 1
    assert records[0].levelname == "WARNING"
    message = records[0].getMessage()
    assert message.startswith("초기 조사 계획 응답 위반으로 1회 재시도한다: ")
    assert (
        "- (전체): Value error, search_queries: "
        "주제 쿼리는 정확히 1개여야 한다. 현재 0개다."
    ) in message.splitlines()


@pytest.mark.parametrize("candidate_count", [3, 5])
def test_initial_plan_retries_instead_of_returning_extra_unlinked_queries(
    catalog: NFRCatalog, candidate_count: int
) -> None:
    invalid = initial_response(candidate_count)
    invalid["search_queries"].append(
        {"query": "chat service cost optimization", "related_nfr": "cost"}
    )
    valid = initial_response(candidate_count)
    llm = FakeLLM(invalid, valid)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert plan.model_dump() == valid
    assert len(llm.calls) == 2
    assert "search_queries" in llm.calls[1][-1]["content"]


@pytest.mark.parametrize("blank", ["", " \n \t"])
def test_initial_plan_removes_blank_queries_before_validation(
    catalog: NFRCatalog, blank: str
) -> None:
    response = initial_response(5)
    expected_queries = list(response["search_queries"])
    response["search_queries"].extend(
        [
            {"query": blank, "related_nfr": None},
            {"query": blank, "related_nfr": "latency"},
        ]
    )
    llm = FakeLLM(response)

    plan = agent.plan_initial_research(BRIEF, catalog, llm)

    assert [query.model_dump() for query in plan.search_queries] == expected_queries
    assert len(llm.calls) == 1
