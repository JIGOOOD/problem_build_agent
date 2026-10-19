import json
from unittest.mock import Mock

from archgen.stage_evaluation import evaluate_stage, load_run


def test_research_reads_numbered_fetch_and_search_once_and_requires_each_target(tmp_path):
    (tmp_path / "input.json").write_text(
        json.dumps({"seniority": "Middle", "topic": "매칭"})
    )
    (tmp_path / "research.json").write_text(
        json.dumps({"topic_summary": "매칭", "nfr_candidates": [], "documents": []})
    )
    raw = {
        "doc_id": "doc-1",
        "url": "https://example.org",
        "title": "원문",
        "sentences": [{"index": 3, "text": "조건부 예약으로 경쟁을 제어한다."}],
    }
    messages = [
        {
            "type": "tool",
            "content": json.dumps(
                [
                    {
                        "query_id": "query-1",
                        "url": raw["url"],
                        "title": raw["title"],
                        "rank": 1,
                    }
                ]
            ),
        },
        {"type": "tool", "content": json.dumps([{"url": raw["url"], "result": raw}])},
    ]
    for name in ["llm-1-input.json", "llm-2-input.json"]:
        (tmp_path / name).write_text(json.dumps({"messages": [messages]}))
    payload = load_run(tmp_path)
    assert len(payload["fetched"]) == len(payload["searches"]) == 1
    assert payload["fetched"][0]["sentences"] == raw["sentences"]

    def answer(msgs):
        expected = json.loads(
            next(
                line for line in msgs[0]["content"].splitlines() if line.startswith("[[")
            )
        )
        return json.dumps(
            {
                "results": [
                    {
                        "rubric": p,
                        "criterion_id": c,
                        "target_id": t,
                        "verdict": "Pass",
                        "applied_rule": "근거를 확인한다.",
                        "reason": "문서 번호와 원문에 설계 근거가 있다.",
                    }
                    for p, c, t in expected
                ]
            }
        )

    model = Mock(side_effect=answer)
    result = evaluate_stage("research", payload, model)
    assert {"doc-1", "overall"} == {r.target_id for r in result.results}
    assert result.summary["overall"]["failed"] == 0
    assert "https://example.org" in model.call_args.args[0][1]["content"]


def test_keep_scores_sentences_and_documents_with_code_budget_and_missing_original():
    payload = {
        "run_id": "run",
        "brief": {"focus": "중복 배정"},
        "research": {
            "documents": [
                {"id": "kept", "content": "원자적으로 확보한다."},
                {"id": "missing", "content": "보관 문장"},
            ]
        },
        "fetched": [
            {
                "doc_id": "kept",
                "sentences": [{"index": 7, "text": "원자적으로 확보한다."}],
                "original_available": True,
            },
            {
                "doc_id": "discarded",
                "sentences": [{"index": 1, "text": "경쟁 제어"}],
                "original_available": True,
            },
        ],
        "keep_budget_chars": 5,
    }

    def answer(msgs):
        keys = json.loads(
            next(
                line for line in msgs[0]["content"].splitlines() if line.startswith("[[")
            )
        )
        assert {c for _, c, _ in keys} == {"1-1", "1-2", "2-1"}
        sent = json.loads(msgs[1]["content"])["kept_sentences"]
        assert sent[0]["original_indices"] == [7]
        return json.dumps(
            {
                "results": [
                    {
                        "rubric": p,
                        "criterion_id": c,
                        "target_id": t,
                        "verdict": "Pass",
                        "applied_rule": "원문과 대조한다.",
                        "reason": "보관 근거를 확인했다.",
                    }
                    for p, c, t in keys
                ]
            }
        )

    result = evaluate_stage("keep", payload, answer)
    rows = {(r.criterion_id, r.target_id): r for r in result.results}
    assert len(rows) == 10
    assert rows["2-2", "kept"].verdict == "Fail"
    assert rows["2-2", "discarded"].verdict == "Pass"
    assert rows["1-1", "missing:kept-1"].verdict == "Pass"
    assert rows["1-2", "missing:kept-1"].verdict is None
    assert rows["2-1", "missing"].verdict is None
    assert result.summary["by_unit"]["sentence"]["unscorable"] == 1
    assert result.summary["by_unit"]["document"]["failed"] == 1


def test_selection_compares_each_selected_nfr_and_upstream_gaps_without_raw_fetch():
    payload = {
        "run_id": "run",
        "brief": {"focus": "주변 검색 지연"},
        "research": {
            "documents": [{"id": "doc-1", "content": "공간 분할로 검색 범위를 줄인다."}]
        },
        "selection": {"confirmed_nfrs": [{"id": "NFR-8", "kind": "latency"}]},
        "golden_reference": "참고이며 이름과 개수의 일치를 강제하지 않는다.",
        "fetched": [{"doc_id": "unrelated", "sentences": []}],
    }

    def answer(msgs):
        actual = json.loads(msgs[1]["content"])
        assert "fetched" not in actual
        assert actual["golden_reference"] == payload["golden_reference"]
        assert "상위" in msgs[0]["content"]
        keys = json.loads(
            next(
                line for line in msgs[0]["content"].splitlines() if line.startswith("[[")
            )
        )
        return json.dumps(
            {
                "results": [
                    {
                        "rubric": p,
                        "criterion_id": c,
                        "target_id": t,
                        "verdict": "Pass",
                        "applied_rule": "선정 근거를 대조한다.",
                        "reason": "선정된 요구가 보관 근거와 연결된다.",
                    }
                    for p, c, t in keys
                ]
            }
        )

    result = evaluate_stage("selection", payload, answer)
    assert {r.target_id for r in result.results} == {"NFR-8", "overall"}


def test_stage_run_records_trace_criteria_and_saves_without_touching_archive(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    from archgen.stage_evaluation import run_stage

    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "input.json").write_text(
        json.dumps({"seniority": "Middle", "topic": "매칭"})
    )
    (archive / "research.json").write_text(
        json.dumps({"topic_summary": "매칭", "nfr_candidates": [], "documents": []})
    )
    model = Mock(model_name="test-model")

    def invoke(messages):
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
                            "rubric": p,
                            "criterion_id": c,
                            "target_id": t,
                            "verdict": None,
                            "applied_rule": "확보한 자료로 평가한다.",
                            "reason": "원문이 없어 판단할 수 없다.",
                        }
                        for p, c, t in keys
                    ]
                }
            )
        )

    model.invoke.side_effect = invoke
    client = MagicMock()
    client.get_trace_url.return_value = "https://example.org/traces/trace-stage"
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "trace-stage", "span-stage"
    result = run_stage(archive, "research", tmp_path / "out", model=model, client=client)
    assert result["trace_id"] == "trace-stage"
    assert result["evaluation"]["summary"]["overall"]["percentage"] is None
    saved = json.loads((tmp_path / "out" / "research.json").read_text())
    assert saved["review_status"] == "provisional"
    assert saved["criteria_sha256"]
    assert saved["model"] == "test-model"
    assert saved["reasoning_effort"] is None
    assert sorted(p.name for p in archive.iterdir()) == ["input.json", "research.json"]
    client.api.scores.create.assert_not_called()


def test_input_failure_leaves_only_minimal_error_record_without_calling_model(tmp_path):
    import pytest

    from archgen.stage_evaluation import run_stage

    archive = tmp_path / "missing-input"
    archive.mkdir()
    model = Mock()
    with pytest.raises(FileNotFoundError):
        run_stage(archive, "research", tmp_path / "out", model=model, client=Mock())
    error = json.loads((tmp_path / "out/research.error.json").read_text())
    assert error["error_type"] == "FileNotFoundError"
    assert set(error) <= {
        "run_id",
        "stage",
        "error_type",
        "elapsed_seconds",
        "review_status",
    }
    model.invoke.assert_not_called()


def test_delivery_failure_keeps_no_document_or_judge_response_in_error_file(tmp_path):
    from unittest.mock import MagicMock

    import pytest

    from archgen.evaluation import Assessment, Evaluation, run

    client = MagicMock()
    span = client.start_as_current_observation.return_value.__enter__.return_value
    span.trace_id, span.id = "trace-failed", "span-failed"
    client.flush.side_effect = RuntimeError("전송 실패")
    assessment = Evaluation(
        results=[
            Assessment(
                rubric="run",
                criterion_id="O-1",
                target_id="overall",
                verdict="Fail",
                applied_rule="범위를 검토한다.",
                reason="보관 문서의 근거가 부족하다.",
            )
        ]
    )
    with pytest.raises(RuntimeError, match="Langfuse 기록 실패"):
        run(
            ["archive"],
            "criteria.md",
            model=Mock(model_name="fake"),
            client=client,
            source="stage-research",
            failure_root=tmp_path,
            metadata={"private_body": "외부 문서 원문"},
            evaluate_fn=lambda *_: assessment,
        )
    saved = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert set(saved) == {"trace_id", "source", "started_at", "model", "error_type"}
    assert "외부 문서 원문" not in json.dumps(saved, ensure_ascii=False)
    client.api.scores.create.assert_not_called()


def test_stage_freezes_criteria_text_before_model_call(tmp_path, monkeypatch):
    from archgen import evaluation as evaluator
    from archgen import stage_evaluation as stages

    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "input.json").write_text(
        json.dumps({"seniority": "Middle", "topic": "매칭"})
    )
    (archive / "research.json").write_text(
        json.dumps({"topic_summary": "매칭", "nfr_candidates": [], "documents": []})
    )
    criteria_root = tmp_path / "criteria"
    criteria_root.mkdir()
    original = "### O-1. 원래 기준\n기존 기준으로 평가한다.\n"
    source = criteria_root / "research.md"
    source.write_text(original)
    monkeypatch.setattr(stages, "CRITERIA_ROOT", criteria_root)

    def recorded_run(paths, criteria_path, *, evaluate_fn, **_):
        assert criteria_path != source
        source.write_text("### O-2. 실행 도중 바뀐 기준\n")

        def answer(messages):
            keys = json.loads(
                next(
                    line
                    for line in messages[0]["content"].splitlines()
                    if line.startswith("[[")
                )
            )
            assert {key[1] for key in keys} == {"O-1"}
            return json.dumps(
                {
                    "results": [
                        {
                            "rubric": p,
                            "criterion_id": c,
                            "target_id": t,
                            "verdict": None,
                            "applied_rule": "실행 당시 기준을 사용한다.",
                            "reason": "판단 자료가 없다.",
                        }
                        for p, c, t in keys
                    ]
                }
            )

        result = evaluate_fn(paths, criteria_path, answer)
        return {
            "trace_id": "frozen",
            "trace_url": "trace",
            "evaluation": result.model_dump(mode="json"),
        }

    monkeypatch.setattr(evaluator, "run", recorded_run)
    stages.run_stage(archive, "research", tmp_path / "out")
    assert (tmp_path / "out/research-criteria.md").read_text() == original


def test_keep_missing_budget_leaves_omission_and_budget_unscored():
    payload = {
        "run_id": "run",
        "research": {"documents": []},
        "fetched": [{"doc_id": "discarded", "original_available": True, "sentences": []}],
        "keep_budget_chars": None,
    }

    def answer(messages):
        keys = json.loads(
            next(
                line
                for line in messages[0]["content"].splitlines()
                if line.startswith("[[")
            )
        )
        assert keys == [["run", "2-1", "discarded"]]
        return json.dumps(
            {
                "results": [
                    {
                        "rubric": p,
                        "criterion_id": c,
                        "target_id": t,
                        "verdict": "Pass",
                        "applied_rule": "근거를 확인한다.",
                        "reason": "검토했다.",
                    }
                    for p, c, t in keys
                ]
            }
        )

    result = evaluate_stage("keep", payload, answer)
    assert all(row.verdict is None for row in result.results)
    assert result.summary["by_unit"]["sentence"]["percentage"] is None


def test_new_research_criteria_target_candidates_queries_fetches_and_overall():
    payload = {
        "run_id": "run",
        "brief": {},
        "research": {"documents": [], "nfr_candidates": []},
        "initial_plan": {"nfr_candidates": [{"kind": "latency", "reason": "검색 지연"}]},
        "queries": [
            {"query_id": "query-1", "related_nfr": "latency", "query": "공간 검색 지연"}
        ],
        "executed_queries": [{"id": "call-1", "query_id": "query-1"}],
        "searches": [],
        "fetched": [{"doc_id": "doc-1", "original_available": True, "sentences": []}],
        "fetch_failures": {"https://example.org/blocked": "접근 차단"},
    }

    def answer(messages):
        keys = json.loads(
            next(
                line
                for line in messages[0]["content"].splitlines()
                if line.startswith("[[")
            )
        )
        actual = {(c, t) for _, c, t in keys}
        assert ("1-2", "latency") in actual
        assert ("2-1", "latency") in actual
        assert ("3-1", "call-1") in actual
        assert ("4-1", "doc-1") in actual
        assert ("5-1", "fetch:https://example.org/blocked") in actual
        assert ("6-1", "overall") in actual and ("6-2", "overall") in actual
        return json.dumps(
            {
                "results": [
                    {
                        "rubric": p,
                        "criterion_id": c,
                        "target_id": t,
                        "verdict": "Pass",
                        "applied_rule": "저장 기록을 평가한다.",
                        "reason": "기록을 확인했다.",
                    }
                    for p, c, t in keys
                ]
            }
        )

    result = evaluate_stage("research", payload, answer)
    assert len(result.results) == 10


def test_load_run_recovers_initial_candidates_and_executed_query_text(tmp_path):
    (tmp_path / "input.json").write_text(
        json.dumps({"seniority": "Middle", "topic": "매칭"})
    )
    (tmp_path / "research.json").write_text(
        json.dumps({"topic_summary": "매칭", "nfr_candidates": [], "documents": []})
    )
    plan = {
        "topic_summary": "매칭",
        "nfr_candidates": [
            {"kind": "latency", "reason": "검색 지연을 검증한다."},
            {"kind": "consistency", "reason": "배정 경쟁을 검증한다."},
            {"kind": "throughput", "reason": "갱신 부하를 검증한다."},
        ],
        "search_queries": [
            {"query": "매칭 설계", "related_nfr": None},
            {"query": "공간 검색 지연", "related_nfr": "latency"},
            {"query": "배정 경쟁", "related_nfr": "consistency"},
            {"query": "위치 갱신 부하", "related_nfr": "throughput"},
        ],
    }
    messages = [
        {"type": "ai", "content": json.dumps(plan)},
        {
            "type": "ai",
            "tool_calls": [
                {"id": "call-1", "name": "search", "args": {"query_id": "query-2"}}
            ],
        },
        {
            "type": "ai",
            "tool_calls": [
                {
                    "id": "call-2",
                    "name": "requery",
                    "args": {"query_id": "query-2", "new_query": "공간 인덱스 조회 비용"},
                }
            ],
        },
    ]
    (tmp_path / "llm-1-input.json").write_text(
        json.dumps({"messages": [messages, messages]})
    )
    payload = load_run(tmp_path)
    assert payload["initial_plan"]["nfr_candidates"][0]["kind"] == "latency"
    assert [q["query"] for q in payload["executed_queries"]] == [
        "공간 검색 지연",
        "공간 인덱스 조회 비용",
    ]
    assert len(payload["queries"]) == 4


def test_search_results_preserve_original_and_requery_call_link(tmp_path):
    (tmp_path / "input.json").write_text(
        json.dumps({"seniority": "Middle", "topic": "매칭"})
    )
    (tmp_path / "research.json").write_text(
        json.dumps({"topic_summary": "매칭", "nfr_candidates": [], "documents": []})
    )
    row = {
        "query_id": "query-1",
        "url": "https://example.org",
        "title": "검색 결과",
        "rank": 1,
    }
    messages = [
        {"type": "tool", "tool_call_id": call_id, "content": json.dumps([row])}
        for call_id in ["first", "requery"]
    ]
    (tmp_path / "llm-1-input.json").write_text(json.dumps({"messages": [messages]}))
    payload = load_run(tmp_path)
    assert {r["search_call_id"] for r in payload["searches"]} == {"first", "requery"}
