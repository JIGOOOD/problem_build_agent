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

BRIEF = InterviewBrief(Seniority.SENIOR, "채팅 서비스")


def test_agent_prompts_cover_scope_fair_levels_and_outcome_based_design(
    research, golden_export
):
    brief = InterviewBrief(
        Seniority.MIDDLE,
        "실시간 채팅 서비스",
        scope="메시지 전송부터 상대방 수신까지",
        focus="메시지 유실 방지",
    )
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
                "kind가 같다는 이유만으로 다른 요구를 제외하지 않는다",
            ),
        ),
        (
            author,
            (
                "동등하게 충족하는 대안 설계",
                "선정된 요구보다 강한 조건",
            ),
        ),
        (
            judge,
            (
                "미확정 범위를 필수 조건",
                "동등한 구현 대안",
                "선정된 요구보다 강한 조건",
                "NFR 간 충돌",
                "중복 채점",
            ),
        ),
    ):
        system = llm.call_args.args[0][0]["content"]
        payload = json.loads(llm.call_args.args[0][1]["content"])
        assert payload["brief"]["scope"] == brief.scope
        assert payload["brief"]["focus"] == brief.focus
        assert "brief.scope" in system
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
    golden_export = golden_export.model_copy(deep=True)
    extra = golden_export.rubric.criteria[-1].model_copy(deep=True)
    extra.id = "C4"
    extra.title = "집중 부하 분산"
    extra.description = "특정 대화에 요청이 집중될 때 부하를 분산하는 설계를 평가한다."
    extra.weight = 10
    for level, descriptor in zip(
        extra.levels,
        (
            "특정 대화에 요청이 집중되어 처리 병목이 생기는 상황을 고려하지 않는다.",
            "처리 서버를 늘리지만 특정 대화에 집중된 작업을 나누는 흐름은 설명하지 못한다.",
            "특정 대화의 요청 처리를 여러 작업자에 분산하는 흐름과 담당 범위를 설명한다.",
            "작업 분산 이후 남는 병목을 식별하고 처리량과 메시지 순서 보장 사이의 절충을 설명한다.",
        ),
        strict=True,
    ):
        level.descriptor = descriptor
    golden_export.rubric.criteria[-1].weight -= extra.weight
    golden_export.rubric.criteria.append(extra)
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
    for rule in (
        "0~3",
        "100",
        "2~4",
        "연차",
        "하나의 NFR",
        "수치",
        "근거",
        "여러 평가 항목",
        "반복 채점하지 않는다",
    ):
        assert rule in system["content"]
    assert "동등하게 충족하는 대안 설계" in system["content"]
    assert "Level 3에는 Level 2 설계의 대표적인 한계" not in system["content"]
    assert "문서 id·URL·출처 목록을 넣지 않는다" in system["content"]
    for rule in (
        "각 항목은 평가 대상이나 설계 판단을 구분한다",
        "점수 의미와 난이도는 아래 MD 기준만 따른다",
        "기본 설계를 먼저 정한다",
        "모든 세부 조건의 설명을 2점에 일괄 요구하지 않는다",
        "처리 조건·순서·갱신 단위",
        "관측지표·검증방법을 추가 필수 채점 조건으로 붙이지 않는다",
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
    counter = Mock(return_value=13001)

    with pytest.raises(ValueError, match="13,001.*13,000.*1토큰"):
        generate_rubric(BRIEF, research, selection, llm, count_tokens=counter)

    system, user = counter.call_args.args[0]
    assert "required" in system["content"]
    assert json.loads(user["content"])["research"] == research.model_dump()
    assert json.loads(user["content"])["selection"] == selection.model_dump(mode="json")
    assert "## Senior\n" in system["content"]
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


@pytest.mark.parametrize("seniority", list(Seniority))
@pytest.mark.parametrize("repair", [False, True])
def test_full_seniority_criteria_reach_author_budget_and_judge(
    research, golden_export, seniority, repair
):
    from archgen.paths import RESOURCES

    brief = InterviewBrief(seniority, "채팅 서비스")
    criteria = (RESOURCES / "seniority-criteria.md").read_text()
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    author = Mock(return_value=golden_export.rubric.model_dump_json())
    counter = Mock(return_value=13_000)
    export = generate_rubric(
        brief,
        research,
        selection,
        author,
        count_tokens=counter,
        previous=golden_export if repair else None,
    )
    judge = Mock(return_value='{"findings": []}')
    judge_export(brief, research, export, judge)

    assert counter.call_args.args[0] == author.call_args.args[0]
    for llm in (author, judge):
        system = llm.call_args.args[0][0]["content"]
        assert criteria in system
        assert f"## {seniority}\n" in system
        for other in Seniority:
            assert f"## {other}\n" in system
        assert "비교" in system
        assert "brief.seniority" in system
        assert "점수 의미와 난이도는 아래 MD 기준만 따른다" in system
        for removed in (
            "3점 추가 필수 요건은 1개",
            "상황 하나 → 영향 → 대응과 비용",
            "정당화만으로 3점을",
            "3점은 대표 상황 하나의 영향·대응·비용",
        ):
            assert removed not in system
        assert "Staff+" not in system


def test_author_receives_paired_golden_examples_in_the_counted_prompt(
    research, golden_export
):
    import re

    from archgen.paths import RESOURCES

    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    author = Mock(return_value=golden_export.rubric.model_dump_json())
    counter = Mock(return_value=10_000)
    generate_rubric(BRIEF, research, selection, author, count_tokens=counter)

    system = author.call_args.args[0][0]["content"]
    assert counter.call_args.args[0] == author.call_args.args[0]
    for topic, version, criterion in (("uber", "v3", "C3"), ("youtube", "v2", "C4")):
        for tier in ("middle", "senior"):
            path = RESOURCES / "golden" / topic / version / f"{topic}_{tier}.md"
            text = path.read_text().split(f"### {criterion}.", 1)[1].split("\n---", 1)[0]
            levels = re.findall(r"(?m)^\| ([0-3]) \| (.+?) \|$", text)
            assert len(levels) == 4
            for _, descriptor in levels:
                assert descriptor in system
    assert "예시의 기술·NFR·배점을 현재 주제의 필수 조건으로 복사하지 않는다" in system
