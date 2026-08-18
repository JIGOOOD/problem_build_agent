"""LangGraph pipeline.

Nodes == sub agents. The repair cycle is a graph edge, not a hand-rolled loop:

    research -> problem -> rubric -> harness --(errors, budget left)--> repair -+
                                        |                                      |
                                        +---(passed OR budget exhausted)--> finalize -> END
                                        ^______________________________________|
                                                    (repair loops back to harness)

State carries a live reference to the mutable :class:`Session` plus a couple of
scalars the router needs. Nodes mutate `session` in place (same pattern as the
pre-LangGraph orchestrator) and return it back under the `session` key —
overwrite-on-same-object, so no custom reducer is needed.
"""

from __future__ import annotations

from typing import Awaitable, Callable, TypedDict

from langgraph.graph import END, StateGraph

from ..agents.authors import (
    ApiAgent,
    ArchitectureAgent,
    EntityAgent,
    NfrAgent,
    ProblemAuthorAgent,
    build_rubric,
)
from ..agents.support import JudgeAgent, ResearchAgent, SolutionAgent
from ..harness import (
    Finding,
    HarnessContext,
    HarnessRunner,
    RepairTarget,
    Stage,
)
from ..llm.client import LLM
from ..render.renderer import render_rubric
from .difficulty import calibrate
from .session import Session

EventFn = Callable[[str, str, dict | None], Awaitable[None]]  # kind, message, payload


class GraphState(TypedDict, total=False):
    session: Session
    passed: bool


class GraphConfig(TypedDict):
    research: bool
    write_solution: bool
    max_attempts: int
    disabled_harnesses: frozenset[str]


def build_graph(llm: LLM, cfg: GraphConfig, emit: EventFn, runner: HarnessRunner):
    """Compiles a fresh graph bound to one `emit` callback (cheap; no heavy state)."""

    async def node_research(state: GraphState) -> GraphState:
        session = state["session"]
        if cfg["research"]:
            await emit("phase", "자료 탐색 중", None)
            session.evidence = await ResearchAgent(llm).run(session.slots)
        return {"session": session}

    async def node_problem(state: GraphState) -> GraphState:
        session = state["session"]
        await emit("phase", "문제 초안 작성 중", None)
        session.problem = await ProblemAuthorAgent(llm).run(
            session.slots, session.evidence
        )
        return {"session": session}

    async def node_rubric(state: GraphState) -> GraphState:
        session = state["session"]
        assert session.problem
        await emit("phase", "루브릭 4개 섹션 병렬 생성 중", None)
        session.rubric = await build_rubric(
            llm, session.slots, session.problem, session.evidence
        )
        return {"session": session}

    async def node_harness(state: GraphState) -> GraphState:
        session = state["session"]
        assert session.problem and session.rubric
        session.attempts = max(session.attempts, len(session.reports))
        await emit("phase", f"하네스 검증 (시도 {session.attempts + 1})", None)

        ctx = HarnessContext(
            slots=session.slots,
            problem=session.problem,
            rubric=session.rubric,
            attempt=session.attempts,
        )
        report = await runner.run(Stage.PRE_RENDER, ctx)

        markdown = render_rubric(session.problem_id, session.problem, session.rubric)
        session.markdown = markdown
        ctx.rendered_markdown = markdown
        post = await runner.run(Stage.POST_RENDER, ctx)
        report.findings.extend(post.findings)

        budget_left = session.attempts < cfg["max_attempts"]
        if budget_left:
            _, judge_findings = await JudgeAgent(llm).run(session.problem, markdown)
            report.findings.extend(judge_findings)

        session.reports.append(report)
        for finding in report.findings:
            await emit("finding", finding.message, finding.as_dict())

        if report.passed:
            await emit("progress", "검증 통과", None)
        elif not budget_left:
            await emit(
                "progress",
                f"재시도 한도 도달 — 미해결 {len(report.errors)}건과 함께 진행",
                None,
            )
        return {"session": session, "passed": report.passed}

    async def node_repair(state: GraphState) -> GraphState:
        session = state["session"]
        assert session.problem and session.rubric
        report = session.reports[-1]
        plan = report.repair_plan()
        await emit("progress", f"재생성 대상: {', '.join(t.value for t in plan)}", None)

        if RepairTarget.PROBLEM in plan:
            session.problem = await ProblemAuthorAgent(llm).run(
                session.slots, session.evidence, plan[RepairTarget.PROBLEM]
            )

        agent_map = {
            RepairTarget.NFR: (NfrAgent, "non_functional_requirements"),
            RepairTarget.API: (ApiAgent, "api_endpoints"),
            RepairTarget.ENTITY: (EntityAgent, "core_entities"),
            RepairTarget.ARCHITECTURE: (ArchitectureAgent, "architecture"),
        }

        async def fix(target: RepairTarget) -> None:
            cls, attr = agent_map[target]
            agent = cls(llm)
            findings: list[Finding] = plan[target]
            payload = await agent.payload(
                session.slots, session.problem, session.evidence, findings
            )
            value = payload.items if hasattr(payload, "items") else payload
            setattr(session.rubric, attr, value)
            section = await agent.section(session.slots, session.problem, payload, findings)
            session.rubric.sections = [
                section if s.key == agent.key else s for s in session.rubric.sections
            ]

        import asyncio

        targets = [t for t in agent_map if t in plan]
        if targets:
            await asyncio.gather(*(fix(t) for t in targets))

        if RepairTarget.SECTIONS in plan:
            await emit("progress", "평가 기준 재작성 중", None)
            session.rubric = await build_rubric(
                llm, session.slots, session.problem, session.evidence
            )

        session.attempts += 1
        return {"session": session}

    async def node_finalize(state: GraphState) -> GraphState:
        session = state["session"]
        assert session.problem and session.rubric
        session.problem.difficulty = calibrate(session.rubric)
        session.markdown = render_rubric(session.problem_id, session.problem, session.rubric)

        if cfg["write_solution"]:
            await emit("phase", "해답지 작성 중", None)
            session.solution = await SolutionAgent(llm).run(
                session.problem, session.rubric, session.markdown
            )
        return {"session": session}

    def route_after_harness(state: GraphState) -> str:
        session = state["session"]
        if state.get("passed") or session.attempts >= cfg["max_attempts"]:
            return "finalize"
        return "repair"

    graph = StateGraph(GraphState)
    graph.add_node("research", node_research)
    graph.add_node("problem", node_problem)
    graph.add_node("rubric", node_rubric)
    graph.add_node("harness", node_harness)
    graph.add_node("repair", node_repair)
    graph.add_node("finalize", node_finalize)

    graph.set_entry_point("research")
    graph.add_edge("research", "problem")
    graph.add_edge("problem", "rubric")
    graph.add_edge("rubric", "harness")
    graph.add_conditional_edges(
        "harness", route_after_harness, {"repair": "repair", "finalize": "finalize"}
    )
    graph.add_edge("repair", "harness")
    graph.add_edge("finalize", END)

    return graph.compile()
