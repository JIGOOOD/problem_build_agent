from unittest.mock import Mock

import pytest

from archgen import config


def test_reasoning_effort_follows_role_environment_and_allows_override(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    for name in config.REQUIRED_VARS:
        monkeypatch.setenv(name, "test-value")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("ARCHGEN_REASONING_EFFORT_MEDIUM", "low")
    monkeypatch.setenv("ARCHGEN_REASONING_EFFORT_LARGE", "medium")
    config.get_settings.cache_clear()
    try:
        factory = Mock()
        for tier, effort in (("medium", "low"), ("large", "medium")):
            config.build_chat_model(tier, model_class=factory)
            assert factory.call_args.kwargs["reasoning_effort"] == effort
        config.build_chat_model("large", model_class=factory, reasoning_effort="high")
        assert factory.call_args.kwargs["reasoning_effort"] == "high"
        config.build_chat_model("small", model_class=factory)
        assert "reasoning_effort" not in factory.call_args.kwargs
    finally:
        config.get_settings.cache_clear()


@pytest.mark.parametrize(
    "base_url,responses",
    [("https://api.openai.com/v1", True), ("https://openrouter.ai/api/v1", False)],
)
def test_model_factory_routes_provider_options(monkeypatch, base_url, responses):
    settings = config.Settings(
        "fake-key", base_url, "large-model", "medium-model", "small-model"
    )
    monkeypatch.setattr(config, "get_settings", lambda: settings)
    factory = Mock()

    for tier in ("small", "medium", "large"):
        config.build_chat_model(tier, model_class=factory)
        assert factory.call_args.kwargs["model"] == f"{tier}-model"

    options = factory.call_args.kwargs
    assert options["use_responses_api"] is responses
    if responses:
        assert options["output_version"] == "v0"
        assert "extra_body" not in options
    else:
        assert options["extra_body"] == {"provider": {"require_parameters": True}}


@pytest.mark.parametrize(
    "content,expected",
    [
        ("OK", "OK"),
        (
            [{"type": "text", "text": "first"}, {"type": "text", "text": "second"}],
            "firstsecond",
        ),
    ],
)
def test_response_text_accepts_strings_and_responses_text_blocks(content, expected):
    from langchain_core.messages import AIMessage

    assert config.response_text(AIMessage(content=content)) == expected


@pytest.mark.parametrize(
    "content",
    [
        [{"type": "image_url", "image_url": {"url": "https://example.com/image"}}],
        [{"type": "text", "text": 3}],
        [],
    ],
)
def test_response_text_rejects_non_text_payloads(content):
    from langchain_core.messages import AIMessage

    with pytest.raises(TypeError, match="텍스트"):
        config.response_text(AIMessage(content=content))
