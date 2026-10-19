"""같은 최초 생성본의 하네스·Judge 검사와 최대 두 번의 보완을 비교한다."""

import hashlib
import json
from pathlib import Path
from time import monotonic

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRExport, NFRSelection
from archgen.domain.research import ResearchResult
from archgen.export.agent import generate_rubric, rubric_repair_findings
from archgen.harness.checks import (
    check_criteria_count,
    check_cross_ref,
    check_levels,
    check_targets,
    check_weight_sum,
)
from archgen.harness.findings import FindingCode, Severity
from archgen.harness.runner import Runner
from archgen.judge.judge import judge_export
from archgen.paths import PROJECT_ROOT
from archgen.render.post_render import check_rendered
from archgen.render.renderer import render_rubric

CONDITIONS = {
    "A": (False, False, 0),
    "B": (True, True, 0),
    "C": (True, False, 2),
    "D": (False, True, 2),
    "E": (True, True, 2),
}


def _save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def _failed_checks(evaluation):
    if evaluation is None:
        return None
    return {
        (r["criterion_id"], r["target_id"])
        for r in evaluation["evaluation"]["results"]
        if r["verdict"] == "Fail"
    }


def provisional_changes(before, after):
    old, new = _failed_checks(before), _failed_checks(after)
    if old is None or new is None:
        return None
    old_rows = {
        (r["criterion_id"], r["target_id"]): r["verdict"]
        for r in before["evaluation"]["results"]
    }
    new_rows = {
        (r["criterion_id"], r["target_id"]): r["verdict"]
        for r in after["evaluation"]["results"]
    }
    comparable = {
        k
        for k in old_rows.keys() & new_rows.keys()
        if old_rows[k] is not None and new_rows[k] is not None
    }
    return {
        "resolved": len((old - new) & comparable),
        "residual": len(old & new & comparable),
        "new": len((new - old) & comparable),
        "unmatched_or_unscorable": len(old_rows.keys() | new_rows.keys())
        - len(comparable),
        "review_status": "provisional",
        "unit": "평가 기준·대상 조합이며 동일 원인의 오류 수가 아니다.",
    }


def compare_run(
    directory,
    output_dir,
    *,
    judge_llm,
    repair_llm,
    count_tokens,
    evaluate_result,
    conditions="ABCDE",
    review=None,
    model_settings=None,
):
    directory, output_dir = Path(directory).resolve(), Path(output_dir).resolve()
    if output_dir == directory or directory in output_dir.parents:
        raise ValueError("비교 출력은 원본 실행 밖에 지정한다.")
    if output_dir.exists():
        raise FileExistsError(output_dir)
    if (
        not conditions
        or len(set(conditions)) != len(conditions)
        or set(conditions) - CONDITIONS.keys()
    ):
        raise ValueError("비교 조건은 A~E를 중복 없이 지정한다.")
    if any(CONDITIONS[c][1] for c in conditions) and judge_llm is None:
        raise ValueError("B·D·E에는 Judge가 반드시 필요하다.")
    read = lambda name: json.loads((directory / name).read_text(encoding="utf-8"))
    brief_data = read("input.json")
    brief = InterviewBrief(
        **{**brief_data, "seniority": Seniority(brief_data["seniority"])}
    )
    research = ResearchResult.model_validate(read("research.json"))
    selection = NFRSelection.model_validate(read("selection.json")["selection"])
    initial = NFRExport.model_validate(read("nfr_export-0.json"))
    initial_hash = _digest(initial.model_dump(mode="json"))
    output_dir.mkdir(parents=True)
    _save(
        output_dir / "manifest.json",
        {
            "source_run": directory.name,
            "initial_sha256": initial_hash,
            "brief": brief_data,
            "research_sha256": _digest(research.model_dump(mode="json")),
            "selection_sha256": _digest(selection.model_dump(mode="json")),
            "review_status": "provisional",
            "models": model_settings,
            "prompt_sha256": {
                str(path.relative_to(PROJECT_ROOT)): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in [
                    PROJECT_ROOT / "src/archgen/export/templates/rubric_system.md.j2",
                    PROJECT_ROOT / "src/archgen/judge/templates/system.md.j2",
                ]
            },
        },
    )
    harness = Runner(
        [
            check_weight_sum,
            check_criteria_count,
            check_levels,
            check_targets,
            check_cross_ref({d.id for d in research.documents}),
        ]
    )
    evaluations, rows = {}, {}
    baseline_evaluation = None
    for condition in conditions:
        use_harness, use_judge, limit = CONDITIONS[condition]
        target = output_dir / condition
        target.mkdir()
        export = initial.model_copy(deep=True)
        repairs = repair_attempts = judge_calls = repair_calls = harness_calls = 0
        rounds = []
        started = monotonic()
        status = "complete"
        failure = None

        def counted_repair(messages):
            nonlocal repair_calls
            repair_calls += 1
            return repair_llm(messages)

        def counted_judge(messages):
            nonlocal judge_calls
            judge_calls += 1
            return judge_llm(messages)

        try:
            while True:
                _save(
                    target / f"nfr_export-{repairs}.json", export.model_dump(mode="json")
                )
                findings = harness.run(export) if use_harness else []
                harness_calls += int(use_harness)
                if use_judge:
                    findings += judge_export(brief, research, export, counted_judge)
                record = {
                    "round": repairs,
                    "findings": [f.model_dump(mode="json") for f in findings],
                }
                rounds.append(record)
                _save(target / f"findings-{repairs}.json", record)
                if any(f.code == FindingCode.JUDGE_RESPONSE_INVALID for f in findings):
                    status = "judge_failed"
                    break
                errors = [f for f in findings if f.severity == Severity.ERROR]
                if not errors:
                    break
                fixable = rubric_repair_findings(errors)
                if limit and not fixable:
                    status = "requires_upstream_repair"
                    break
                if repairs == limit:
                    status = "observed_errors" if limit == 0 else "repair_limit"
                    break
                repair_attempts += 1
                export = generate_rubric(
                    brief,
                    research,
                    selection,
                    counted_repair,
                    count_tokens=count_tokens,
                    previous=export,
                    findings=fixable,
                )
                repairs += 1
        except Exception as error:  # noqa: BLE001 -- 조건 실패를 남기고 다음 독립 조건을 수행한다.
            status, failure = (
                "failed",
                {"type": type(error).__name__, "message": str(error)[:1000]},
            )
        operation_seconds = monotonic() - started
        render_findings = []
        render_error = None
        try:
            markdown = render_rubric(export, brief)
            render_findings = [
                f.model_dump(mode="json") for f in check_rendered(markdown, export, brief)
            ]
            (target / "nfr_rubric.md").write_text(markdown, encoding="utf-8")
        except Exception as error:  # noqa: BLE001 -- 렌더 오류는 보완 원인에서 제외한다.
            render_error = {"type": type(error).__name__, "message": str(error)[:1000]}
        _save(
            target / "render-findings.json",
            {"findings": render_findings, "error": render_error},
        )
        if render_error is not None or render_findings:
            status = "render_failed"
        _save(target / "nfr_export.json", export.model_dump(mode="json"))
        final_hash = _digest(export.model_dump(mode="json"))
        evaluation = None
        evaluation_error = None
        evaluation_started = monotonic()
        if render_error is None and not render_findings:
            try:
                if final_hash not in evaluations:
                    evaluations[final_hash] = evaluate_result(target / "nfr_rubric.md")
                evaluation = evaluations[final_hash]
            except Exception as error:  # noqa: BLE001 -- 독립 평가 실패를 품질 Fail로 바꾸지 않는다.
                evaluation_error = {
                    "type": type(error).__name__,
                    "message": str(error)[:1000],
                }
        if final_hash == initial_hash and baseline_evaluation is None:
            baseline_evaluation = evaluation
        if evaluation is not None:
            _save(target / "evaluation.json", evaluation)
        row = {
            "condition": condition,
            "status": status,
            "failure": failure,
            "initial_sha256": initial_hash,
            "final_sha256": final_hash,
            "harness_calls": harness_calls,
            "judge_calls": judge_calls,
            "repair_calls": repair_calls,
            "repair_attempts": repair_attempts,
            "repairs": repairs,
            "operation_seconds": operation_seconds,
            "evaluation_seconds": monotonic() - evaluation_started,
            "evaluation_error": evaluation_error,
            "evaluation": evaluation,
            "rounds": rounds,
            "render_errors": len(render_findings) + int(render_error is not None),
            "precision": None,
            "recall": None,
            "confirmed_errors": None,
            "review_status": "provisional",
            "provisional_changes": provisional_changes(baseline_evaluation, evaluation),
        }
        row["detection"] = human_detection_metrics(
            rounds[0]["findings"] if rounds else [], (review or {}).get(condition)
        )
        row["precision"], row["recall"] = (
            row["detection"]["precision"],
            row["detection"]["recall"],
        )
        rows[condition] = row
        _save(target / "result.json", row)
        _save(
            output_dir / "comparison.json",
            {"conditions": rows, "review_status": "provisional"},
        )
        write_comparison_table(output_dir / "comparison.md", rows)
    return {"conditions": rows, "review_status": "provisional"}


def write_comparison_table(path, rows):
    lines = [
        "# 하네스·Judge 비교",
        "",
        "독립 LLM 판정은 잠정 결과다. 사람 검토 전 Precision·Recall과 확인된 오류 수는 N/A다.",
        "",
        "| 조건 | 종료 상태 | 하네스 검사 | Judge 호출 | 보완 호출 / 완료 횟수 | 추가 시간(초) | 잠정 통과율 | Precision | Recall |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def show(value):
        return "N/A" if value is None else str(value)

    for name, row in rows.items():
        summary = (
            (row.get("evaluation") or {})
            .get("evaluation", {})
            .get("summary", {})
            .get("overall", {})
        )
        lines.append(
            f"| {name} | {row['status']} | {row['harness_calls']} | {row['judge_calls']} | "
            f"{row['repair_calls']} / {row['repairs']} | {row['operation_seconds']:.2f} | "
            f"{show(summary.get('percentage'))} | {show(row['precision'])} | {show(row['recall'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def human_detection_metrics(findings, review):
    """사람이 정답과 오탐 후보를 확인한 범위에서만 오류 ID 단위로 집계한다."""
    unknown = {"precision": None, "recall": None, "tp": None, "fp": None, "fn": None}
    if (
        not review
        or review.get("review_status") != "confirmed"
        or not review.get("reviewed_by")
    ):
        return {**unknown, "reason": "사람의 정답 판정이 없어 N/A다."}
    errors = review["errors"]
    if len({e["id"] for e in errors}) != len(errors):
        raise ValueError("사람 검토 오류 ID가 중복이다.")

    def key(finding):
        return finding["source"], finding["code"], finding["path"].removeprefix("export.")

    detected = {key(f) for f in findings}
    covered = {key(m) for e in errors for m in e["matches"]}
    if detected - covered:
        return {**unknown, "reason": "사람이 확인하지 않은 Finding이 있어 N/A다."}
    tp = fp = fn = 0
    for error in errors:
        hit = bool(detected & {key(m) for m in error["matches"]})
        if type(error["present"]) is not bool:
            raise ValueError("오류 존재 판정은 참 또는 거짓이어야 한다.")
        tp += int(error["present"] and hit)
        fp += int(not error["present"] and hit)
        fn += int(error["present"] and not hit)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(100 * tp / (tp + fp), 2) if tp + fp else None,
        "recall": round(100 * tp / (tp + fn), 2) if tp + fn else None,
        "reviewed_by": review["reviewed_by"],
    }


def run_comparison(directory, output_dir, *, conditions="ABCDE", review=None):
    """수동 실험만 실행한다. 조사·선정 및 일반 생성의 기본 Judge 설정은 바꾸지 않는다."""
    from langchain_core.messages import convert_to_messages

    from archgen.config import (
        bind_structured_model,
        build_chat_model,
        get_settings,
        response_text,
    )
    from archgen.core.service import _LLMTrace
    from archgen.domain.nfr import Rubric
    from archgen.evaluation import run
    from archgen.judge.judge import JudgeResponse

    output_dir = Path(output_dir)
    trace = _LLMTrace(output_dir)
    settings = get_settings()
    medium = build_chat_model(
        "medium",
        timeout=300,
        max_retries=0,
        tiktoken_model_name="gpt-4o",
        callbacks=[trace],
    )
    large = build_chat_model("large", timeout=600, max_retries=0, callbacks=[trace])
    repair = bind_structured_model(medium, Rubric)
    judge = bind_structured_model(large, JudgeResponse)
    return compare_run(
        directory,
        output_dir,
        conditions=conditions,
        review=review,
        model_settings={
            "generation": settings.model_medium,
            "generation_effort": settings.reasoning_effort_medium,
            "judge": settings.model_large,
            "judge_effort": settings.reasoning_effort_large,
            "evaluator": settings.model_large,
            "evaluator_effort": settings.reasoning_effort_large,
        },
        judge_llm=lambda messages: response_text(judge.invoke(messages)),
        repair_llm=lambda messages: response_text(repair.invoke(messages)),
        count_tokens=lambda messages: medium.get_num_tokens_from_messages(
            convert_to_messages(messages)
        ),
        evaluate_result=lambda path: run(
            [path],
            source="generation",
            failure_root=output_dir / "delivery-failed",
            metadata={
                "experiment": "m7-comparison",
                "condition": path.parent.name,
                "source_run": Path(directory).name,
                "review_status": "provisional",
            },
        ),
    )


def make_known_error_cases(directory, output_dir):
    """자연 발생 오류와 분리한 작은 탐지 확인용 복사본을 만든다."""
    import shutil

    directory, output_dir = Path(directory).resolve(), Path(output_dir).resolve()
    if output_dir == directory or directory in output_dir.parents:
        raise ValueError("오류 사례는 원본 실행 밖에 저장한다.")
    initial = NFRExport.model_validate_json(
        (directory / "nfr_export-0.json").read_text(encoding="utf-8")
    )
    output_dir.mkdir(parents=True)
    cases = []
    for name in ("weight", "level", "ambiguous"):
        export = initial.model_copy(deep=True)
        criterion = export.rubric.criteria[0]
        if name == "weight":
            criterion.weight += 1
            codes = ["WEIGHT_SUM_INVALID"]
            path = "rubric.criteria[0].weight"
        elif name == "level":
            criterion.levels[-1].score = criterion.levels[-2].score
            codes = ["LEVEL_DUPLICATED", "LEVEL_MISSING"]
            path = "rubric.criteria[0].levels"
        else:
            criterion.levels[
                2
            ].descriptor = "주요 문제를 적절하게 처리하는 설계를 설명한다."
            codes = ["LEVEL_AMBIGUOUS", "CRITERION_UNSCORABLE"]
            path = "rubric.criteria[0].levels[2].descriptor"
        target = output_dir / name
        target.mkdir()
        for filename in ("input.json", "research.json", "selection.json"):
            shutil.copyfile(directory / filename, target / filename)
        _save(target / "nfr_export-0.json", export.model_dump(mode="json"))
        case = {
            "id": name,
            "source_run": directory.name,
            "origin": "injected",
            "review_status": "synthetic_expected",
            "changed_path": path,
            "expected_codes": codes,
            "directory": str(target),
        }
        _save(target / "case.json", case)
        cases.append(case)
    _save(output_dir / "cases.json", cases)
    return cases


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--conditions", default="ABCDE")
    parser.add_argument("--review", type=Path, help="사람이 확인한 조건별 오류 라벨 JSON")
    args = parser.parse_args(argv)
    try:
        review = (
            json.loads(args.review.read_text(encoding="utf-8")) if args.review else None
        )
        result = run_comparison(
            args.run_dir, args.output, conditions=args.conditions, review=review
        )
    except Exception as error:  # noqa: BLE001 -- CLI는 실패를 표시하고 비정상 종료한다.
        parser.exit(1, f"{error}\n")
    print(
        json.dumps(
            {"output": str(args.output), "review_status": result["review_status"]},
            ensure_ascii=False,
        )
    )
    return int(
        any(
            row["failure"]
            or row["evaluation_error"]
            or row["status"] in {"judge_failed", "render_failed"}
            for row in result["conditions"].values()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
