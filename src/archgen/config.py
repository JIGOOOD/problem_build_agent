"""Runtime configuration loaded from the environment (and a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL_LARGE = "anthropic/claude-sonnet-4.5"
DEFAULT_MODEL_SMALL = "anthropic/claude-haiku-4.5"

Tier = Literal["large", "small"]


@dataclass(frozen=True)
class Settings:
    """Credentials and model choices for the OpenRouter-backed agents."""

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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read settings once per process, failing loudly when the key is missing."""
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Settings(
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL),
        model_large=os.getenv("ARCHGEN_MODEL_LARGE", DEFAULT_MODEL_LARGE),
        model_small=os.getenv("ARCHGEN_MODEL_SMALL", DEFAULT_MODEL_SMALL),
    )


def build_chat_model(tier: Tier = "large", **overrides):
    """Return a ChatOpenAI client for one model tier, pointed at OpenRouter."""
    from langchain_openai import ChatOpenAI

    settings = get_settings()
    return ChatOpenAI(
        model=overrides.pop("model", settings.model_for(tier)),
        api_key=settings.api_key,
        base_url=settings.base_url,
        **overrides,
    )
