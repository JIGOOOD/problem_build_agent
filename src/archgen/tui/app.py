"""The initial terminal interface for collecting an interview brief."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from ..core.service import GenerationService


class ArchGenApp(App[None]):
    """Collect a short problem brief before handing it to the future workflow."""

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

    def __init__(self) -> None:
        super().__init__()
        self.answers: list[str] = []
        self.generation = GenerationService()

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static(
                "[b]What system-design problem should we create?[/b]\n"
                "Describe the domain, constraints, or target seniority. "
                "Press Enter to add notes; Ctrl+G starts generation.",
                id="transcript",
            )
        yield Input(
            placeholder="e.g. Design a high-traffic ticketing service", id="brief"
        )
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        answer = event.value.strip()
        if not answer:
            return
        self.answers.append(answer)
        event.input.value = ""
        self._render_transcript()

    def action_generate(self) -> None:
        if not self.answers:
            self.notify("Add at least one brief before generating.", severity="warning")
            return
        self.run_worker(self._start_generation(), exclusive=True)

    async def _start_generation(self) -> None:
        result = await self.generation.start(self.answers)
        self.notify("LangGraph workflow completed: agents are not configured yet.")
        transcript = self.query_one("#transcript", Static)
        events = "\n".join(f"• {event}" for event in result["events"])
        transcript.update(f"[b]LangGraph workflow[/b]\n{events}")

    def _render_transcript(self) -> None:
        transcript = self.query_one("#transcript", Static)
        entries = "\n".join(f"• {answer}" for answer in self.answers)
        transcript.update(
            "[b]Interview brief[/b]\n"
            f"{entries}\n\n"
            "Add more context, or press Ctrl+G when the brief is ready."
        )
