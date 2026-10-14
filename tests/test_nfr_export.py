import json
from dataclasses import asdict
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.domain.nfr import NFRSelection
from archgen.domain.research import Document, ResearchResult
from archgen.export.agent import generate_rubric, select_nfrs
from archgen.harness.checks import (
    check_criteria_count,
    check_cross_ref,
    check_levels,
    check_weight_sum,
)
from archgen.harness.runner import Runner
from archgen.judge.judge import judge_export
from archgen.paths import CATALOG_DIR
from archgen.render.post_render import check_rendered
from archgen.render.renderer import render_rubric

BRIEF = InterviewBrief(Seniority.SENIOR, "채팅 서비스", "장애 복구")


def test_agent_prompts_cover_scope_fair_levels_and_outcome_based_design(
    research, golden_export
):
    brief = InterviewBrief(Seniority.MIDDLE, "실시간 채팅 서비스")
    selector = Mock(
        return_value=NFRSelection(
            **golden_export.model_dump(exclude={"rubric"})
        ).model_dump_json()
    )
    selected = select_nfrs(
        brief,
        research,
        selector,
        catalog=load_catalog(CATALOG_DIR),
        count_tokens=lambda _: 1000,
    ).selection
    author = Mock(return_value=golden_export.rubric.model_dump_json())
    export = generate_rubric(
        brief, research, selected, author, count_tokens=lambda _: 1000
    )
    judge = Mock(return_value='{"findings": []}')
    judge_export(brief, research, export, judge)

    # 지시 전달 계약이다. 실제 생성·판별 품질을 검증하는 테스트는 아니다.
    for llm, rules in (
        (
            selector,
            (
                "확정 요구와 미확정 범위",
                "excluded_nfrs",
                "선정 이유",
                "NFR 간 충돌",
                "설계 선택의 이득·비용",
                "보장 수준을 명시",
            ),
        ),
        (
            author,
            (
                "하나의 핵심 설계 기준",
                "동등하게 충족하는 대안 설계",
                "선정된 요구보다 강한 조건",
                "정당화만으로 3점을",
                "상황 하나 → 영향 → 대응과 비용",
                "요구 수준과 무관한 추가 조건을 필수화하지 않는다",
            ),
        ),
        (
            judge,
            (
                "미확정 범위를 필수 조건",
                "동등한 구현 대안",
                "항목 간 2점 난이도",
                "하나의 핵심 설계 기준",
                "3점의 추가 판단 깊이",
                "선정된 요구보다 강한 조건",
                "정당화만으로 3점을",
                "NFR 간 충돌",
            ),
        ),
    ):
        system = llm.call_args.args[0][0]["content"]
        for rule in rules:
            assert rule in system


def test_selection_scope_and_exclusion_reasons_stay_in_json_not_rubric_sections(
    research, golden_export
):
    answer = golden_export.model_dump(exclude={"rubric"}) | {
        "scope": [
            "미확정: 기기 수와 대화방 규모. 합리적인 범위를 명시한 설계를 인정한다."
        ],
        "excluded_nfrs": [
            "security: 중요하지만 보존 문서의 설계 근거가 부족해 이번 평가에서 제외."
        ],
    }
    selected = select_nfrs(
        BRIEF,
        research,
        Mock(return_value=json.dumps(answer)),
        catalog=load_catalog(CATALOG_DIR),
        count_tokens=lambda _: 1000,
    ).selection
    export = generate_rubric(
        BRIEF,
        research,
        selected,
        Mock(return_value=golden_export.rubric.model_dump_json()),
        count_tokens=lambda _: 1000,
    )

    assert export.model_dump()["scope"] == answer["scope"]
    assert export.model_dump()["excluded_nfrs"] == answer["excluded_nfrs"]
    md = render_rubric(export, BRIEF)
    assert "**적용 범위**" not in md
    assert "**검토 후 제외한 NFR**" not in md
    assert "**선정 이유**" not in md
    assert answer["scope"][0] not in md
    assert answer["excluded_nfrs"][0] not in md
    assert check_rendered(md, export, BRIEF) == []


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
    for rule in (
        "각 항목에서는 서로 다른 결과 속성을 평가한다",
        "하나의 핵심 설계 기준",
        "3점 추가 필수 요건은 1개",
        "3점은 같은 연차의 우수한 답변",
    ):
        assert rule in system["content"]
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
    assert payload["previous"] == {"rubric": previous.rubric.model_dump(mode="json")}
    assert payload["selection"] == selection.model_dump(mode="json")
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
