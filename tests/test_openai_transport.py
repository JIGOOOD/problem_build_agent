"""실제 SDK의 Responses 변환을 가짜 HTTP 전송으로 검증한다."""

import json

import httpx
import pytest
from langchain_core.messages.utils import convert_to_openai_messages

from archgen import config
from archgen.domain.nfr import NFRSelection, Rubric
from archgen.judge.judge import JudgeResponse
from archgen.research.agent import bind_initial_research_model
from archgen.research.runner import TOOLS


def reply(output):
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "model": "gpt-6.1-sol",
        "status": "completed",
        "error": None,
        "output": output,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        },
    }


def text_output(text):
    return [
        {
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": text, "annotations": []}],
        }
    ]


@pytest.mark.parametrize("schema", [NFRSelection, Rubric, JudgeResponse])
def test_generation_schemas_reach_the_responses_api(monkeypatch, golden_export, schema):
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: config.Settings(
            "fake-key",
            "https://api.openai.com/v1",
            "gpt-6.1-sol",
            "gpt-6.1-sol",
            "gpt-6.1-sol",
        ),
    )
    outputs = {
        NFRSelection: NFRSelection(**golden_export.model_dump(exclude={"rubric"})),
        Rubric: golden_export.rubric,
        JudgeResponse: JudgeResponse(findings=[]),
    }
    raw = outputs[schema].model_dump_json()

    def handle(request):
        assert request.url.path == "/v1/responses"
        spec = json.loads(request.content)["text"]["format"]
        assert spec["type"] == "json_schema"
        assert spec["name"] == schema.__name__
        assert spec["strict"] is True
        assert spec["schema"]["additionalProperties"] is False
        assert set(spec["schema"]["required"]) == set(schema.model_fields)
        return httpx.Response(200, json=reply(text_output(raw)))

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        model = config.build_chat_model("small", http_client=client, max_retries=0)
        response = config.bind_structured_model(model, schema).invoke(
            [{"role": "user", "content": "JSON 응답"}]
        )
    assert schema.model_validate_json(config.response_text(response)) == outputs[schema]


def test_initial_schema_and_tool_roundtrip_use_responses_without_provider_options(
    monkeypatch,
):
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: config.Settings(
            "fake-key",
            "https://api.openai.com/v1",
            "gpt-6.1-sol",
            "gpt-6.1-sol",
            "gpt-6.1-sol",
        ),
    )
    calls = []
    responses = iter(
        [
            reply(text_output('{"plan": "ok"}')),
            reply(
                [
                    {
                        "id": "fc_test",
                        "type": "function_call",
                        "call_id": "call_test",
                        "name": "search",
                        "arguments": '{"query_id":"query-1"}',
                        "status": "completed",
                    }
                ]
            ),
            reply(text_output("done")),
        ]
    )

    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        assert request.url.path == "/v1/responses"
        assert "provider" not in body
        return httpx.Response(200, json=next(responses))

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        model = config.build_chat_model("small", http_client=client, max_retries=0)
        initial = bind_initial_research_model(model).invoke(
            [{"role": "user", "content": "JSON plan"}]
        )
        assert config.response_text(initial) == '{"plan": "ok"}'
        assert calls[0]["text"]["format"]["type"] == "json_schema"
        assert calls[0]["text"]["format"]["strict"] is True
        tools = model.bind_tools(TOOLS)
        messages = [{"role": "user", "content": "Search for chat"}]
        first = tools.invoke(messages)
        assert first.tool_calls[0]["args"] == {"query_id": "query-1"}
        messages.extend(
            [
                convert_to_openai_messages(first),
                {"role": "tool", "tool_call_id": "call_test", "content": "[]"},
            ]
        )
        final = tools.invoke(messages)
        assert config.response_text(final) == "done"

    assert any(
        item["type"] == "function_call_output" and item["call_id"] == "call_test"
        for item in calls[2]["input"]
    )
    assert calls[1]["tools"][0]["type"] == "function"
