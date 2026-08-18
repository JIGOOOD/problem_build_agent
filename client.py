"""LangChain-based LLM layer.

Every call is a small LCEL chain: ``ChatPromptTemplate | model``. Structured
output goes through ``with_structured_output`` (function-calling under the
hood), so agent code never touches JSON parsing directly. Retry/backoff is
LangChain's built-in ``.with_retry()`` rather than a hand-rolled decorator.
"""

from __future__ import annotations

import os
from typing import Type, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

RETRY_ATTEMPTS = 3


class LLM:
    """One instance per process. `large` for authoring, `small` for interview
    turns / research. Both are lazily built and cached per (model, temperature)."""

    def __init__(
        self,
        api_key: str | None = None,
        large: str | None = None,
        small: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ["OPENAI_API_KEY"]
        self.large = large or os.getenv("ARCHGEN_MODEL_LARGE", "gpt-4.1")
        self.small = small or os.getenv("ARCHGEN_MODEL_SMALL", "gpt-4.1-mini")
        self._chat_cache: dict[tuple[str, float], ChatOpenAI] = {}

    def _chat(self, *, big: bool, temperature: float) -> ChatOpenAI:
        model = self.large if big else self.small
        key = (model, temperature)
        if key not in self._chat_cache:
            self._chat_cache[key] = ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.api_key,
            ).with_retry(stop_after_attempt=RETRY_ATTEMPTS)
        return self._chat_cache[key]

    async def parse(
        self,
        schema: Type[T],
        system: str,
        user: str,
        *,
        big: bool = True,
        temperature: float = 0.2,
    ) -> T:
        """Structured-output call. `schema` must be a pydantic BaseModel."""
        chat = self._chat(big=big, temperature=temperature)
        structured = chat.with_structured_output(schema)
        prompt = ChatPromptTemplate.from_messages(
            [SystemMessage(content=system), HumanMessage(content=user)]
        )
        chain: Runnable = prompt | structured
        result = await chain.ainvoke({})
        if not isinstance(result, schema):
            raise RuntimeError(f"structured output refused for {schema.__name__}")
        return result

    async def text(self, system: str, user: str, *, big: bool = True) -> str:
        chat = self._chat(big=big, temperature=0.3)
        prompt = ChatPromptTemplate.from_messages(
            [SystemMessage(content=system), HumanMessage(content=user)]
        )
        chain: Runnable = prompt | chat | StrOutputParser()
        return await chain.ainvoke({})
