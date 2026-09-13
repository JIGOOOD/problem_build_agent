"""Runtime configuration loaded from the environment (and a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv

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
