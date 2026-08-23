"""Baseline LangGraph workflow for an ArchGen generation run.

The nodes deliberately contain no LLM calls yet. They establish the state and
execution contract that future research, authoring, validation, and rendering
agents will implement.
"""

from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

Phase = Literal["intake", "research", "author", "validate", "finalize"]


class GenerationState(TypedDict, total=False):
    """State shared by every node in one generation thread."""

    brief: list[str]
    phase: Phase
    status: str
    events: Annotated[list[str], operator.add]


def new_thread_config() -> dict[str, dict[str, str]]:
    """Return an isolated LangGraph thread configuration for one TUI run."""
    return {"configurable": {"thread_id": str(uuid4())}}


def build_generation_graph():
    """Compile the initial workflow with in-process, thread-scoped checkpoints."""
    workflow = StateGraph(GenerationState)
    workflow.add_node("intake", _intake)
    workflow.add_node("research", _research)
    workflow.add_node("author", _author)
    workflow.add_node("validate", _validate)
    workflow.add_node("finalize", _finalize)

    workflow.add_edge(START, "intake")
    workflow.add_edge("intake", "research")
    workflow.add_edge("research", "author")
    workflow.add_edge("author", "validate")
    workflow.add_edge("validate", "finalize")
    workflow.add_edge("finalize", END)
    return workflow.compile(checkpointer=InMemorySaver())


def _intake(state: GenerationState) -> GenerationState:
    if not state.get("brief"):
        raise ValueError("A generation run needs at least one brief entry.")
    return {"phase": "intake", "events": ["intake: brief accepted"]}


def _research(_: GenerationState) -> GenerationState:
    return {"phase": "research", "events": ["research: agent not configured"]}


def _author(_: GenerationState) -> GenerationState:
    return {"phase": "author", "events": ["author: agent not configured"]}


def _validate(_: GenerationState) -> GenerationState:
    return {"phase": "validate", "events": ["validate: harness not configured"]}


def _finalize(_: GenerationState) -> GenerationState:
    return {
        "phase": "finalize",
        "status": "ready_for_agents",
        "events": ["finalize: workflow scaffold completed"],
    }
