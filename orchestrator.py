"""Main orchestrator — thin wrapper around the LangGraph pipeline in `graph.py`.

Public contract is unchanged from the pre-LangGraph version so the TUI needs no
changes: `Orchestrator(llm, ...).generate(session)` is an async generator of
`Event`. Internally, that pipeline is now a compiled `StateGraph`.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from ..harness import HarnessRunner, discover
from ..llm.client import LLM
from .graph import GraphConfig, build_graph
from .session import Session

MAX_REPAIR_ATTEMPTS = 2


@dataclass(slots=True)
class Event:
    kind: str  # phase | progress | finding | done | error
    message: str
    payload: dict | None = None


class Orchestrator:
    def __init__(
        self,
        llm: LLM,
        *,
        research: bool = True,
        write_solution: bool = True,
        disabled_harnesses: frozenset[str] = frozenset(),
        max_attempts: int = MAX_REPAIR_ATTEMPTS,
    ) -> None:
        self.llm = llm
        self.cfg: GraphConfig = {
            "research": research,
            "write_solution": write_solution,
            "max_attempts": max_attempts,
            "disabled_harnesses": disabled_harnesses,
        }
        self.runner = HarnessRunner(disabled=disabled_harnesses)
        discover()

    async def generate(self, session: Session):
        """Runs the graph end-to-end, yielding progress events as it goes."""
        queue: asyncio.Queue[Event | None] = asyncio.Queue()

        async def emit(kind: str, message: str, payload: dict | None) -> None:
            await queue.put(Event(kind, message, payload))

        graph = build_graph(self.llm, self.cfg, emit, self.runner)

        async def run() -> None:
            try:
                await graph.ainvoke({"session": session, "passed": False})
                await emit("done", "생성 완료", None)
            except Exception as exc:
                await emit("error", f"{type(exc).__name__}: {exc}", None)
                raise

        task = asyncio.create_task(run())
        task.add_done_callback(lambda _: queue.put_nowait(None))

        while True:
            event = await queue.get()
            if event is None:
                break
            yield event
        await task
