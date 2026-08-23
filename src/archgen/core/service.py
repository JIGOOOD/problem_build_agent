"""Application-facing facade over the LangGraph generation workflow."""

from __future__ import annotations

from .graph import GenerationState, build_generation_graph, new_thread_config


class GenerationService:
    """Start isolated generation threads without exposing graph details to the UI."""

    def __init__(self) -> None:
        self.graph = build_generation_graph()

    async def start(self, brief: list[str]) -> GenerationState:
        result = await self.graph.ainvoke(
            {"brief": brief, "events": []}, config=new_thread_config()
        )
        return result
