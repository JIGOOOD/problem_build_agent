from pathlib import Path

import pytest
from pydantic import ValidationError

from archgen.domain.research import (
    CANDIDATES_MAX,
    CANDIDATES_MIN,
    NFRCandidate,
    ResearchPlan,
    SearchQuery,
)


def candidates(count: int) -> list[NFRCandidate]:
    return [
        NFRCandidate(kind=f"kind_{i}", reason=f"{i}번째 후보를 고른 이유")
        for i in range(count)
    ]


def queries(count: int) -> list[SearchQuery]:
    return [
        SearchQuery(query=f"query {i}", purpose=f"{i}번째 쿼리의 목적", related_nfrs=[])
        for i in range(count)
    ]


def a_plan(candidate_count: int = 3, query_count: int = 6) -> ResearchPlan:
    return ResearchPlan(
        topic_summary="실시간 채팅 시스템의 메시지 전달 경로를 다룬다.",
        nfr_candidates=candidates(candidate_count),
        search_queries=queries(query_count),
    )


@pytest.mark.parametrize("count", [3, 4, 5])
def test_research_plan_takes_three_to_five_candidates(count: int) -> None:
    assert len(a_plan(candidate_count=count).nfr_candidates) == count


@pytest.mark.parametrize("count", [0, 2, 6])
def test_research_plan_rejects_a_candidate_count_outside_three_to_five(
    count: int,
) -> None:
    with pytest.raises(ValidationError):
        a_plan(candidate_count=count)


def test_research_plan_rejects_more_than_six_queries() -> None:
    with pytest.raises(ValidationError):
        a_plan(query_count=7)


FIXTURE = Path(__file__).parent / "fixtures" / "planner_response.json"


def plan_dict(**overrides: object) -> dict:
    """실제 모델 응답(fixture)을 바탕으로 일부만 바꾼 dict."""
    import json

    return json.loads(FIXTURE.read_text(encoding="utf-8")) | overrides


def test_research_plan_accepts_a_real_model_response() -> None:
    """deepseek-v4-pro가 Planner 프롬프트에 실제로 낸 응답."""
    plan = ResearchPlan.model_validate(plan_dict())

    assert plan.nfr_candidates and plan.search_queries


@pytest.mark.parametrize("blank", ["", "   "])
@pytest.mark.parametrize(
    "where",
    [
        "topic_summary",
        "nfr_candidates.reason",
        "search_queries.query",
        "search_queries.purpose",
    ],
)
def test_research_plan_rejects_blank_text(where: str, blank: str) -> None:
    raw = plan_dict()
    if where == "topic_summary":
        raw["topic_summary"] = blank
    else:
        section, field = where.split(".")
        raw[section][0][field] = blank

    with pytest.raises(ValidationError):
        ResearchPlan.model_validate(raw)


@pytest.mark.parametrize(
    ("raw", "kind"),
    [
        ("latency", "latency"),
        ("Latency", "latency"),
        ("Fault Tolerance", "fault_tolerance"),
        ("fault-tolerance", "fault_tolerance"),
        (" Fault  Tolerance ", "fault_tolerance"),
    ],
)
def test_candidate_kind_is_normalized_to_snake_case(raw: str, kind: str) -> None:
    """표기 흔들림은 코드로 고친다. 이걸로 LLM을 다시 부르면 비용만 든다."""
    assert NFRCandidate(kind=raw, reason="이유").kind == kind


@pytest.mark.parametrize("kind", ["", "   ", "1latency", "처리량"])
def test_candidate_kind_that_cannot_be_normalized_is_rejected(kind: str) -> None:
    """정리해도 snake_case가 안 되는 값만 재시도 대상으로 남긴다."""
    with pytest.raises(ValidationError):
        NFRCandidate(kind=kind, reason="이유")


def test_search_query_refs_are_normalized_like_kinds() -> None:
    """kind와 참조를 같은 규칙으로 정리해야 표기 차이로 참조가 어긋나지 않는다."""
    raw = plan_dict()
    raw["search_queries"][1]["related_nfrs"] = [" Latency "]

    plan = ResearchPlan.model_validate(raw)

    assert plan.search_queries[1].related_nfrs == ["latency"]


def test_duplicate_candidate_kinds_keep_the_first_one() -> None:
    """겹친 후보는 코드로 걸러낸다. 걸러낸 뒤에도 3~5개면 그대로 쓴다."""
    raw = plan_dict()
    first_reason = raw["nfr_candidates"][0]["reason"]
    raw["nfr_candidates"][4] = {"kind": "Latency", "reason": "뒤에 나온 중복"}

    plan = ResearchPlan.model_validate(raw)

    kinds = [candidate.kind for candidate in plan.nfr_candidates]
    assert kinds == ["latency", "scalability", "fault_tolerance", "consistency"]
    assert plan.nfr_candidates[0].reason == first_reason


def test_duplicates_that_leave_too_few_candidates_are_rejected() -> None:
    """걸러낸 뒤 3개 미만이면 코드로 채울 수 없으니 재시도 대상이다."""
    raw = plan_dict()
    raw["nfr_candidates"] = raw["nfr_candidates"][:3]
    raw["nfr_candidates"][2]["kind"] = "latency"
    for query in raw["search_queries"]:
        query["related_nfrs"] = []

    with pytest.raises(ValidationError, match="3~5"):
        ResearchPlan.model_validate(raw)


def test_refs_to_unknown_kinds_are_dropped_but_the_query_stays() -> None:
    """참조만 틀렸지 검색어 자체는 쓸 만하다. 가져온 문서는 M5가 판단한다."""
    raw = plan_dict()
    raw["search_queries"][1]["related_nfrs"] = ["throughput", "latency"]
    raw["search_queries"][2]["related_nfrs"] = ["throughput"]

    plan = ResearchPlan.model_validate(raw)

    assert len(plan.search_queries) == len(raw["search_queries"])
    assert plan.search_queries[1].related_nfrs == ["latency"]
    assert plan.search_queries[2].related_nfrs == []
    assert plan.search_queries[2].query == raw["search_queries"][2]["query"]


def test_duplicates_are_removed_before_counting_candidates() -> None:
    """6개 중 1개가 중복이면 걸러서 5개다. 코드로 해결되니 재시도하지 않는다."""
    raw = plan_dict()
    raw["nfr_candidates"].append({"kind": "Latency", "reason": "중복"})

    plan = ResearchPlan.model_validate(raw)

    assert len(plan.nfr_candidates) == 5


def test_six_distinct_candidates_are_rejected() -> None:
    """어느 후보를 버릴지 코드가 판단할 수 없으니 재시도 대상이다."""
    raw = plan_dict()
    raw["nfr_candidates"].append({"kind": "throughput", "reason": "여섯 번째"})

    with pytest.raises(ValidationError, match="3~5"):
        ResearchPlan.model_validate(raw)


def test_schema_still_tells_the_model_three_to_five_candidates() -> None:
    """개수 검사를 중복 제거 뒤로 옮겨도, 구조화 출력 스키마로는 생성 단계에서 묶는다."""
    schema = ResearchPlan.model_json_schema()["properties"]["nfr_candidates"]

    assert (schema["minItems"], schema["maxItems"]) == (CANDIDATES_MIN, CANDIDATES_MAX)


@pytest.mark.parametrize(
    "raw",
    ["fault__tolerance", "fault_tolerance_", "_fault_tolerance", "Fault - Tolerance"],
)
def test_kind_underscores_are_collapsed(raw: str) -> None:
    """밑줄이 겹치거나 앞뒤에 남으면 Catalog 이름 fault_tolerance와 어긋난다."""
    assert NFRCandidate(kind=raw, reason="이유").kind == "fault_tolerance"


def test_repeated_search_queries_keep_the_first_one() -> None:
    """같은 검색을 두 번 돌리면 비용만 든다. 대소문자·공백 차이도 같은 검색어로 본다."""
    raw = plan_dict()
    first = raw["search_queries"][0]
    raw["search_queries"][3] = first | {"query": "  " + first["query"].upper() + " "}

    plan = ResearchPlan.model_validate(raw)

    queries = [query.query for query in plan.search_queries]
    assert len(queries) == len(raw["search_queries"]) - 1
    assert queries[0] == first["query"]


def test_repeated_refs_in_one_query_collapse() -> None:
    raw = plan_dict()
    raw["search_queries"][1]["related_nfrs"] = ["latency", "Latency", "scalability"]

    plan = ResearchPlan.model_validate(raw)

    assert plan.search_queries[1].related_nfrs == ["latency", "scalability"]
