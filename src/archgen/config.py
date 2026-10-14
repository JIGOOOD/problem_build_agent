"""Runtime configuration loaded from the environment (and a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from dotenv import load_dotenv

Tier = Literal["large", "small"]


@dataclass(frozen=True)
class Settings:
    """Credentials and model choices for the OpenAI-compatible agents."""

    api_key: str
    base_url: str
    model_large: str
    model_small: str

    def model_for(self, tier: Tier) -> str:
        """Return the model name for a tier, rejecting unknown tiers loudly."""
        if tier == "large":
            return self.model_large
        if tier == "small":
            return self.model_small
        raise ValueError(f"Unknown model tier: {tier!r}")


REQUIRED_VARS = (
    "OPENROUTER_API_KEY",
    "OPENROUTER_BASE_URL",
    "ARCHGEN_MODEL_LARGE",
    "ARCHGEN_MODEL_SMALL",
)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read settings once per process, failing loudly when anything is missing."""
    load_dotenv()
    values = {name: os.getenv(name, "").strip() for name in REQUIRED_VARS}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in every entry."
        )
    return Settings(
        api_key=values["OPENROUTER_API_KEY"],
        base_url=values["OPENROUTER_BASE_URL"],
        model_large=values["ARCHGEN_MODEL_LARGE"],
        model_small=values["ARCHGEN_MODEL_SMALL"],
    )


def build_chat_model(tier: Tier = "large", *, model_class=None, **overrides):
    """공식 OpenAI는 Responses, OpenRouter는 Chat Completions를 사용한다."""
    from langchain_openai import ChatOpenAI

    settings = get_settings()
    host = urlparse(settings.base_url).hostname
    overrides.setdefault("use_responses_api", host == "api.openai.com")
    if host == "api.openai.com":
        overrides.setdefault("output_version", "v0")
    elif host == "openrouter.ai":
        overrides.setdefault("extra_body", {"provider": {"require_parameters": True}})
    return (model_class or ChatOpenAI)(
        model=overrides.pop("model", settings.model_for(tier)),
        api_key=settings.api_key,
        base_url=settings.base_url,
        **overrides,
    )


def response_text(message) -> str:
    """문자열 또는 Responses의 텍스트 블록만 허용한다."""
    content = message.content
    if isinstance(content, str):
        return content
    if (
        isinstance(content, list)
        and content
        and all(
            isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
            for block in content
        )
    ):
        return "".join(block["text"] for block in content)
    raise TypeError("LLM 응답은 텍스트 문자열 또는 텍스트 블록이어야 한다.")
