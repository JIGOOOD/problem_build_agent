import json
from dataclasses import asdict
from unittest.mock import Mock

import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.domain.research import Document, NFRCandidate, ResearchResult
from archgen.export.agent import select_nfrs
from archgen.paths import CATALOG_DIR

BRIEF = InterviewBrief(Seniority.MIDDLE, "채팅 서비스")
CATALOG = load_catalog(CATALOG_DIR)


@pytest.fixture
def research():
    return ResearchResult(
        topic_summary="메시지 전달과 보존",
        nfr_candidates=[],
        documents=[
            Document(
                id="D1",
                url="https://example.com/delivery",
                title="전달",
                content="피크 부하에서 전달 지연 p99는 200ms 이하다.",
            ),
            Document(
                id="D2",
                url="https://example.com/storage",
                title="보존",
                content="응답 전 저장은 장애 시 유실을 막지만 전달 지연을 늘린다.",
            ),
        ],
    )


@pytest.fixture
def answer():
    return {
        "confirmed_nfrs": [
            {
                "id": "N1",
                "kind": "latency",
                "statement": "전달 지연 제한",
                "rationale": "전달 경로 선택에 영향",
                "target": {"value": 200, "unit": "ms", "condition": "피크 부하 p99"},
                "evidence_refs": ["D1"],
            },
            {
                "id": "N2",
                "kind": "durability",
                "statement": "수락한 메시지 보존",
                "rationale": "응답 전 저장 필요",
                "qualitative_target": "장애 시 유실 방지",
                "evidence_refs": ["D2"],
            },
        ],
        "tradeoffs": [
            {
                "id": "T1",
                "related_nfr_ids": ["N1", "N2"],
                "description": "응답 전 저장은 유실을 막지만 지연을 늘린다.",
                "evidence_refs": ["D2"],
            }
        ],
    }


@pytest.mark.parametrize("with_candidate", [False, True])
def test_passes_all_evidence_and_selection_rules_and_parses_response(
    research, answer, with_candidate
):
    if with_candidate:
        research.nfr_candidates = [
            NFRCandidate(kind="latency", reason="전달 지연", doc_ids=["D1"])
        ]
    llm = Mock(return_value=json.dumps(answer))
    counter = Mock(return_value=10000)

    result = select_nfrs(BRIEF, research, llm, catalog=CATALOG, count_tokens=counter)

    messages = llm.call_args.args[0]
    llm.assert_called_once()
    counter.assert_called_once_with(messages)
    assert [m["role"] for m in messages] == ["system", "user"]
    assert json.loads(messages[1]["content"]) == {
        "brief": asdict(BRIEF),
        "research": research.model_dump(mode="json"),
    }
    system = messages[0]["content"]
    assert CATALOG.to_prompt_block() in system
    assert "사람이 읽는 텍스트는 한국어로 작성한다" in system
    # 프롬프트 계약만 검사한다. 실제 선정 품질은 M5-4에서 사람이 검토한다.
    for rule in (
        "brief의 품질 보장을 유지하며 짧게",
        "세부 예외·해결 절차를 필수화하지 않는다",
        "연차별 평가 깊이는 Rubric에서 정한다",
        "주제 적합성",
        "문서 근거",
        "설계 영향",
        "충족하지 못하면 제외",
        "카탈로그와 초기 후보 밖",
        "보존 문서 전체",
        "중복",
        "중요도",
        "수치를 지어내지",
        "qualitative_target",
        "value가 null인 target",
        "대략적인 규모",
        "다른 서비스의 실측",
        "이번 설계의 확정 목표로 바꾸지 않는다",
        "trade-off",
        "evidence_refs",
    ):
        assert rule in system
    assert "confirmed_nfrs" in system and "required" in system
    assert result.status == "selected"
    assert result.reason is None
    assert result.selection.model_dump(exclude_unset=True) == answer


def test_no_documents_stops_without_counting_or_calling_llm(research, caplog):
    research.documents = []
    llm = Mock(return_value='{"confirmed_nfrs": [], "tradeoffs": []}')
    counter = Mock(return_value=0)

    result = select_nfrs(BRIEF, research, llm, catalog=CATALOG, count_tokens=counter)

    assert result.status == "candidate_not_found"
    assert result.selection.confirmed_nfrs == []
    assert result.selection.tradeoffs == []
    assert result.selection.scope == []
    assert result.selection.excluded_nfrs == []
    assert result.reason and result.reason in caplog.text
    llm.assert_not_called()
    counter.assert_not_called()


@pytest.mark.parametrize("nfr_count", [0, 1])
def test_insufficient_evidence_preserves_partial_output_and_reason(
    research, answer, nfr_count, caplog
):
    answer["confirmed_nfrs"] = answer["confirmed_nfrs"][:nfr_count]
    answer["tradeoffs"] = []
    llm = Mock(return_value=json.dumps(answer))

    result = select_nfrs(
        BRIEF, research, llm, catalog=CATALOG, count_tokens=lambda messages: 9000
    )

    assert result.status == "insufficient_evidence"
    assert result.selection.model_dump(exclude_unset=True) == answer
    assert result.reason and str(nfr_count) in result.reason
    assert result.reason in caplog.text


def test_over_budget_stops_before_llm_without_truncating_input(research, answer, caplog):
    before = research.model_dump(mode="json")
    llm = Mock(return_value=json.dumps(answer))
    counter = Mock(return_value=13001)

    with pytest.raises(ValueError, match="13,001.*13,000.*1토큰"):
        select_nfrs(BRIEF, research, llm, catalog=CATALOG, count_tokens=counter)

    counter.assert_called_once()
    messages = counter.call_args.args[0]
    assert CATALOG.to_prompt_block() in messages[0]["content"]
    assert "confirmed_nfrs" in messages[0]["content"]
    assert "Breadth" not in messages[0]["content"]
    assert json.loads(messages[1]["content"]) == {
        "brief": asdict(BRIEF),
        "research": before,
    }
    assert research.model_dump(mode="json") == before
    assert "1토큰 초과" in caplog.text
    llm.assert_not_called()
