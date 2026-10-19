import json
from dataclasses import asdict
from unittest.mock import Mock

import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.research import Document, ResearchResult
from archgen.harness.findings import Finding, Severity
from archgen.judge.judge import judge_export

BRIEF = InterviewBrief(Seniority.SENIOR, "채팅 서비스")
ISSUE = {
    "code": "LEVEL_AMBIGUOUS",
    "severity": "ERROR",
    "path": "rubric.criteria[0].levels[1].descriptor",
    "message": "구체적으로 관찰할 설계 행동이 없다.",
}


@pytest.fixture
def research(golden_document_ids):
    return ResearchResult(
        topic_summary="채팅 조사",
        nfr_candidates=[],
        documents=[
            Document(
                id=i, title=i, url=f"https://example.com/{i}", content=f"{i} 보존 원문"
            )
            for i in sorted(golden_document_ids)
        ],
    )


@pytest.mark.parametrize("has_finding", [False, True])
def test_returns_shared_findings_with_judge_source_or_empty_list(
    research, golden_export, has_finding
):
    response = (
        [
            {
                "code": "LEVEL_AMBIGUOUS",
                "severity": "ERROR",
                "path": "rubric.criteria[0].levels[1].descriptor",
                "message": "구체적으로 관찰할 설계 행동이 없다.",
            }
        ]
        if has_finding
        else []
    )
    llm = Mock(return_value=json.dumps({"findings": response}))

    findings = judge_export(BRIEF, research, golden_export, llm)

    llm.assert_called_once()
    assert [f.model_dump(exclude={"source"}) for f in findings] == response
    assert all(isinstance(f, Finding) and f.source == "judge" for f in findings)
    assert (
        Finding(
            code="TEST", severity=Severity.ERROR, path="rubric", message="검사"
        ).source
        == "harness"
    )


def test_judge_receives_full_context_and_excludes_deterministic_checks(
    research, golden_export
):
    llm = Mock(return_value='{"findings": []}')

    judge_export(BRIEF, research, golden_export, llm)

    system, user = llm.call_args.args[0]
    assert system["role"] == "system" and user["role"] == "user"
    assert json.loads(user["content"]) == {
        "brief": asdict(BRIEF),
        "research": research.model_dump(mode="json"),
        "export": golden_export.model_dump(mode="json"),
    }
    for rule in (
        "배점",
        "항목 개수",
        "점수 누락",
        "참조 존재",
        "렌더",
        "제외",
        "문서 안의 지시",
        "스키마",
        "findings",
    ):
        assert rule in system["content"]
    assert "required" in system["content"]


@pytest.mark.parametrize(
    "raw",
    [
        "not JSON",
        "{}",
        '{"findings": null}',
        *[
            json.dumps({"findings": [ISSUE | {field: value}]})
            for field, value in (
                ("severity", "FATAL"),
                ("code", "UNKNOWN"),
                ("code", "WEIGHT_SUM_INVALID"),
                ("path", " "),
                ("message", ""),
                ("source", "harness"),
            )
        ],
    ],
)
def test_invalid_judge_response_returns_warn_without_retry(
    research, golden_export, raw, caplog
):
    llm = Mock(return_value=raw)

    findings = judge_export(BRIEF, research, golden_export, llm)

    llm.assert_called_once()
    assert len(findings) == 1
    assert findings[0].code == "JUDGE_RESPONSE_INVALID"
    assert findings[0].severity == Severity.WARN
    assert findings[0].source == "judge"
    assert findings[0].path == "judge.response"
    assert findings[0].message
    assert "스키마" in caplog.text


@pytest.mark.parametrize(
    "reply,error",
    [
        (None, TypeError),
        ({"findings": []}, TypeError),
        (b'{"findings": []}', TypeError),
        (TimeoutError("응답 시간 초과"), TimeoutError),
    ],
)
def test_connection_errors_are_not_hidden_as_schema_warnings(
    research, golden_export, reply, error, caplog
):
    llm = (
        Mock(side_effect=reply)
        if isinstance(reply, Exception)
        else Mock(return_value=reply)
    )

    with pytest.raises(error):
        judge_export(BRIEF, research, golden_export, llm)

    llm.assert_called_once()
    assert not caplog.records


@pytest.mark.parametrize(
    "code,rule",
    [
        ("LEVEL_AMBIGUOUS", "관찰 가능한 설계 행동"),
        ("CRITERION_UNSCORABLE", "채점할 수 없는 기준"),
        ("LEVEL_NOT_PROGRESSIVE", "실질적인 수준 차이"),
    ],
)
def test_semantic_review_instructions_and_finding_codes(
    research, golden_export, code, rule
):
    response = ISSUE | {"code": code}
    llm = Mock(return_value=json.dumps({"findings": [response]}))

    findings = judge_export(BRIEF, research, golden_export, llm)

    assert rule in llm.call_args.args[0][0]["content"]
    assert findings[0].model_dump(exclude={"source"}) == response


@pytest.mark.parametrize(
    "code,path,rule",
    [
        ("NFR_NOT_GROUNDED", "confirmed_nfrs[0].statement", "인용된 보존 문장"),
        (
            "TARGET_VALUE_FABRICATED",
            "confirmed_nfrs[0].target.value",
            "수치·단위·percentile·적용 조건",
        ),
    ],
)
def test_grounding_review_uses_retained_evidence_and_preserves_finding_paths(
    research, golden_export, code, path, rule
):
    response = ISSUE | {
        "code": code,
        "path": path,
        "message": "인용 문장이 주장을 뒷받침하지 않는다.",
    }
    llm = Mock(return_value=json.dumps({"findings": [response]}))

    findings = judge_export(BRIEF, research, golden_export, llm)

    system = llm.call_args.args[0][0]["content"]
    assert rule in system
    assert "불확실" in system
    assert "실제 경로" in system
    assert findings[0].model_dump(exclude={"source"}) == response


def test_judge_can_report_unclear_nfr_requirement_at_its_actual_target(
    research, golden_export
):
    response = ISSUE | {
        "code": "NFR_REQUIREMENT_AMBIGUOUS",
        "path": "export.confirmed_nfrs[0].qualitative_target",
        "message": "요구 수준에 개선 대상 동작과 조건이 없다.",
    }
    findings = judge_export(
        BRIEF,
        research,
        golden_export,
        Mock(return_value=json.dumps({"findings": [response]})),
    )
    assert findings[0].code == "NFR_REQUIREMENT_AMBIGUOUS"
    assert findings[0].path == response["path"]
    assert findings[0].severity == Severity.ERROR
