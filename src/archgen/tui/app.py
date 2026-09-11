"""The terminal interface that fills the interview brief one slot at a time."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from ..core.service import GenerationService
from .slots import SlotFiller

READY_HINT = "모든 항목을 받았습니다. Ctrl+G 로 생성을 시작하세요."
LOG_PATH = Path(os.environ.get("ARCHGEN_LOG", ".archgen/input.log"))


class ArchGenApp(App[None]):
    """Ask for seniority, topic, and optional notes before generating."""

    TITLE = "ArchGen"
    SUB_TITLE = "System-design interview generator"
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+g", "generate", "Generate", key_display="Ctrl+G"),
        Binding("ctrl+q", "quit", "Quit", key_display="Ctrl+Q"),
    ]

    CSS = """
    #transcript {
        height: 1fr;
        padding: 1 2;
    }

    #brief {
        dock: bottom;
        margin: 0 1 1 1;
    }
    """

    def __init__(self, log_path: Path | None = None) -> None:
        super().__init__()
        self.filler = SlotFiller()
        self.generation = GenerationService()
        self.log_path = LOG_PATH if log_path is None else log_path

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static(id="transcript")
        yield Input(id="brief")
        yield Footer()

    def on_mount(self) -> None:
        self._render_transcript()
        self.query_one("#brief", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        slot = self.filler.current
        raw = event.value
        result = self.filler.submit(raw)
        event.input.value = ""

        if not result.accepted:
            self.notify(result.error, severity="warning")
            self._trace(f"거절 {slot.label if slot else '-'} <- {raw!r} :: {result.error}")
        else:
            stored = self.filler.values.get(slot.key)
            self._trace(f"저장 {slot.label} <- {raw!r} => {stored!r}")
            if self.filler.is_complete:
                self._trace(f"완료 {self.filler.build_brief()!r}")

        self._render_transcript(error=result.error)

    def action_generate(self) -> None:
        if not self.filler.is_complete:
            self.notify(
                f"{self.filler.current.label} 항목이 아직 남았습니다.", severity="warning"
            )
            return
        self.run_worker(self._start_generation(), exclusive=True)

    async def _start_generation(self) -> None:
        brief = self.filler.build_brief()
        self._trace(f"생성 시작 {brief.to_lines()}")
        result = await self.generation.start(brief.to_lines())
        self.notify("LangGraph workflow completed: agents are not configured yet.")
        events = "\n".join(f"• {event}" for event in result["events"])
        self.query_one("#transcript", Static).update(
            f"[b]LangGraph workflow[/b]\n{events}"
        )

    def _trace(self, message: str) -> None:
        """Append one line to the input log so answers can be inspected live."""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{datetime.now():%H:%M:%S} {message}\n")
        except OSError:
            pass

    def _render_transcript(self, error: str | None = None) -> None:
        """Show the answers so far, then the current question (or the saved brief)."""
        slot = self.filler.current
        lines = [f"[b]인터뷰 브리프[/b] ({len(self.filler.filled)}/{len(self.filler.slots)})"]
        lines += [f"• {label}: {value}" for label, value in self.filler.filled]
        lines.append("")
        if error:
            lines.append(f"[b red]{error}[/b red]")
        if slot:
            lines.append(slot.prompt)
        else:
            lines.append("[b]저장된 브리프[/b]")
            lines += [f"  {line}" for line in self.filler.build_brief().to_lines()]
            lines.append(f"[dim]내부 값: {self.filler.values!r}[/dim]")
            lines.append("")
            lines.append(READY_HINT)

        self.query_one("#transcript", Static).update("\n".join(lines))
        brief_input = self.query_one("#brief", Input)
        brief_input.placeholder = slot.placeholder if slot else ""
        brief_input.disabled = slot is None
