import json
from unittest.mock import Mock

import pytest

from archgen.core.graph import build_generation_graph, new_thread_config
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.domain.nfr import NFRSelection
from archgen.domain.research import Document, ResearchResult
from archgen.paths import CATALOG_DIR

BRIEF = InterviewBrief(Seniority.SENIOR, "채팅 서비스")


@pytest.fixture
def pipeline(tmp_path, golden_export, golden_document_ids):
    research = ResearchResult(
        topic_summary="채팅 조사",
        nfr_candidates=[],
        documents=[
            Document(id=i, title=i, url=f"https://example.com/{i}", content="보존 원문")
            for i in sorted(golden_document_ids)
        ],
    )
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    return {
        "research": Mock(return_value=research),
        "llm": Mock(
            side_effect=[
                selection.model_dump_json(),
                golden_export.rubric.model_dump_json(),
            ]
        ),
        "count_tokens": Mock(return_value=9000),
        "catalog": load_catalog(CATALOG_DIR),
        "output_dir": tmp_path,
    }


def invoke(pipeline):
    return build_generation_graph(**pipeline).invoke(
        {"brief": BRIEF, "events": []}, config=new_thread_config()
    )


def test_research_result_reaches_selection_and_rubric(pipeline, golden_export):
    result = invoke(pipeline)

    pipeline["research"].assert_called_once_with(BRIEF)
    assert result["export"] == golden_export
    assert result["research"] == pipeline["research"].return_value
    assert result["selection"].status == "selected"
    assert pipeline["llm"].call_count == 2
    for call in pipeline["llm"].call_args_list:
        payload = json.loads(call.args[0][1]["content"])
        assert payload["research"] == result["research"].model_dump(mode="json")
        assert payload["brief"]["seniority"] == "Senior"
        assert "notes" not in payload["brief"]


@pytest.mark.parametrize("failure", [None, "pre", "post"])
def test_checks_render_and_judge_run_in_order(
    pipeline, monkeypatch, failure, golden_export
):
    import archgen.core.graph as module
    from archgen.harness.findings import Finding, Severity

    calls = []
    error = Finding(
        code="TEST_ERROR", severity=Severity.ERROR, path="rubric", message="실패"
    )
    runner = Mock()
    runner.run.side_effect = lambda export: (
        calls.append("pre") or ([error] if failure == "pre" else [])
    )
    monkeypatch.setattr(module, "Runner", lambda checks: runner)
    renderer = module.render_rubric
    monkeypatch.setattr(
        module, "render_rubric", lambda *args: calls.append("render") or renderer(*args)
    )
    monkeypatch.setattr(
        module,
        "check_rendered",
        lambda *args: calls.append("post") or ([error] if failure == "post" else []),
    )
    pipeline["judge_llm"] = Mock(
        side_effect=lambda messages: calls.append("judge") or '{"findings": []}'
    )
    if failure == "pre":
        pipeline["llm"].side_effect = [
            NFRSelection(
                **golden_export.model_dump(exclude={"rubric"})
            ).model_dump_json(),
            *[golden_export.rubric.model_dump_json()] * 3,
        ]

    result = invoke(pipeline)

    assert (
        calls
        == {
            None: ["pre", "render", "post", "judge"],
            "pre": ["pre"] * 3,
            "post": ["pre", "render", "post"],
        }[failure]
    )
    assert result["findings"] == ([error] if failure else [])


@pytest.mark.parametrize(
    "scenario,repairs,status",
    [
        ("pre", 1, "complete"),
        ("judge", 1, "complete"),
        ("mixed", 2, "complete"),
        ("pre_exhausted", 2, "failed"),
        ("judge_exhausted", 2, "failed"),
    ],
)
def test_repair_budget_is_shared_and_reuses_research(
    pipeline, golden_export, scenario, repairs, status
):
    selected = NFRSelection(
        **golden_export.model_dump(exclude={"rubric"})
    ).model_dump_json()
    valid = golden_export.rubric.model_dump_json()
    broken = golden_export.rubric.model_copy(deep=True)
    broken.criteria[0].weight += 1
    invalid = broken.model_dump_json()
    responses = {
        "pre": [selected, invalid, valid],
        "judge": [selected, valid, valid],
        "mixed": [selected, invalid, valid, valid],
        "pre_exhausted": [selected, invalid, invalid, invalid],
        "judge_exhausted": [selected, valid, valid, valid],
    }
    pipeline["llm"].side_effect = responses[scenario]
    error = json.dumps(
        {
            "findings": [
                {
                    "code": "LEVEL_AMBIGUOUS",
                    "severity": "ERROR",
                    "path": "rubric.criteria.0.levels",
                    "message": "단계가 모호하다",
                }
            ]
        }
    )
    pipeline["judge_llm"] = Mock(
        side_effect=[error] * 3
        if scenario == "judge_exhausted"
        else [error, '{"findings": []}']
        if scenario in {"judge", "mixed"}
        else ['{"findings": []}']
    )

    result = invoke(pipeline)

    assert result["repairs"] == repairs
    assert result["status"] == status
    pipeline["research"].assert_called_once()
    assert pipeline["llm"].call_count == 2 + repairs
    for call in pipeline["llm"].call_args_list[2:]:
        payload = json.loads(call.args[0][1]["content"])
        assert payload["research"] == result["research"].model_dump(mode="json")
        assert payload["selection"] == result["selection"].selection.model_dump(
            mode="json"
        )
        assert payload["previous"]
        assert any(f["severity"] == "ERROR" for f in payload["findings"])


def test_post_render_error_stops_without_repair_or_judge(pipeline, monkeypatch):
    import archgen.core.graph as module
    from archgen.harness.findings import Finding, Severity

    failure = Finding(
        code="RENDER_HEADER_MISMATCH",
        severity=Severity.ERROR,
        path="header",
        message="렌더 불일치",
    )
    monkeypatch.setattr(module, "check_rendered", lambda *args: [failure])
    pipeline["judge_llm"] = Mock()

    result = invoke(pipeline)

    assert result["status"] == "failed"
    assert result["repairs"] == 0
    assert result["findings"] == [failure]
    assert pipeline["llm"].call_count == 2
    pipeline["judge_llm"].assert_not_called()


@pytest.mark.parametrize(
    "status", ["complete", "failed", "insufficient_evidence", "candidate_not_found"]
)
def test_finalize_preserves_artifacts_and_only_publishes_valid_markdown(
    pipeline, golden_export, status
):
    if status == "failed":
        broken = golden_export.rubric.model_copy(deep=True)
        broken.criteria[0].weight += 1
        pipeline["llm"].side_effect = [
            NFRSelection(
                **golden_export.model_dump(exclude={"rubric"})
            ).model_dump_json(),
            *[broken.model_dump_json()] * 3,
        ]
    elif status == "insufficient_evidence":
        pipeline["llm"].side_effect = [
            NFRSelection(
                confirmed_nfrs=golden_export.confirmed_nfrs[:1], tradeoffs=[]
            ).model_dump_json()
        ]
    elif status == "candidate_not_found":
        pipeline["research"].return_value = ResearchResult(
            topic_summary="근거 없음", nfr_candidates=[], documents=[]
        )

    result = invoke(pipeline)

    root = pipeline["output_dir"]
    assert result["status"] == status
    assert result["phase"] == "finalize"
    assert result["output_dir"] == str(root)
    assert json.loads((root / "status.json").read_text())["status"] == status
    assert json.loads((root / "findings.json").read_text()) == [
        f.model_dump(mode="json") for f in result["findings"]
    ]
    assert (root / "research.json").exists()
    assert (root / "selection.json").exists()
    assert (root / "input.json").exists()
    assert (root / "nfr_export.json").exists() == (status in {"complete", "failed"})
    assert (root / "nfr_rubric.md").exists() == (status == "complete")
    if status == "complete":
        assert (root / "nfr_rubric.md").read_text().startswith("# 채팅 서비스")
        assert "judge: disabled" in "\n".join(result["events"])
    elif status == "candidate_not_found":
        pipeline["llm"].assert_not_called()
        pipeline["count_tokens"].assert_not_called()
    elif status == "insufficient_evidence":
        assert pipeline["llm"].call_count == 1
        assert result["reason"]


@pytest.mark.parametrize(
    "response",
    [
        '{"findings": [{"code": "LEVEL_AMBIGUOUS", "severity": "WARN", "path": "rubric.criteria.0", "message": "보완 권고"}]}',
        "invalid json",
    ],
)
def test_judge_warnings_are_preserved_without_repair(pipeline, response):
    pipeline["judge_llm"] = Mock(return_value=response)

    result = invoke(pipeline)

    assert result["status"] == "complete"
    assert result["repairs"] == 0
    assert len(result["findings"]) == 1
    assert result["findings"][0].severity == "WARN"
    assert result["findings"][0].source == "judge"
    assert pipeline["llm"].call_count == 2
    assert (pipeline["output_dir"] / "nfr_rubric.md").exists()
    assert (
        json.loads((pipeline["output_dir"] / "findings.json").read_text())[0]["severity"]
        == "WARN"
    )


def test_invalid_brief_is_rejected_before_any_external_call(pipeline):
    graph = build_generation_graph(**pipeline)

    with pytest.raises(TypeError, match="InterviewBrief"):
        graph.invoke({"brief": ["채팅"], "events": []}, config=new_thread_config())

    pipeline["research"].assert_not_called()
    pipeline["llm"].assert_not_called()
