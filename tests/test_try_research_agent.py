import json
from types import SimpleNamespace

import httpx
import pytest
from langchain_core.messages import AIMessage, AIMessageChunk

import try_research_agent as manual
from archgen.research.agent import bind_initial_research_model


def test_raw_stream_records_field_sizes_before_langchain_drops_reasoning(tmp_path):
    events = [
        {"role": "assistant", "content": " "},
        {"reasoning_content": "private reasoning"},
        {"reasoning_details": [{"type": "reasoning.text", "text": "private details"}]},
        {"content": "{}"},
    ]
    chunks = [
        {
            "id": "test",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "test",
            "choices": [
                {"index": 0, "delta": delta, "finish_reason": "stop" if i == 3 else None}
            ],
        }
        for i, delta in enumerate(events)
    ]
    body = (
        "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n"
    )
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, text=body
            )
        )
    ) as client:
        model = manual.RawTraceChatOpenAI(
            model="test",
            api_key="offline-test-key",
            base_url="https://example.test/v1",
            http_client=client,
            max_retries=0,
        )
        trace = manual.TraceLLM(model, tmp_path, 600, debug=True)
        response = bind_initial_research_model(trace).invoke(
            [{"role": "user", "content": "plan"}]
        )

    assert response.content == " {}"
    path = tmp_path / "step-01-stream.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(records) == 4
    assert records[1]["choices"][0]["delta_chars"] == {"reasoning_content": 17}
    assert records[2]["choices"][0]["delta_chars"]["reasoning_details"] > 0
    assert records[-1]["choices"][0]["finish_reason"] == "stop"
    assert "private reasoning" not in path.read_text()
    assert "private details" not in path.read_text()


def tool_call(name, arguments):
    return AIMessage(
        content="",
        tool_calls=[
            {"id": f"{name}-{i}", "name": name, "args": args, "type": "tool_call"}
            for i, args in enumerate(arguments, start=1)
        ],
    )


class Model:
    def __init__(self, *responses):
        self.responses = iter(responses)

    def bind(self, **kwargs):
        return self

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        response = next(self.responses)
        return response(messages) if callable(response) else response

    def stream(self, messages, **kwargs):
        response = self.invoke(messages)
        yield AIMessageChunk(**response.model_dump(exclude={"type"}))


def test_manual_runner_defaults_to_ten_minutes_per_llm_call(monkeypatch):
    options = {}

    def build_model(name, **kwargs):
        options.update(kwargs)
        raise RuntimeError("stop before any network call")

    monkeypatch.setattr(manual, "build_chat_model", build_model)

    with pytest.raises(RuntimeError, match="stop before any network call"):
        manual.run()

    assert options["timeout"] == 600


def test_initial_plan_requests_strict_schema_but_tool_loop_does_not(tmp_path):
    bindings = []
    model = Model(AIMessage(content="{}"), AIMessage(content="done"))

    def bind(**kwargs):
        bindings.append(kwargs)
        return model

    model.bind = bind
    trace = manual.TraceLLM(model, tmp_path, 600)
    bind_initial_research_model(trace).invoke([{"role": "user", "content": "chat"}])

    options = bindings[0]
    assert options["response_format"]["type"] == "json_schema"
    spec = options["response_format"]["json_schema"]
    assert spec["strict"] is True
    schema = spec["schema"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "topic_summary",
        "nfr_candidates",
        "search_queries",
    }
    queries = schema["properties"]["search_queries"]
    assert queries["type"] == "array"
    assert queries["items"]["additionalProperties"] is False
    assert set(queries["items"]["required"]) == {"query", "related_nfr"}
    assert options["extra_body"]["provider"]["require_parameters"] is True

    trace.bind_tools([])
    trace.invoke(
        [
            {"role": "system", "content": "research"},
            {"role": "user", "content": "chat"},
            {"role": "assistant", "content": '{"search_queries":[]}'},
        ]
    )
    assert len(bindings) == 1


def test_manual_runner_labels_query_and_search_rank_and_saves_context(
    tmp_path, monkeypatch, capsys
):
    topic_url = "https://docs.example/topic"
    latency_urls = ["https://docs.example/latency/1", "https://docs.example/latency/2"]
    kinds = ["latency", "availability", "consistency"]
    plan = {
        "topic_summary": "채팅 설계 조사",
        "nfr_candidates": [
            {"kind": kind, "reason": "채팅 설계에 중요하다"} for kind in kinds
        ],
        "search_queries": [
            {"query": "chat", "related_nfr": None},
            *[{"query": f"chat {kind}", "related_nfr": kind} for kind in kinds],
        ],
    }

    def keep_fetched(messages):
        return tool_call(
            "keep",
            [
                {
                    "doc_id": item["result"]["doc_id"],
                    "sentence_indices": [1],
                }
                for message in messages[-2:]
                for item in json.loads(message["content"])
            ],
        )

    model = Model(
        AIMessage(content=json.dumps(plan)),
        tool_call(
            "search",
            [
                {"query_id": f"query-{i}"}
                for i, _ in enumerate(plan["search_queries"], start=1)
            ],
        ),
        tool_call("fetch", [{"query_id": "query-1"}, {"query_id": "query-2"}]),
        keep_fetched,
        AIMessage(content="조사 완료"),
    )

    def search(*, query, max_results):
        urls = (
            [topic_url]
            if query == "chat"
            else latency_urls
            if query == "chat latency"
            else []
        )
        return {"results": [{"url": url, "title": url} for url in urls]}

    monkeypatch.setattr(manual, "build_chat_model", lambda *a, **kw: model)
    monkeypatch.setattr(
        manual, "TavilyClient", lambda **kw: SimpleNamespace(search=search)
    )
    monkeypatch.setattr(
        manual,
        "HttpFetcher",
        lambda client: (
            lambda url: {"title": url, "content": "소개\n\n설계 근거 p99 100ms"}
        ),
    )
    monkeypatch.setenv("TAVILY_API_KEY", "offline-test-key")

    run_dir = manual.run(log_root=tmp_path)

    output = capsys.readouterr().out
    assert "[SEARCH 시작] 4건" in output
    assert "query-2 · latency" in output
    assert "검색어: chat latency" in output
    assert "[FETCH 시작] 2개 쿼리" in output
    assert f"#2 | 성공 | 본문 2문장 · {latency_urls[1]}" in output
    assert "[KEEP 시작] 3건" in output
    assert "문장: [1]" in output
    assert "[KEEP 결과] 3건" in output
    assert "쿼리 누적 문서: 2개" in output
    assert "[결과] 후보 1개 | 수집 3개 | 보존 3개" in output
    fetches = json.loads((run_dir / "step-03-tools.json").read_text())
    assert fetches[1]["context"] == {
        "query_id": "query-2",
        "related_nfr": "latency",
    }
    batch = json.loads(fetches[1]["result"]["content"])
    assert [(item["rank"], item["url"]) for item in batch] == list(
        enumerate(latency_urls, start=1)
    )
    assert len(json.loads((run_dir / "result.json").read_text())["documents"]) == 3
    assert not (run_dir / "messages.json").exists()
    assert "offline-test-key" not in "".join(p.read_text() for p in run_dir.iterdir())


def test_display_groups_fetch_results_by_query_and_shortens_long_urls(capsys):
    display = manual.TraceDisplay()
    display.set_plan(
        {
            "search_queries": [
                {"query": "chat latency", "related_nfr": "latency"},
                {"query": "chat availability", "related_nfr": "availability"},
            ]
        }
    )
    urls = ["https://docs.example/" + "a" * 200, "https://docs.example/down"]
    for i, url in enumerate(urls, start=1):
        display.remember(
            {"name": "search"},
            json.dumps(
                [
                    {"query_id": f"query-{i}", "url": url, "rank": i},
                ]
            ),
        )
    capsys.readouterr()
    calls = [{"name": "fetch", "args": {"query_id": f"query-{i}"}} for i in [1, 2]]

    display.batch(
        calls,
        [
            json.dumps(
                [
                    {
                        "url": urls[0],
                        "rank": 1,
                        "result": {
                            "doc_id": "doc-a",
                            "url": urls[0],
                            "sentences": [{"index": 0, "text": "本文"}],
                        },
                    }
                ]
            ),
            json.dumps(
                [{"url": urls[1], "rank": 2, "result": "fetch 실패: HTTP 403 Forbidden"}]
            ),
        ],
    )

    output = capsys.readouterr().out
    assert output.count("[FETCH 결과]") == 1
    assert "query-1 · latency" in output
    assert "#1 | 성공 | 본문 1문장" in output
    assert "query-2 · availability" in output
    assert "#2 | 실패 | fetch 실패: HTTP 403 Forbidden" in output
    assert urls[0] not in output
    assert max(map(len, output.splitlines())) <= 120


def test_trace_reports_initial_plan_retry_and_timeout_separately(tmp_path, capsys):
    def timeout(messages):
        raise TimeoutError("LLM 호출이 실제 경과 시간 300초를 초과했습니다.")

    trace = manual.TraceLLM(Model(AIMessage(content="{}"), timeout), tmp_path, 300)
    initial = [{"role": "system", "content": "plan"}, {"role": "user", "content": "chat"}]
    trace.invoke(initial)
    feedback = (
        "직전 응답이 ResearchPlan 규칙을 어겼다.\n- (전체): 후보에 없는 kind: consistency"
    )

    with pytest.raises(TimeoutError):
        trace.invoke(
            [
                *initial,
                {"role": "assistant", "content": "{}"},
                {"role": "user", "content": feedback},
            ]
        )

    output = capsys.readouterr().out
    assert "초기 계획 재시도" in output
    assert "재시도 이유: 후보에 없는 kind: consistency" in output
    assert "[시간 초과] LLM 02 · 초기 계획 재시도 · 상한 300초" in output
    record = json.loads((tmp_path / "step-02-llm.json").read_text())
    assert record["status"] == "error"
    assert record["error_type"] == "TimeoutError"


def test_trace_measures_first_chunk_and_first_output_separately(tmp_path, monkeypatch):
    clock = SimpleNamespace(now=0.0)
    monkeypatch.setattr(manual.time, "monotonic", lambda: clock.now)

    def stream(messages, **kwargs):
        assert kwargs == {"stream_usage": True}
        clock.now = 2.0
        yield AIMessageChunk(content="")
        clock.now = 5.0
        yield AIMessageChunk(content='{"ok":')
        clock.now = 7.0
        yield AIMessageChunk(content="true}")
        clock.now = 8.0
        yield AIMessageChunk(
            content="",
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": 4,
                "total_tokens": 14,
            },
        )
        clock.now = 9.0

    model = Model()
    model.stream = stream
    trace = manual.TraceLLM(model, tmp_path, 300)

    response = trace.invoke([{"role": "user", "content": "plan"}])

    assert json.loads(response.content) == {"ok": True}
    assert response.usage_metadata["output_tokens"] == 4
    record = json.loads((tmp_path / "step-01-llm.json").read_text())
    assert record["first_chunk_seconds"] == 2.0
    assert record["first_output_seconds"] == 5.0
    assert record["seconds"] == 9.0
    assert record["chunks_received"] == 4
    assert record["output_chars"] == len('{"ok":true}')


def test_trace_assembles_fragmented_tool_arguments(tmp_path):
    def stream(messages, **kwargs):
        yield AIMessageChunk(
            content="",
            tool_call_chunks=[
                {
                    "index": 0,
                    "id": "call-1",
                    "name": "fetch",
                    "args": '{"url":"https://',
                }
            ],
        )
        yield AIMessageChunk(
            content="",
            tool_call_chunks=[
                {
                    "index": 0,
                    "id": None,
                    "name": None,
                    "args": 'docs.example/a"}',
                }
            ],
        )

    model = Model()
    model.stream = stream
    trace = manual.TraceLLM(model, tmp_path, 300)
    trace.bind_tools([])

    response = trace.invoke(
        [
            {"role": "system", "content": "research"},
            {"role": "user", "content": "chat"},
            {"role": "assistant", "content": '{"search_queries":[]}'},
        ]
    )

    assert isinstance(response, AIMessage)
    assert response.tool_calls == [
        {
            "id": "call-1",
            "name": "fetch",
            "args": {"url": "https://docs.example/a"},
            "type": "tool_call",
        }
    ]
    record = json.loads((tmp_path / "step-01-llm.json").read_text())
    assert record["first_output_seconds"] is not None
    assert record["output_chars"] == len('{"url":"https://docs.example/a"}')


@pytest.mark.parametrize("partial", ["", '{"topic_summary":'])
def test_trace_saves_received_data_on_timeout(tmp_path, partial, monkeypatch, capsys):
    closed = []
    clock = SimpleNamespace(now=0.0)
    monkeypatch.setattr(manual.time, "monotonic", lambda: clock.now)

    def stream(messages, **kwargs):
        try:
            if partial:
                clock.now = 2.0
                yield AIMessageChunk(content=partial)
            clock.now = 30.0
            trace.show_elapsed(30)
            raise TimeoutError("stream timed out")
        finally:
            closed.append(True)

    model = Model()
    model.stream = stream
    trace = manual.TraceLLM(model, tmp_path, 30)
    with pytest.raises(TimeoutError, match="stream timed out"):
        trace.invoke([{"role": "user", "content": "plan"}])

    record = json.loads((tmp_path / "step-01-llm.json").read_text())
    assert record["status"] == "error"
    assert record["seconds"] == 30
    assert record["first_chunk_seconds"] == (2.0 if partial else None)
    assert record["first_output_seconds"] == (2.0 if partial else None)
    assert record["output_chars"] == len(partial)
    assert record["chunks_received"] == bool(partial)
    if partial:
        assert record["partial_response"]["content"] == partial
    else:
        assert "partial_response" not in record
    assert closed == [True]
    output = capsys.readouterr().out
    assert ("수신 중 30/30초" if partial else "첫 청크 대기 30/30초") in output


@pytest.mark.parametrize("debug", [False, True])
def test_trace_saves_full_input_messages_only_in_debug_mode(tmp_path, debug):
    messages = [{"role": "user", "content": "full-input-for-debug"}]
    trace = manual.TraceLLM(Model(AIMessage(content="{}")), tmp_path, 300, debug=debug)

    trace.invoke(messages)

    record = json.loads((tmp_path / "step-01-llm.json").read_text())
    assert ("messages" in record) is debug
    if debug:
        assert record["messages"] == messages
    assert record["response"]["content"] == "{}"
    assert record["status"] == "completed"
    assert record["first_chunk_seconds"] is not None


def test_display_labels_requery_with_its_query_and_new_search_text(capsys):
    display = manual.TraceDisplay()
    display.set_plan(
        {"search_queries": [{"query": "chat latency", "related_nfr": "latency"}]}
    )
    call = {
        "name": "requery",
        "args": {
            "query_id": "query-1",
            "new_query": "chat p99 design",
            "reason": "근거 부족",
        },
    }

    display.remember(call, "[]")
    display.batch([call], ["[]"])

    output = capsys.readouterr().out
    assert "[REQUERY 결과]" in output
    assert "query-1 · latency" in output
    assert "검색어: chat p99 design" in output
