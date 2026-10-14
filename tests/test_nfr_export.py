import json
from dataclasses import asdict
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRSelection
from archgen.domain.research import Document, ResearchResult
from archgen.export.agent import generate_rubric
from archgen.harness.checks import (
    check_criteria_count,
    check_cross_ref,
    check_levels,
    check_weight_sum,
)
from archgen.harness.runner import Runner
from archgen.render.post_render import check_rendered
from archgen.render.renderer import render_rubric

BRIEF = InterviewBrief(Seniority.SENIOR, "채팅 서비스", "장애 복구")


@pytest.fixture
def research(golden_document_ids):
    return ResearchResult(
        topic_summary="채팅 서비스 조사",
        nfr_candidates=[],
        documents=[
            Document(
                id=i, title=i, url=f"https://example.com/{i}", content=f"{i} 보존 원문"
            )
            for i in sorted(golden_document_ids)
        ],
    )


def test_generates_rubric_from_fixed_nfrs_and_validates_and_renders(
    research, golden_export
):
    selection = NFRSelection(
        confirmed_nfrs=golden_export.confirmed_nfrs, tradeoffs=golden_export.tradeoffs
    )
    llm = Mock(return_value=golden_export.rubric.model_dump_json())

    export = generate_rubric(
        BRIEF, research, selection, llm, count_tokens=lambda messages: 10000
    )

    llm.assert_called_once()
    system, user = llm.call_args.args[0]
    payload = json.loads(user["content"])
    assert payload == {
        "brief": asdict(BRIEF),
        "research": research.model_dump(),
        "selection": selection.model_dump(mode="json"),
    }
    for rule in ("0~3", "100", "2~4", "연차", "하나의 NFR", "수치", "근거"):
        assert rule in system["content"]
    assert "동등하게 충족하는 대안 설계" in system["content"]
    assert "문서 id·URL·출처 목록을 넣지 않는다" in system["content"]
    assert export == golden_export
    checks = Runner(
        [
            check_weight_sum,
            check_criteria_count,
            check_levels,
            check_cross_ref({d.id for d in research.documents}),
        ]
    )
    assert checks.run(export) == []
    md = render_rubric(export, BRIEF)
    assert check_rendered(md, export, BRIEF) == []
    assert "# 채팅 서비스" in md


def test_rubric_input_budget_includes_schema_documents_and_selection(
    research, golden_export
):
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    llm = Mock(return_value=golden_export.rubric.model_dump_json())
    counter = Mock(return_value=10001)

    with pytest.raises(ValueError, match="10,001.*10,000.*1토큰"):
        generate_rubric(BRIEF, research, selection, llm, count_tokens=counter)

    system, user = counter.call_args.args[0]
    assert "required" in system["content"]
    assert json.loads(user["content"])["research"] == research.model_dump()
    assert json.loads(user["content"])["selection"] == selection.model_dump(mode="json")
    llm.assert_not_called()


def test_regeneration_receives_previous_export_and_findings_and_keeps_nfrs(
    research, golden_export
):
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    previous = golden_export.model_copy(deep=True)
    previous.rubric.criteria[0].weight += 1
    findings = check_weight_sum(previous)
    llm = Mock(return_value=golden_export.rubric.model_dump_json())

    export = generate_rubric(
        BRIEF,
        research,
        selection,
        llm,
        count_tokens=lambda messages: 9000,
        previous=previous,
        findings=findings,
    )

    payload = json.loads(llm.call_args.args[0][1]["content"])
    assert payload["previous"] == previous.model_dump(mode="json")
    assert payload["findings"] == [f.model_dump(mode="json") for f in findings]
    assert payload["research"] == research.model_dump()
    assert "Finding" in llm.call_args.args[0][0]["content"]
    assert export == golden_export
    assert previous.rubric.criteria[0].weight != export.rubric.criteria[0].weight


@pytest.mark.parametrize("response", ["invalid JSON", '{"criteria": [{}]}'])
def test_rejects_malformed_rubric_responses(research, golden_export, response):
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    llm = Mock(return_value=response)

    with pytest.raises(ValidationError):
        generate_rubric(
            BRIEF, research, selection, llm, count_tokens=lambda messages: 9000
        )

    assert selection.confirmed_nfrs == golden_export.confirmed_nfrs
