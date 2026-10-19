import json
from unittest.mock import Mock

import pytest


def case(tmp_path):
    def document(nfr, criterion, text):
        return (
            "# 채팅\n\n**설계 범위**\n메시지 전송\n\n"
            "**대상 연차** Middle\n\n"
            f"## {nfr}. 지연\n목표: 전송 대기를 줄인다.\n"
            f"### {criterion}. 전송\n{text}\n"
        )

    gold = tmp_path / "gold.md"
    candidate = tmp_path / "candidate.md"
    gold.write_text(document("NFR-1", "C1", "큐를 나눠 대기를 줄인다."))
    candidate.write_text(document("NFR-9", "C7", "분산 처리로 대기를 줄인다."))
    rows = []
    for rule, target, mapped in [
        ("1-1", "NFR-1", "NFR-9"),
        ("2-1", "C1", "C7"),
    ]:
        rows.append(
            {
                "rubric": str(candidate),
                "criterion_id": rule,
                "target_id": target,
                "verdict": "Pass",
                "applied_rule": "동등한 설계 역량을 평가한다.",
                "reason": "이름은 다르지만 대기를 줄이는 역량을 요구한다.",
                "matched_ids": [mapped],
                "golden_quotes": [
                    "전송 대기를 줄인다." if rule == "1-1" else "큐를 나눠 대기를 줄인다."
                ],
                "generated_quotes": [
                    "전송 대기를 줄인다."
                    if rule == "1-1"
                    else "분산 처리로 대기를 줄인다."
                ],
                "null_reason": None,
            }
        )
    return (
        candidate,
        gold,
        {
            "input_compatible": True,
            "compatibility_reason": "같은 주제와 범위다.",
            "results": rows,
        },
    )


def test_golden_comparison_keeps_semantic_mapping_despite_different_ids(tmp_path):
    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, response = case(tmp_path)
    llm = Mock(return_value=json.dumps(response))
    result = evaluate_golden(candidate, gold, llm)
    assert result.summary["by_criterion"]["1-1"]["percentage"] == 100
    assert result.results[1].matched_ids == ["C7"]
    assert result.summary["unmapped_criteria"] == 0
    assert "타당한 다른 해결 방법" in llm.call_args.args[0][0]["content"]


@pytest.mark.parametrize(
    "defect",
    [
        "unknown_id",
        "invented_quote",
        "wrong_path",
        "null_reason",
        "pass_no_mapping",
        "removed_level_rule",
        "duplicate",
        "missing",
    ],
)
def test_rejects_invalid_comparison_evidence_and_result_coverage(tmp_path, defect):
    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, response = case(tmp_path)
    row = response["results"][1]
    if defect == "unknown_id":
        row["matched_ids"] = ["C999"]
    elif defect == "invented_quote":
        row["generated_quotes"] = ["문서에 없는 원자적 보장이다."]
    elif defect == "wrong_path":
        row["rubric"] = "other.md"
    elif defect == "null_reason":
        row["null_reason"] = "insufficient_data"
    elif defect == "pass_no_mapping":
        row["matched_ids"] = []
    elif defect == "removed_level_rule":
        response["results"].append({**row, "criterion_id": "3-1"})
    elif defect == "duplicate":
        response["results"].append(row.copy())
    else:
        response["results"].pop()
    with pytest.raises(ValueError):
        evaluate_golden(candidate, gold, Mock(return_value=json.dumps(response)))


def test_missing_competency_fails_and_keeps_unknown_separate(tmp_path):
    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, response = case(tmp_path)
    response["results"][0].update(verdict=None, null_reason="insufficient_data")
    response["results"][1].update(verdict="Fail", matched_ids=[], generated_quotes=[])
    result = evaluate_golden(candidate, gold, Mock(return_value=json.dumps(response)))
    assert result.summary["by_criterion"]["2-1"]["percentage"] == 0
    assert "3-1" not in result.summary["by_criterion"]
    assert result.summary["unmapped_criteria"] == 1
    assert result.summary["null_reasons"] == {"insufficient_data": 1}


@pytest.mark.parametrize("mismatch", ["tier", "scope"])
def test_incompatible_inputs_never_return_comparison_scores(tmp_path, mismatch):
    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, response = case(tmp_path)
    if mismatch == "tier":
        candidate.write_text(candidate.read_text().replace("Middle", "Senior"))
    else:
        response.update(
            input_compatible=False, compatibility_reason="서로 다른 처리 범위다."
        )
    llm = Mock(return_value=json.dumps(response))
    with pytest.raises(ValueError, match="연차|범위 불일치"):
        evaluate_golden(candidate, gold, llm)
    if mismatch == "tier":
        llm.assert_not_called()


def test_manual_comparison_returns_separate_quality_and_golden_groups(
    tmp_path, monkeypatch
):
    from archgen import golden_evaluation as module

    candidate, gold, _ = case(tmp_path)
    calls = []

    def run(paths, criteria_path=None, **kwargs):
        calls.append((paths, kwargs))
        return {
            "trace_id": kwargs.get("source"),
            "evaluation": {"summary": {"overall": {"percentage": 90}}},
        }

    monkeypatch.setattr(module, "run", run)
    result = module.run_comparison(
        candidate,
        gold,
        model=Mock(model_name="gold-judge"),
        quality_model=Mock(model_name="quality-judge"),
        client=Mock(),
    )
    assert set(result) == {"quality", "golden_comparison"}
    assert calls[0][1]["score_group"] == "golden"
    assert calls[1][1]["source"] == "generation"
    assert result["golden_comparison"]["trace_id"] != result["quality"]["trace_id"]


def test_unknown_mapping_does_not_count_as_confirmed_missing_competency(tmp_path):
    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, response = case(tmp_path)
    for row in response["results"][1:]:
        row.update(
            verdict=None,
            null_reason="insufficient_data",
            matched_ids=[],
            generated_quotes=[],
        )
    result = evaluate_golden(candidate, gold, Mock(return_value=json.dumps(response)))
    assert result.summary["unmapped_criteria"] == 0
    assert result.summary["null_reasons"]["insufficient_data"] == 1


@pytest.mark.parametrize("with_golden", [False, True])
def test_cli_preserves_existing_quality_mode_and_adds_explicit_golden_mode(
    monkeypatch, capsys, with_golden
):
    import sys

    from archgen import evaluation, golden_evaluation

    quality = Mock(return_value={"quality_only": True})
    compare = Mock(return_value={"quality": {}, "golden_comparison": {}})
    monkeypatch.setattr(evaluation, "run", quality)
    monkeypatch.setattr(golden_evaluation, "run_comparison", compare)
    argv = ["evaluate_rubric.py", "generated.md"]
    if with_golden:
        argv += ["--golden", "reference.md"]
    monkeypatch.setattr(sys, "argv", argv)
    evaluation.main()
    output = json.loads(capsys.readouterr().out)
    if with_golden:
        quality.assert_not_called()
        compare.assert_called_once()
        assert set(output) == {"quality", "golden_comparison"}
    else:
        compare.assert_not_called()
        quality.assert_called_once()
        assert output == {"quality_only": True}


def test_golden_language_retry_preserves_reference_mapping(tmp_path):
    from copy import deepcopy

    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, clean = case(tmp_path)
    bad = deepcopy(clean)
    bad["results"][0]["reason"] = "消息"
    llm = Mock(side_effect=[json.dumps(bad), json.dumps(clean)])
    result = evaluate_golden(candidate, gold, llm)
    assert llm.call_count == 2
    assert result.results[0].matched_ids == ["NFR-9"]


def test_langfuse_golden_percentage_is_separate_from_quality_score_names(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    from archgen.evaluation import run
    from archgen.golden_evaluation import CRITERIA, evaluate_golden

    candidate, gold, response = case(tmp_path)
    model = Mock(model_name="test-model", reasoning_effort="high")
    model.invoke.return_value = SimpleNamespace(content=json.dumps(response))
    client = MagicMock()
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "golden-trace", "golden-span"
    client.api.scores.create.return_value = SimpleNamespace(rejected=0)
    run(
        [candidate, gold],
        CRITERIA,
        model=model,
        client=client,
        source="golden-comparison",
        score_group="golden",
        evaluate_fn=lambda paths, criteria, llm: evaluate_golden(paths[0], paths[1], llm),
    )
    scores = client.api.scores.create.call_args.kwargs["request"]
    names = [score.name for score in scores]
    assert "golden::overall::percentage" in names
    assert not any(name.startswith("quality::") for name in names)


def test_comparison_evaluates_only_nfr_and_competency_without_level_equivalence(tmp_path):
    from archgen.golden_evaluation import evaluate_golden

    candidate, gold, response = case(tmp_path)
    response["results"] = response["results"][:2]
    for row in response["results"]:
        row.pop("differing_levels", None)
    result = evaluate_golden(candidate, gold, Mock(return_value=json.dumps(response)))
    assert set(result.summary["by_criterion"]) == {"1-1", "2-1"}
    assert all("differing_levels" not in row.model_dump() for row in result.results)
