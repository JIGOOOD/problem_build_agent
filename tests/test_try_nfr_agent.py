import json
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage

import try_nfr_agent as manual
from archgen.domain.nfr import NFRSelection
from archgen.domain.research import Document, ResearchResult
from archgen.harness.findings import Finding, Severity


@pytest.fixture
def saved_m4(tmp_path, monkeypatch, golden_export, golden_document_ids):
    research_dir = tmp_path / ".archgen" / "research-agent" / "saved"
    research_dir.mkdir(parents=True)
    research = ResearchResult(
        topic_summary="채팅 조사",
        nfr_candidates=[],
        documents=[
            Document(id=i, title=i, url=f"https://example.com/{i}", content="보존 원문")
            for i in sorted(golden_document_ids)
        ],
    )
    (research_dir / "result.json").write_text(research.model_dump_json())
    (research_dir / "run.log").write_text("주제: 채팅 서비스\n")
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    model = Mock()
    model.bind.return_value = model
    model.get_num_tokens_from_messages.return_value = 9000
    model.invoke.side_effect = [
        AIMessage(content=selection.model_dump_json()),
        AIMessage(content=golden_export.rubric.model_dump_json()),
    ]
    monkeypatch.setattr(manual, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(manual, "build_chat_model", lambda *a, **kw: model)

    return model


def test_saved_m4_result_produces_logged_selection_and_validated_markdown(
    saved_m4, golden_export, monkeypatch
):
    factory = Mock(return_value=saved_m4)
    monkeypatch.setattr(manual, "build_chat_model", factory)
    run_dir = manual.run()

    assert factory.call_args.args == ("small",)
    assert saved_m4.invoke.call_count == 2
    assert json.loads((run_dir / "selection.json").read_text())["status"] == "selected"
    assert json.loads(
        (run_dir / "nfr_export.json").read_text()
    ) == golden_export.model_dump(mode="json")
    assert json.loads((run_dir / "findings-0.json").read_text()) == []
    assert json.loads((run_dir / "post-render-findings.json").read_text()) == []
    assert (run_dir / "nfr_rubric.md").read_text().startswith("# 채팅 서비스")
    for stage in ("NFR 선정", "루브릭 생성", "검증", "완료"):
        assert stage in (run_dir / "run.log").read_text()
    assert (run_dir / "llm-01-input.json").exists()
    assert (run_dir / "llm-02-response.json").exists()


@pytest.mark.parametrize("nfr_count", [0, 1])
def test_insufficient_nfrs_save_partial_selection_and_stop(
    saved_m4, golden_export, tmp_path, nfr_count
):
    selection = NFRSelection(
        confirmed_nfrs=golden_export.confirmed_nfrs[:nfr_count], tradeoffs=[]
    )
    saved_m4.invoke.side_effect = [AIMessage(content=selection.model_dump_json())]

    with pytest.raises(RuntimeError, match="근거"):
        manual.run()

    run_dir = next((tmp_path / ".archgen" / "nfr-agent").iterdir())
    assert saved_m4.invoke.call_count == 1
    output = json.loads((run_dir / "selection.json").read_text())
    assert output["status"] == "insufficient_evidence"
    assert len(output["selection"]["confirmed_nfrs"]) == nfr_count
    assert output["reason"]
    assert (run_dir / "error.json").exists()
    assert not (run_dir / "nfr_rubric.md").exists()


@pytest.mark.parametrize("repair_at", [1, 2, None])
def test_harness_repairs_are_bounded_and_record_previous_output(
    saved_m4, golden_export, tmp_path, repair_at
):
    selection = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
    broken = golden_export.rubric.model_copy(deep=True)
    broken.criteria[0].weight += 1
    responses = [AIMessage(content=selection.model_dump_json())]
    responses += [AIMessage(content=broken.model_dump_json())] * (repair_at or 3)
    if repair_at:
        responses.append(AIMessage(content=golden_export.rubric.model_dump_json()))
    saved_m4.invoke.side_effect = responses

    if repair_at:
        run_dir = manual.run()
        assert (run_dir / "nfr_rubric.md").exists()
        assert json.loads((run_dir / f"findings-{repair_at}.json").read_text()) == []
    else:
        with pytest.raises(RuntimeError, match="2회"):
            manual.run()
        run_dir = next((tmp_path / ".archgen" / "nfr-agent").iterdir())
        assert (run_dir / "error.json").exists()
        assert not (run_dir / "nfr_rubric.md").exists()
    assert saved_m4.invoke.call_count == (repair_at + 2 if repair_at else 4)
    payload = json.loads(saved_m4.invoke.call_args_list[2].args[0][1]["content"])
    assert payload["previous"]["rubric"] == broken.model_dump(mode="json")
    assert payload["findings"][0]["code"] == "WEIGHT_SUM_INVALID"
    assert payload["selection"] == selection.model_dump(mode="json")


@pytest.mark.parametrize(
    "failure", ["budget", "json", "schema", "timeout", "no_documents", "render"]
)
def test_failures_leave_diagnostics_without_successful_markdown(
    saved_m4, tmp_path, monkeypatch, failure
):
    if failure == "budget":
        saved_m4.get_num_tokens_from_messages.return_value = 10001
    elif failure == "json":
        saved_m4.invoke.side_effect = [AIMessage(content="invalid JSON")]
    elif failure == "schema":
        saved_m4.invoke.side_effect = [
            AIMessage(content='{"confirmed_nfrs": [{}], "tradeoffs": []}')
        ]
    elif failure == "timeout":
        saved_m4.invoke.side_effect = TimeoutError("모델 응답 시간 초과")
    elif failure == "no_documents":
        source = next((tmp_path / ".archgen" / "research-agent").glob("*/result.json"))
        raw = json.loads(source.read_text())
        raw["documents"] = []
        source.write_text(json.dumps(raw))
    else:
        monkeypatch.setattr(
            manual,
            "check_rendered",
            lambda *a: [
                Finding(
                    code="RENDER_HEADER_MISMATCH",
                    severity=Severity.ERROR,
                    path="header",
                    message="렌더 결과 불일치",
                )
            ],
        )

    with pytest.raises((ValueError, RuntimeError, TimeoutError)):
        manual.run()

    run_dir = next((tmp_path / ".archgen" / "nfr-agent").iterdir())
    assert json.loads((run_dir / "error.json").read_text())["message"]
    assert "실행 실패" in (run_dir / "run.log").read_text()
    assert not (run_dir / "nfr_rubric.md").exists()
    expected_calls = (
        0 if failure in {"budget", "no_documents"} else 2 if failure == "render" else 1
    )
    assert saved_m4.invoke.call_count == expected_calls
    if failure == "render":
        assert (run_dir / "nfr_export.json").exists()
        assert (run_dir / "post-render-findings.json").exists()
    elif failure in {"json", "schema"}:
        assert (run_dir / "llm-01-response.json").exists()
