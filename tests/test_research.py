import pytest
from pydantic import ValidationError

from archgen.domain.research import NFRCandidate, ResearchPlan, SearchQuery


def candidates(count: int) -> list[NFRCandidate]:
    return [
        NFRCandidate(kind=f"kind-{i}", reason=f"{i}번째 후보를 고른 이유")
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
