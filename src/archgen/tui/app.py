"""The terminal interface that fills the interview brief one slot at a time."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Footer, Header, Input, LoadingIndicator, Static

from ..core.service import GenerationService
from .slots import SlotFiller

READY_HINT = "모든 항목을 받았습니다. Ctrl+G 로 생성을 시작하세요."
LOG_PATH = Path(os.environ.get("ARCHGEN_LOG", ".archgen/input.log"))


class GenerationProgress(Message):
    def __init__(self, phase: str) -> None:
        super().__init__()
        self.phase = phase


class ArchGenApp(App[None]):
    """Ask for seniority, topic, and optional notes before generating."""

    TITLE = "ArchGen"
    SUB_TITLE = "System-design interview generator"
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+g", "generate", "Generate", key_display="Ctrl+G"),
        Binding("ctrl+q", "quit", "Quit", key_display="Ctrl+Q"),
    ]

    CSS = """
    #loading { height: 1; }
    #progress { height: auto; margin: 0 2; }
    #transcript {
        height: 1fr;
        padding: 1 2;
    }

    #brief {
        dock: bottom;
        margin: 0 1 1 1;
    }
    """

    def __init__(self, log_path: Path | None = None, *, fake: bool = False) -> None:
        super().__init__()
        self.filler = SlotFiller()
        self.generation = GenerationService(fake=fake)
        if fake:
            self.sub_title = "Fake 모드 · 고정 채팅 예시 · API 호출 없음"
        self.log_path = LOG_PATH if log_path is None else log_path
        self._generating = False
        self._phase = ""
        self._started_at = 0.0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="progress")
        yield LoadingIndicator(id="loading")
        with VerticalScroll():
            yield Static(id="transcript")
        yield Input(id="brief")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#progress").display = False
        self.query_one("#loading").display = False
        self._render_transcript()
        self.query_one("#brief", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        slot = self.filler.current
        raw = event.value
        result = self.filler.submit(raw)
        event.input.value = ""

        if not result.accepted:
            self.notify(result.error, severity="warning")
            self._trace(
                f"거절 {slot.label if slot else '-'} <- {raw!r} :: {result.error}"
            )
        else:
            stored = self.filler.values.get(slot.key)
            self._trace(f"저장 {slot.label} <- {raw!r} => {stored!r}")
            if self.filler.is_complete:
                self._trace(f"완료 {self.filler.build_brief()!r}")

        self._render_transcript(error=result.error)

    def action_generate(self) -> None:
        if self._generating:
            return
        if not self.filler.is_complete:
            self.notify(
                f"{self.filler.current.label} 항목이 아직 남았습니다.", severity="warning"
            )
            return
        self._generating = True
        self._phase = "생성 준비 중"
        self._started_at = monotonic()
        self.query_one("#progress").display = True
        self.query_one("#loading").display = True
        self._refresh_progress()
        self.run_worker(self._start_generation(), exclusive=True)

    async def _start_generation(self) -> None:
        brief = self.filler.build_brief()
        self._trace(f"생성 시작 {brief.to_lines()}")
        timer = self.set_interval(1, self._refresh_progress)
        try:
            result = await self.generation.start(brief, on_progress=self._report_progress)
            self._phase = "생성 완료" if result["status"] == "complete" else "생성 중단"
        except Exception as error:  # noqa: BLE001 — 생성 실패는 알림으로 표시하고 UI를 유지한다.
            self._phase = "생성 실패"
            self._trace(f"생성 실패: {error}")
            self.notify(f"생성 실패: {error}", severity="error")
            return
        finally:
            timer.stop()
            self._generating = False
            self.query_one("#loading").display = False
            self._refresh_progress()
        self.notify(f"생성 결과: {result['status']}")
        events = "\n".join(f"• {event}" for event in result["events"])
        self.query_one("#transcript", Static).update(
            f"[b]생성 결과: {result['status']}[/b]\n{events}\n{result['output_dir']}"
        )

    def _report_progress(self, phase: str) -> None:
        # 생성 스레드에서는 Textual 메시지를 통해 화면을 갱신한다.
        self.post_message(GenerationProgress(phase))

    def on_generation_progress(self, message: GenerationProgress) -> None:
        if self._generating:
            self._phase = message.phase
            self._refresh_progress()

    def _refresh_progress(self) -> None:
        elapsed = int(monotonic() - self._started_at)
        self.query_one("#progress", Static).update(f"{self._phase} · 경과 {elapsed}초")

    def _trace(self, message: str) -> None:
        """Append one line to the input log so answers can be inspected live."""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{datetime.now().astimezone():%H:%M:%S} {message}\n")
        except OSError:
            pass

    def _render_transcript(self, error: str | None = None) -> None:
        """Show the answers so far, then the current question (or the saved brief)."""
        slot = self.filler.current
        lines = [
            f"[b]인터뷰 브리프[/b] ({len(self.filler.filled)}/{len(self.filler.slots)})"
        ]
        lines += [f"• {label}: {value}" for label, value in self.filler.filled]
        lines.append("")
        if error:
            lines.append(f"[b red]{error}[/b red]")
        if slot:
            lines.append(slot.prompt)
        else:
            lines.append(READY_HINT)

        self.query_one("#transcript", Static).update("\n".join(lines))
        brief_input = self.query_one("#brief", Input)
        brief_input.placeholder = slot.placeholder if slot else ""
        brief_input.disabled = slot is None
