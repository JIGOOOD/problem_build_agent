import json
from pathlib import Path
from unittest.mock import Mock

import pytest

import evaluate_rubric as evaluator


def test_judge_retries_chinese_and_five_english_words_before_returning_korean(tmp_path):
    rubric = tmp_path / "this filename has five english words 中文.md"
    rubric.write_text(
        "# 채팅\n## NFR-1. Low Latency\n### C1. 메시지 전송 · 100\n",
        encoding="utf-8",
    )
    criteria = tmp_path / "criteria.md"
    criteria.write_text("### 3-1. NFR과 Criterion의 연관성\n", encoding="utf-8")
    clean = {
        "rubric": str(rubric),
        "criterion_id": "3-1",
        "target_id": "C1",
        "verdict": "Pass",
        "applied_rule": "메시지 전송 지연을 평가한다.",
        "reason": "전송 지연을 줄이는 처리 흐름을 평가하므로 요구 수준과 연결된다.",
    }
    chinese = {**clean, "applied_rule": "消息应及时送达"}
    english = {**clean, "reason": "The system must deliver messages"}
    llm = Mock(
        side_effect=[json.dumps({"results": [row]}) for row in [chinese, english, clean]]
    )

    result = evaluator.evaluate([rubric], criteria, llm)

    assert llm.call_count == 3
    assert result.results[0].reason == clean["reason"]
    assert result.results[0].applied_rule == clean["applied_rule"]
    first_retry = llm.call_args_list[1].args[0][-1]["content"]
    last_retry = llm.call_args_list[2].args[0][-1]["content"]
    assert "applied_rule" in first_retry and "한국어" in first_retry
    assert "reason" in last_retry and "5단어" in last_retry


def test_persistent_foreign_language_never_creates_langfuse_scores(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    def respond(messages):
        keys = json.loads(
            next(
                line
                for line in messages[0]["content"].splitlines()
                if line.startswith("[[")
            )
        )
        return SimpleNamespace(
            content=json.dumps(
                {
                    "results": [
                        {
                            "rubric": path,
                            "criterion_id": rule,
                            "target_id": target,
                            "verdict": "Pass",
                            "applied_rule": "적용 기준",
                            "reason": "消息",
                        }
                        for path, rule, target in keys
                    ]
                }
            )
        )

    model = Mock(model_name="test-judge")
    model.invoke.side_effect = respond
    client = MagicMock()
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "trace-language", "span-language"

    with pytest.raises(RuntimeError, match="언어 검증 실패.*2회"):
        evaluator.run(
            [Path("resources/golden/uber_middle.md")],
            model=model,
            client=client,
            failure_root=tmp_path,
        )

    assert model.invoke.call_count == 3
    client.api.scores.create.assert_not_called()
    assert span.update.call_args.kwargs["level"] == "ERROR"
    assert "消息" not in span.update.call_args.kwargs["output"]["evaluation_error"]
    assert not list(tmp_path.iterdir())


def test_reports_percentages_by_rule_and_rubric_excluding_unscorable_results():
    result = evaluator.Evaluation(
        results=[
            evaluator.Assessment(
                rubric=rubric,
                criterion_id=rule,
                target_id="rubric",
                verdict=verdict,
                applied_rule="적용 기준",
                reason="판단 근거",
            )
            for rubric, rule, verdict in [
                ("middle.md", "1-1", "Pass"),
                ("senior.md", "1-1", "Fail"),
                ("middle.md", "3-4", "Pass"),
                ("middle.md", "3-4", None),
                ("senior.md", "3-4", "Pass"),
                ("comparison", "4-1", "Pass"),
            ]
        ]
    )

    summary = result.summary

    assert summary["overall"] == {
        "passed": 4,
        "failed": 1,
        "unscorable": 1,
        "percentage": 80.0,
    }
    assert summary["by_criterion"]["1-1"]["percentage"] == 50.0
    assert summary["by_criterion"]["3-4"]["percentage"] == 100.0
    assert summary["by_rubric"]["middle.md"]["percentage"] == 100.0
    assert summary["by_rubric"]["senior.md"]["percentage"] == 50.0
    assert summary["by_rubric"]["comparison"]["percentage"] == 100.0
    assert [r.percentage for r in result.results] == [
        100.0,
        0.0,
        100.0,
        None,
        100.0,
        100.0,
    ]
    unknown = evaluator.Evaluation(results=[result.results[3]])
    assert unknown.summary["overall"]["percentage"] is None


def test_evaluates_md_with_pass_fail_and_unscorable_without_a_score(tmp_path):
    rubric = tmp_path / "middle.md"
    rubric.write_text(
        "# 채팅\n\n**설계 범위**\n메시지 전송\n\n"
        "**평가 초점**\n전송 지연\n\n**대상 연차** Middle\\\n"
        "## NFR-1. Low Latency\n### C1. 메시지 전송 · 100\n내용\n",
        encoding="utf-8",
    )
    criteria = tmp_path / "criteria.md"
    criteria.write_text(
        "### 1-1. 범위\n### 1-2. 누락\n### 2-1. NFR\n### 3-1. 항목\n### 4-1. 연차 비교\n",
        encoding="utf-8",
    )
    items = [
        ("1-1", "rubric", "Pass"),
        ("1-2", "rubric", None),
        ("2-1", "NFR-1", "Fail"),
        ("3-1", "C1", "Pass"),
    ]
    llm = Mock(
        return_value=json.dumps(
            {
                "results": [
                    {
                        "rubric": str(rubric),
                        "criterion_id": cid,
                        "target_id": target,
                        "verdict": verdict,
                        "applied_rule": "제공한 기준",
                        "reason": "구체적인 판단 이유",
                    }
                    for cid, target, verdict in items
                ]
            }
        )
    )

    result = evaluator.evaluate([rubric], criteria, llm)

    assert [r.score for r in result.results] == [1, None, 0, 1]
    messages = llm.call_args.args[0]
    assert rubric.read_text(encoding="utf-8") in messages[1]["content"]
    assert criteria.read_text(encoding="utf-8") in messages[0]["content"]
    assert "판단 불가" in messages[0]["content"]
    assert "Middle" in messages[0]["content"]


def test_rejects_a_judge_response_that_silently_omits_required_assessments():
    llm = Mock(return_value='{"results": []}')

    with pytest.raises(ValueError, match="누락|불일치"):
        evaluator.evaluate(
            [Path("resources/golden/uber_middle.md")],
            Path("docs/evaluator/rubric.md"),
            llm,
        )


def test_compares_matching_middle_senior_and_rejects_different_scope(tmp_path):
    paths = [
        Path("resources/golden/uber_middle.md"),
        Path("resources/golden/uber_senior.md"),
    ]

    def llm(messages):
        keys = json.loads(
            next(
                line
                for line in messages[0]["content"].splitlines()
                if line.startswith("[[")
            )
        )
        assert len(keys) == 81
        assert keys[-1] == ["comparison", "4-1", "pair"]
        return json.dumps(
            {
                "results": [
                    {
                        "rubric": path,
                        "criterion_id": cid,
                        "target_id": target,
                        "verdict": "Pass",
                        "applied_rule": "기준",
                        "reason": "근거",
                    }
                    for path, cid, target in keys
                ]
            }
        )

    result = evaluator.evaluate(paths, Path("docs/evaluator/rubric.md"), llm)
    assert len(result.results) == 81
    other = tmp_path / "senior.md"
    other.write_text(
        paths[1].read_text(encoding="utf-8").replace("# Uber 차량 매칭", "# 채팅"),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="동일|비교"):
        evaluator.evaluate([paths[0], other], Path("docs/evaluator/rubric.md"), Mock())


@pytest.mark.parametrize("response", ["not json", TimeoutError("judge timeout")])
def test_invalid_json_or_call_failure_is_an_evaluation_error(response):
    llm = (
        Mock(side_effect=response)
        if isinstance(response, Exception)
        else Mock(return_value=response)
    )
    with pytest.raises((ValueError, TimeoutError)):
        evaluator.evaluate(
            [Path("resources/golden/uber_middle.md")],
            Path("docs/evaluator/rubric.md"),
            llm,
        )


def test_records_only_scored_assessments_and_keeps_unscorable_reason(
    tmp_path, monkeypatch
):
    from unittest.mock import MagicMock

    result = evaluator.Evaluation(
        results=[
            evaluator.Assessment(
                rubric="middle.md",
                criterion_id=cid,
                target_id="rubric",
                verdict=verdict,
                applied_rule="적용 기준",
                reason="판단 이유",
            )
            for cid, verdict in [("1-1", "Pass"), ("1-2", None), ("1-3", "Fail")]
        ]
    )
    monkeypatch.setattr(evaluator, "evaluate", Mock(return_value=result))
    client = MagicMock()
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "trace-123", "span-123"
    client.api.scores.create.return_value.rejected = 0
    model = Mock(model_name="test-judge")

    output = evaluator.run(
        [Path("resources/golden/uber_middle.md")],
        model=model,
        client=client,
        failure_root=tmp_path,
    )

    assert output["trace_id"] == "trace-123"
    scores = client.api.scores.create.call_args.kwargs["request"]
    assert [(s.name, s.value) for s in scores if s.data_type == "BOOLEAN"] == [
        ("middle.md::1-1::rubric", 1.0),
        ("middle.md::1-3::rubric", 0.0),
    ]
    assert {s.name: s.value for s in scores if s.data_type == "NUMERIC"} == {
        "quality::overall::percentage": 50.0,
        "quality::criterion::1-1::percentage": 100.0,
        "quality::criterion::1-3::percentage": 0.0,
        "quality::rubric::middle.md::percentage": 50.0,
    }
    assert all(s.trace_id == "trace-123" and s.comment for s in scores)
    span.update.assert_called_once_with(output=result.model_dump(mode="json"))
    client.flush.assert_called_once()
    assert not list(tmp_path.iterdir())


def test_missing_input_is_logged_as_evaluation_error_without_a_score(tmp_path):
    from unittest.mock import MagicMock

    client = MagicMock()
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "trace-missing", "span-missing"
    with pytest.raises(RuntimeError, match="평가 오류"):
        evaluator.run(
            [tmp_path / "missing.md"],
            model=Mock(model_name="test-judge"),
            client=client,
            failure_root=tmp_path / "failed",
        )
    assert span.update.call_args.kwargs["level"] == "ERROR"
    client.api.scores.create.assert_not_called()
    assert not (tmp_path / "failed").exists()


def test_langfuse_transfer_failure_keeps_result_for_manual_recovery(
    tmp_path, monkeypatch
):
    from unittest.mock import MagicMock

    result = evaluator.Evaluation(
        results=[
            evaluator.Assessment(
                rubric="middle.md",
                criterion_id="1-1",
                target_id="rubric",
                verdict="Pass",
                applied_rule="적용 기준",
                reason="판단 근거",
            )
        ]
    )
    monkeypatch.setattr(evaluator, "evaluate", Mock(return_value=result))
    client = MagicMock()
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "trace-transfer", "span-transfer"
    client.flush.side_effect = RuntimeError("network unavailable")

    with pytest.raises(RuntimeError, match="Langfuse 기록 실패"):
        evaluator.run(
            [Path("resources/golden/uber_middle.md")],
            model=Mock(model_name="test-judge"),
            client=client,
            failure_root=tmp_path,
        )

    saved = json.loads((tmp_path / "trace-transfer.json").read_text(encoding="utf-8"))
    assert saved["result"] == result.model_dump(mode="json")
    assert saved["delivery_error"] == "network unavailable"
    assert "input" not in saved


def test_trace_export_uses_the_same_v4_ingestion_as_the_score_api(monkeypatch):
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    for key, value in {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-test",
        "LANGFUSE_SECRET_KEY": "sk-lf-test",
        "LANGFUSE_BASE_URL": "https://example.test",
    }.items():
        monkeypatch.setenv(key, value)
    constructor = Mock(return_value=None)
    monkeypatch.setattr(OTLPSpanExporter, "__init__", constructor)
    monkeypatch.setattr("langfuse.Langfuse", Mock())

    evaluator._connect_langfuse()

    assert constructor.call_args.kwargs["headers"]["x-langfuse-ingestion-version"] == "4"
