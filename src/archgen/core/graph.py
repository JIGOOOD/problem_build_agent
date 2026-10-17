"""조사 결과를 재사용하는 NFR 생성·검증 LangGraph."""

from __future__ import annotations

import json
import logging
import operator
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.nfr import NFRExport
from archgen.domain.research import ResearchResult
from archgen.export.agent import SelectionResult, generate_rubric, select_nfrs
from archgen.harness.checks import (
    check_criteria_count,
    check_cross_ref,
    check_levels,
    check_weight_sum,
)
from archgen.harness.findings import Finding, Severity
from archgen.harness.runner import Runner
from archgen.judge.judge import judge_export
from archgen.render.post_render import check_rendered
from archgen.render.renderer import render_rubric

_LOGGER = logging.getLogger(__name__)


class GenerationState(TypedDict, total=False):
    brief: InterviewBrief
    research: ResearchResult
    selection: SelectionResult
    export: NFRExport
    findings: list[Finding]
    repairs: int
    markdown: str
    phase: str
    status: str
    reason: str | None
    output_dir: str
    events: Annotated[list[str], operator.add]


def new_thread_config() -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": str(uuid4())}}


def build_generation_graph(
    *,
    research: Callable[[InterviewBrief], ResearchResult],
    llm: Callable[[list[dict[str, str]]], str],
    count_tokens: Callable[[list[dict[str, str]]], int],
    catalog: NFRCatalog,
    output_dir: Path,
    selection_llm: Callable[[list[dict[str, str]]], str] | None = None,
    judge_llm: Callable[[list[dict[str, str]]], str] | None = None,
    on_progress: Callable[[str], None] | None = None,
):
    """외부 호출은 주입하고 실행마다 별도 출력 디렉터리를 사용한다."""
    output_dir = Path(output_dir)

    def progress(message):
        if on_progress is not None:
            on_progress(message)

    def save(name, value):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def event(phase, message):
        _LOGGER.info("%s: %s", phase, message)
        return {"phase": phase, "events": [f"{phase}: {message}"]}

    def intake(state):
        if not isinstance(state.get("brief"), InterviewBrief):
            raise TypeError("InterviewBrief 입력이 필요하다.")
        save("input.json", asdict(state["brief"]))
        return {**event("intake", "brief accepted"), "repairs": 0, "findings": []}

    def investigate(state):
        progress("자료 조사 중")
        result = research(state["brief"])
        save("research.json", result.model_dump(mode="json"))
        return {**event("research", "completed"), "research": result}

    def author(state):
        progress("NFR 선정 중")
        selection = select_nfrs(
            state["brief"],
            state["research"],
            selection_llm if selection_llm is not None else llm,
            catalog=catalog,
            count_tokens=count_tokens,
        )
        save(
            "selection.json",
            {
                "status": selection.status,
                "selection": selection.selection.model_dump(mode="json"),
                "reason": selection.reason,
            },
        )
        update = {**event("author", selection.status), "selection": selection}
        if selection.status != "selected":
            return {**update, "status": selection.status, "reason": selection.reason}
        progress("평가 기준 작성 중")
        export = generate_rubric(
            state["brief"],
            state["research"],
            selection.selection,
            llm,
            count_tokens=count_tokens,
        )
        save("nfr_export-0.json", export.model_dump(mode="json"))
        return {**update, "export": export}

    def finalize(state):
        progress("결과 저장 중")
        status = state.get("status") or (
            "failed" if has_errors(state["findings"]) else "complete"
        )
        update = {
            **event("finalize", status),
            "status": status,
            "output_dir": str(output_dir),
        }
        save("findings.json", [f.model_dump(mode="json") for f in state["findings"]])
        save(
            "status.json",
            {
                "status": status,
                "reason": state.get("reason"),
                "repairs": state["repairs"],
                "judge_enabled": judge_llm is not None,
                "events": [*state["events"], *update["events"]],
            },
        )
        if "export" in state:
            save("nfr_export.json", state["export"].model_dump(mode="json"))
        if status == "complete":
            (output_dir / "nfr_rubric.md").write_text(state["markdown"], encoding="utf-8")
        return update

    def has_errors(findings):
        return any(f.severity == Severity.ERROR for f in findings)

    def validate(state):
        progress("기본 검증 중")
        findings = Runner(
            [
                check_weight_sum,
                check_criteria_count,
                check_levels,
                check_cross_ref({doc.id for doc in state["research"].documents}),
            ]
        ).run(state["export"])
        save(
            f"pre-findings-{state['repairs']}.json",
            [f.model_dump(mode="json") for f in findings],
        )
        return {**event("validate", f"{len(findings)} findings"), "findings": findings}

    def render(state):
        progress("채점표 작성 중")
        markdown = render_rubric(state["export"], state["brief"])
        findings = check_rendered(markdown, state["export"], state["brief"])
        save(
            f"post-findings-{state['repairs']}.json",
            [f.model_dump(mode="json") for f in findings],
        )
        return {
            **event("render", f"{len(findings)} findings"),
            "markdown": markdown,
            "findings": [*state["findings"], *findings],
        }

    def judge(state):
        if judge_llm is None:
            return event("judge", "disabled: actual validation pending")
        progress("평가 기준 검토 중")
        findings = judge_export(
            state["brief"], state["research"], state["export"], judge_llm
        )
        save(
            f"judge-findings-{state['repairs']}.json",
            [f.model_dump(mode="json") for f in findings],
        )
        return {
            **event("judge", f"{len(findings)} findings"),
            "findings": [*state["findings"], *findings],
        }

    def repair_route(state):
        if has_errors(state["findings"]) and state["repairs"] < 2:
            return "repair"
        return "finalize"

    def repair(state):
        attempt = state["repairs"] + 1
        progress(f"평가 기준 보완 중 ({attempt}/2)")
        export = generate_rubric(
            state["brief"],
            state["research"],
            state["selection"].selection,
            llm,
            count_tokens=count_tokens,
            previous=state["export"],
            findings=state["findings"],
        )
        save(f"nfr_export-{attempt}.json", export.model_dump(mode="json"))
        return {**event("repair", f"{attempt}/2"), "export": export, "repairs": attempt}

    workflow = StateGraph(GenerationState)
    for name, node in [
        ("intake", intake),
        ("research", investigate),
        ("author", author),
        ("validate", validate),
        ("render", render),
        ("judge", judge),
        ("repair", repair),
        ("finalize", finalize),
    ]:
        workflow.add_node(name, node)
    workflow.add_edge(START, "intake")
    workflow.add_edge("intake", "research")
    workflow.add_edge("research", "author")
    workflow.add_conditional_edges(
        "author", lambda state: "validate" if "export" in state else "finalize"
    )
    workflow.add_conditional_edges(
        "validate",
        lambda state: repair_route(state) if has_errors(state["findings"]) else "render",
    )
    workflow.add_conditional_edges(
        "render", lambda state: "finalize" if has_errors(state["findings"]) else "judge"
    )
    workflow.add_conditional_edges("judge", repair_route)
    workflow.add_edge("repair", "validate")
    workflow.add_edge("finalize", END)
    return workflow.compile(checkpointer=InMemorySaver())
