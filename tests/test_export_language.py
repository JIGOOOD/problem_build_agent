import json
from unittest.mock import Mock

import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.domain.nfr import NFRSelection
from archgen.domain.research import Document, ResearchResult
from archgen.export.agent import generate_rubric, select_nfrs
from archgen.export.language import check_language
from archgen.paths import CATALOG_DIR


def test_selection_retries_chinese_body_and_returns_corrected_response():
    research = ResearchResult(
        topic_summary="채팅",
        nfr_candidates=[],
        documents=[
            Document(id="D1", url="https://example.com", title="자료", content="消息")
        ],
    )
    answer = {"confirmed_nfrs": [], "tradeoffs": [], "scope": ["消息应及时送达"]}
    corrected = {**answer, "scope": ["메시지를 전달한다."]}
    llm = Mock(side_effect=[json.dumps(answer), json.dumps(corrected)])

    result = select_nfrs(
        InterviewBrief(Seniority.MIDDLE, "채팅"),
        research,
        llm,
        catalog=load_catalog(CATALOG_DIR),
        count_tokens=lambda _: 1000,
    )

    assert llm.call_count == 2
    assert result.selection.scope == corrected["scope"]
    feedback = llm.call_args.args[0][-1]["content"]
    assert "scope[0]" in feedback
    assert "한국어" in feedback


@pytest.mark.parametrize(
    ("text", "rejected"),
    [
        ("single point of failure", False),
        ("The system must deliver messages", True),
        ("The\nsystem must deliver messages", True),
        ("at-least-once 전달과 message queue 및 p99 ≤ 200ms", False),
    ],
)
def test_english_runs_of_five_words_are_rejected(text, rejected):
    assert bool(check_language({"description": text})) is rejected


@pytest.mark.parametrize("stage", ["selection", "rubric"])
def test_language_retry_limit_is_two_and_never_returns_invalid_output(
    stage, golden_export
):
    research = ResearchResult(
        topic_summary="채팅",
        nfr_candidates=[],
        documents=[
            Document(id="D1", url="https://example.com", title="자료", content="근거")
        ],
    )
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    answer = (
        selection.model_dump()
        if stage == "selection"
        else golden_export.rubric.model_dump()
    )
    if stage == "selection":
        answer["confirmed_nfrs"][0]["statement"] = "消息"
    else:
        answer["criteria"][0]["levels"][0]["descriptor"] = (
            "The system must deliver messages"
        )
    llm = Mock(return_value=json.dumps(answer))
    counter = Mock(return_value=1000)
    brief = InterviewBrief(Seniority.MIDDLE, "채팅")

    with pytest.raises(ValueError, match="언어 검증 실패.*2회"):
        if stage == "selection":
            select_nfrs(
                brief,
                research,
                llm,
                catalog=load_catalog(CATALOG_DIR),
                count_tokens=counter,
            )
        else:
            generate_rubric(brief, research, selection, llm, count_tokens=counter)

    assert llm.call_count == counter.call_count == 3
    assert "5단어" in llm.call_args.args[0][0]["content"]


@pytest.mark.parametrize("stage", ["selection", "rubric"])
def test_last_language_retry_can_succeed(stage, golden_export):
    research = ResearchResult(
        topic_summary="채팅",
        nfr_candidates=[],
        documents=[
            Document(id="D1", url="https://example.com", title="자료", content="근거")
        ],
    )
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    clean = (
        selection.model_dump_json()
        if stage == "selection"
        else golden_export.rubric.model_dump_json()
    )
    bad = json.loads(clean)
    if stage == "selection":
        bad["tradeoffs"][0]["description"] = "消息"
    else:
        bad["criteria"][0]["title"] = "消息"
    llm = Mock(side_effect=[json.dumps(bad), json.dumps(bad), clean])
    brief = InterviewBrief(Seniority.MIDDLE, "채팅")

    if stage == "selection":
        result = select_nfrs(
            brief,
            research,
            llm,
            catalog=load_catalog(CATALOG_DIR),
            count_tokens=lambda _: 1000,
        )
        assert result.selection == selection
    else:
        result = generate_rubric(
            brief, research, selection, llm, count_tokens=lambda _: 1000
        )
        assert result == golden_export
    assert llm.call_count == 3


@pytest.mark.parametrize("text", ["消息", "メッセージ", "сообщение", "رسالة", "a\u0301"])
def test_other_language_letters_and_marks_are_rejected(text):
    assert check_language({"description": text})


def test_language_checks_ignore_identifiers_but_cover_nested_body_fields():
    assert (
        check_language(
            {
                "id": "中文",
                "related_nfr_ids": ["中文"],
                "evidence_refs": ["中文"],
                "target": {"value": 200, "unit": "ms", "condition": "피크 부하"},
                "statement": "메시지 큐(message queue)를 이용한다.",
            }
        )
        == []
    )
    assert check_language({"target": {"condition": "消息"}})[0].startswith(
        "target.condition:"
    )
