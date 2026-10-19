import json
from dataclasses import asdict
from unittest.mock import Mock

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.research import Document, ResearchResult


def make_archive(path, export):
    path.mkdir()
    brief = InterviewBrief(Seniority.SENIOR, "채팅")
    values = {
        "input.json": asdict(brief),
        "research.json": ResearchResult(
            topic_summary="채팅",
            nfr_candidates=[],
            documents=[
                Document(
                    id=ref,
                    url="https://example.org",
                    title="설계 근거",
                    content="확인한 설계 근거",
                )
                for ref in sorted(
                    {ref for n in export.confirmed_nfrs for ref in n.evidence_refs}
                    | {ref for t in export.tradeoffs for ref in t.evidence_refs}
                )
            ],
        ).model_dump(mode="json"),
        "selection.json": {
            "status": "selected",
            "selection": export.model_dump(mode="json", exclude={"rubric"}),
            "reason": None,
        },
        "nfr_export-0.json": export.model_dump(mode="json"),
    }
    for name, value in values.items():
        (path / name).write_text(json.dumps(value, ensure_ascii=False))


def test_conditions_start_from_same_export_and_only_error_feedback_repairs(
    tmp_path, golden_export
):
    from archgen.validation_comparison import compare_run

    raw = golden_export.model_dump(mode="json")
    raw["rubric"]["criteria"][0]["weight"] += 1
    broken = golden_export.model_validate(raw)
    archive = tmp_path / "archive"
    make_archive(archive, broken)
    original = {p.name: p.read_bytes() for p in archive.iterdir()}
    judge = Mock(return_value='{"findings":[]}')
    repair = Mock(return_value=golden_export.rubric.model_dump_json())
    assess = Mock(return_value={"trace_id": "evaluation", "evaluation": {"results": []}})
    result = compare_run(
        archive,
        tmp_path / "comparison",
        judge_llm=judge,
        repair_llm=repair,
        count_tokens=lambda _: 100,
        evaluate_result=assess,
    )
    rows = result["conditions"]
    assert [rows[c]["repairs"] for c in "ABCDE"] == [0, 0, 1, 0, 1]
    assert [rows[c]["judge_calls"] for c in "ABCDE"] == [0, 1, 0, 1, 2]
    assert (tmp_path / "comparison/A/nfr_export-0.json").read_bytes() == (
        tmp_path / "comparison/B/nfr_export-0.json"
    ).read_bytes()
    assert all(rows[c]["initial_sha256"] == rows["A"]["initial_sha256"] for c in "ABCDE")
    assert rows["B"]["precision"] is None and rows["B"]["recall"] is None
    assert all(p.read_bytes() == original[p.name] for p in archive.iterdir())
    assert assess.call_count == 2  # 동일 결과는 독립 평가를 재사용한다.


def test_precision_recall_requires_review_and_deduplicates_one_error():
    from archgen.validation_comparison import human_detection_metrics

    findings = [
        {"source": "judge", "code": "LEVEL_AMBIGUOUS", "path": "rubric.criteria[0]"},
        {"source": "judge", "code": "LEVEL_AMBIGUOUS", "path": "rubric.criteria[0]"},
        {"source": "harness", "code": "WEIGHT_SUM_INVALID", "path": "rubric.criteria"},
    ]
    assert human_detection_metrics(findings, None)["precision"] is None
    review = {
        "review_status": "confirmed",
        "reviewed_by": "사용자",
        "errors": [
            {"id": "ambiguous", "present": True, "matches": [findings[0]]},
            {"id": "false-positive", "present": False, "matches": [findings[-1]]},
            {
                "id": "missed",
                "present": True,
                "matches": [
                    {
                        "source": "judge",
                        "code": "NFR_NOT_GROUNDED",
                        "path": "confirmed_nfrs[0]",
                    }
                ],
            },
        ],
    }
    result = human_detection_metrics(findings, review)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 1, 1)
    assert result["precision"] == result["recall"] == 50
    review["review_status"] = "provisional"
    assert human_detection_metrics(findings, review)["recall"] is None


def test_comparison_attaches_human_metrics_and_emits_readable_table(
    tmp_path, golden_export
):
    from archgen.validation_comparison import compare_run

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)
    result = compare_run(
        archive,
        tmp_path / "comparison",
        conditions="B",
        judge_llm=lambda _: '{"findings":[]}',
        repair_llm=None,
        count_tokens=lambda _: 100,
        evaluate_result=lambda _: {"evaluation": {"results": []}},
        review={
            "B": {"review_status": "confirmed", "reviewed_by": "사용자", "errors": []}
        },
    )
    assert result["conditions"]["B"]["detection"]["reviewed_by"] == "사용자"
    table = (tmp_path / "comparison/comparison.md").read_text()
    assert "| B |" in table and "N/A" in table
    manifest = json.loads((tmp_path / "comparison/manifest.json").read_text())
    assert manifest["prompt_sha256"]


def test_judge_invalid_response_is_failed_and_never_triggers_repair(
    tmp_path, golden_export
):
    from archgen.validation_comparison import compare_run

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)
    repair = Mock()
    result = compare_run(
        archive,
        tmp_path / "comparison",
        conditions="DE",
        judge_llm=lambda _: "{}",
        repair_llm=repair,
        count_tokens=lambda _: 100,
        evaluate_result=lambda _: {"evaluation": {"results": []}},
    )
    assert all(row["status"] == "judge_failed" for row in result["conditions"].values())
    assert all(row["judge_calls"] == 1 for row in result["conditions"].values())
    repair.assert_not_called()


def test_repeated_judge_errors_stop_after_two_actual_repairs(tmp_path, golden_export):
    from archgen.validation_comparison import compare_run

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)
    problem = json.dumps(
        {
            "findings": [
                {
                    "code": "LEVEL_AMBIGUOUS",
                    "severity": "ERROR",
                    "path": "rubric.criteria[0]",
                    "message": "설계 행동이 모호하다.",
                    "source": "judge",
                }
            ]
        }
    )
    result = compare_run(
        archive,
        tmp_path / "comparison",
        conditions="D",
        judge_llm=lambda _: problem,
        repair_llm=lambda _: golden_export.rubric.model_dump_json(),
        count_tokens=lambda _: 100,
        evaluate_result=lambda _: {"evaluation": {"results": []}},
    )
    row = result["conditions"]["D"]
    assert (row["repairs"], row["repair_calls"], row["judge_calls"]) == (2, 2, 3)
    assert row["status"] == "repair_limit"


def test_judge_required_conditions_refuse_disabled_judge(tmp_path, golden_export):
    import pytest

    from archgen.validation_comparison import compare_run

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)
    with pytest.raises(ValueError, match="Judge"):
        compare_run(
            archive,
            tmp_path / "out",
            conditions="B",
            judge_llm=None,
            repair_llm=None,
            count_tokens=lambda _: 100,
            evaluate_result=Mock(),
        )
    assert not (tmp_path / "out").exists()


def test_manual_comparison_cli_reports_the_requested_archive(
    tmp_path, monkeypatch, capsys
):
    from archgen import validation_comparison as comparison

    runner = Mock(return_value={"conditions": {}, "review_status": "provisional"})
    monkeypatch.setattr(comparison, "run_comparison", runner, raising=False)
    assert (
        comparison.main(
            ["archive", "--output", str(tmp_path / "out"), "--conditions", "AB"]
        )
        == 0
    )
    assert runner.call_args.args[0].name == "archive"
    assert runner.call_args.kwargs["conditions"] == "AB"
    assert "provisional" in capsys.readouterr().out


def test_known_error_cases_are_isolated_and_distinguished_from_natural_errors(
    tmp_path, golden_export
):
    from archgen.domain.nfr import NFRExport
    from archgen.harness.checks import check_levels, check_weight_sum
    from archgen.validation_comparison import make_known_error_cases

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)
    before = (archive / "nfr_export-0.json").read_bytes()
    cases = make_known_error_cases(archive, tmp_path / "injected")
    assert len(cases) == 3
    assert all(
        c["origin"] == "injected" and c["review_status"] == "synthetic_expected"
        for c in cases
    )
    weight = NFRExport.model_validate_json(
        (tmp_path / "injected/weight/nfr_export-0.json").read_text()
    )
    levels = NFRExport.model_validate_json(
        (tmp_path / "injected/level/nfr_export-0.json").read_text()
    )
    assert any(f.code == "WEIGHT_SUM_INVALID" for f in check_weight_sum(weight))
    assert any(f.code == "LEVEL_DUPLICATED" for f in check_levels(levels))
    assert before == (archive / "nfr_export-0.json").read_bytes()


def test_render_failure_is_separate_from_llm_repairs_and_fails_the_condition(
    tmp_path, golden_export, monkeypatch
):
    from archgen import validation_comparison as comparison

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)

    def broken_renderer(*_):
        raise RuntimeError("렌더러 오류")

    monkeypatch.setattr(comparison, "render_rubric", broken_renderer)
    repair, assess = Mock(), Mock()
    result = comparison.compare_run(
        archive,
        tmp_path / "comparison",
        conditions="C",
        judge_llm=None,
        repair_llm=repair,
        count_tokens=lambda _: 100,
        evaluate_result=assess,
    )
    row = result["conditions"]["C"]
    assert row["status"] == "render_failed" and row["render_errors"] == 1
    assert row["evaluation"] is None
    repair.assert_not_called()
    assess.assert_not_called()


def test_human_review_matches_the_same_path_with_optional_export_prefix():
    from archgen.validation_comparison import human_detection_metrics

    finding = {
        "source": "judge",
        "code": "LEVEL_AMBIGUOUS",
        "path": "export.rubric.criteria[0].levels[2].descriptor",
    }
    review = {
        "review_status": "confirmed",
        "reviewed_by": "검토자",
        "errors": [
            {
                "id": "ambiguous",
                "present": True,
                "matches": [
                    {**finding, "path": "rubric.criteria[0].levels[2].descriptor"}
                ],
            }
        ],
    }
    result = human_detection_metrics([finding], review)
    assert result["tp"] == 1 and result["recall"] == 100


def test_comparison_does_not_retry_immutable_selection_errors(tmp_path, golden_export):
    from archgen.validation_comparison import compare_run

    archive = tmp_path / "archive"
    make_archive(archive, golden_export)
    problem = json.dumps(
        {
            "findings": [
                {
                    "code": "NFR_NOT_GROUNDED",
                    "severity": "ERROR",
                    "path": "export.tradeoffs[0]",
                    "message": "선정한 요구의 상충 근거가 부족하다.",
                    "source": "judge",
                }
            ]
        }
    )
    repair = Mock()
    result = compare_run(
        archive,
        tmp_path / "comparison",
        conditions="DE",
        judge_llm=lambda _: problem,
        repair_llm=repair,
        count_tokens=lambda _: 100,
        evaluate_result=lambda _: {"evaluation": {"results": []}},
    )
    assert all(
        row["status"] == "requires_upstream_repair"
        for row in result["conditions"].values()
    )
    assert all(row["repairs"] == 0 for row in result["conditions"].values())
    repair.assert_not_called()
