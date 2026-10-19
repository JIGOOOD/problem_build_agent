"""연차를 받은 뒤 Agent와 범위를 정하고 생성하는 터미널 UI."""

from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import ClassVar

from rich.markup import escape
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Footer, Header, Input, LoadingIndicator, Static

from ..core.service import GenerationService
from ..intake.agent import ScopeDecision, ScopeDraft, assess_scope
from .slots import SlotFiller

READY_HINT = "Ctrl+G를 눌러 생성을 시작하세요."
LOG_PATH = Path(os.environ.get("ARCHGEN_LOG", ".archgen/input.log"))


class GenerationProgress(Message):
    def __init__(self, phase: str) -> None:
        super().__init__()
        self.phase = phase


class ArchGenApp(App[None]):
    """사용자가 범위 초안을 확인한 뒤 생성한다."""

    TITLE = "ArchGen"
    SUB_TITLE = "System-design interview generator"
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+g", "generate", "Generate", key_display="Ctrl+G"),
        Binding("ctrl+q", "quit", "Quit", key_display="Ctrl+Q"),
    ]

    CSS = """
    #loading { height: 1; }
    #progress {
        height: auto;
        margin: 1 2;
        padding: 1 2;
        border: round $primary;
    }
    #progress.running {
        border: heavy $warning;
        background: $warning 15%;
        color: $text;
    }
    #transcript {
        height: auto;
        padding: 1 2;
    }

    #input_area {
        dock: bottom;
        height: auto;
        margin: 0 1 1 1;
    }
    #input_context {
        height: auto;
        max-height: 12;
        overflow-y: auto;
        border-top: solid $accent;
        padding: 1 1 0 1;
        margin-bottom: 1;
    }
    """

    def __init__(self, log_path: Path | None = None, *, fake: bool = False) -> None:
        super().__init__()
        self.filler = SlotFiller()
        self.generation = GenerationService(fake=fake)
        self._fake = fake
        self._scope_history: list[dict[str, str]] = []
        self._draft: ScopeDraft | None = None
        self._confirmed = False
        self._assessing = False
        self._scope_error: str | None = None
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
        with Vertical(id="input_area"):
            yield Static(id="input_context")
            yield Input(id="brief")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#progress").display = False
        self.query_one("#loading").display = False
        self._render_transcript()
        self.query_one("#brief", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._assessing or self._generating or self._confirmed:
            return
        slot = self.filler.current
        raw = event.value
        if self.filler.is_complete:
            event.input.value = ""
            if self._draft is not None and raw.strip().lower() == "y":
                self._confirmed = True
                self._trace(f"범위 확정: {self._draft.model_dump_json()}")
                self._render_transcript()
                return
            if not raw.strip() and self._scope_error is None:
                self._render_transcript(error="답변 또는 수정 내용을 입력해 주세요.")
                return
            if raw.strip():
                self._scope_history.append({"role": "user", "content": raw.strip()})
                self._trace(f"범위 답변: {raw.strip()}")
            self._begin_scope_assessment()
            return
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
                self._trace(f"연차 입력 완료 {self.filler.values['seniority']}")
                question = "어떤 주제로 연습하고 싶으세요?"
                self._scope_history.append(
                    {
                        "role": "assistant",
                        "content": json.dumps({"question": question}, ensure_ascii=False),
                    }
                )
                self._trace(f"주제 질문: {question}")

        self._render_transcript(error=result.error)

    def _begin_scope_assessment(self) -> None:
        self._draft = None
        self._confirmed = False
        self._scope_error = None
        self._assessing = True
        self._render_transcript()
        self.query_one("#loading").display = True
        self.run_worker(self._assess_scope(), group="scope", exclusive=True)

    async def _assess_scope(self) -> None:
        seniority = self.filler.values["seniority"]
        try:
            if self._fake:
                answers = [
                    m["content"] for m in self._scope_history if m["role"] == "user"
                ]
                judgment = {
                    "applies": not answers,
                    "reason": "고정 채팅 예시의 범위를 확인한다.",
                }
                decision = ScopeDecision(
                    multiple_domains=judgment,
                    unclear_core_function=judgment,
                    nfr_depends_on_scope=judgment,
                    question=None if answers else "어떤 서비스를 설계할까요?",
                    draft=ScopeDraft(
                        title="실시간 채팅 시스템",
                        scope=answers[-1],
                        focus="고정 채팅 예시의 평가 기준",
                    )
                    if answers
                    else None,
                )
            else:
                decision = await asyncio.to_thread(
                    assess_scope, seniority, history=list(self._scope_history)
                )
            self._scope_history.append(
                {"role": "assistant", "content": decision.model_dump_json()}
            )
            self._draft = decision.draft
            self._trace(f"범위 판단: {decision.model_dump_json()}")
        except Exception as error:  # noqa: BLE001 — 대화를 유지하고 재시도를 허용한다.
            self._scope_error = str(error)
            self._trace(f"범위 판단 실패: {error}")
            self.notify(f"범위 판단 실패: {error}", severity="error")
        finally:
            self._assessing = False
            self.query_one("#loading").display = False
            self._render_transcript()
            self.query_one("#brief", Input).focus()

    def action_generate(self) -> None:
        if self._generating or self._assessing:
            return
        if not self.filler.is_complete:
            self.notify(
                f"{self.filler.current.label} 항목이 아직 남았습니다.", severity="warning"
            )
            return
        if self._draft is None:
            self.notify("범위 질문에 답하고 초안을 확인해 주세요.", severity="warning")
            return
        if not self._confirmed:
            self.notify("초안을 확인한 뒤 y를 입력해 주세요.", severity="warning")
            return
        self._generating = True
        self._phase = "생성 준비 중"
        self._started_at = monotonic()
        self.query_one("#progress").display = True
        self.query_one("#loading").display = True
        self._refresh_progress()
        self.query_one("#brief", Input).disabled = True
        self.run_worker(self._start_generation(), exclusive=True)

    async def _start_generation(self) -> None:
        brief = self.filler.build_brief(
            self._draft.title, self._draft.scope, self._draft.focus
        )
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
            self.query_one("#brief", Input).disabled = False
        self.notify(f"생성 결과: {result['status']}")
        self._trace(f"생성 결과: {result['status']} | 저장 위치: {result['output_dir']}")
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
        progress = self.query_one("#progress", Static)
        progress.set_class(self._generating, "running")
        progress.update(
            f"[b]● 생성 진행 중[/b]\n\n{escape(self._phase)}\n경과 {elapsed}초"
            if self._generating
            else f"{escape(self._phase)} · 경과 {elapsed}초"
        )
        self.query_one("#input_area").display = not self._generating
        self.query_one("#transcript").styles.opacity = 0.5 if self._generating else 1.0

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
        agent_block = ""
        current = []
        lines = [
            f"[b]인터뷰 브리프[/b] ({len(self.filler.filled)}/{len(self.filler.slots)})"
        ]
        lines += [f"• {label}: {escape(value)}" for label, value in self.filler.filled]
        lines.append("")
        if error:
            lines.append(f"[b red]{escape(error)}[/b red]")
        if slot:
            current = [slot.prompt]
        else:
            for message in self._scope_history:
                if message["role"] == "user":
                    body = escape(message["content"]).replace("\n", "\n  ")
                    lines += [f"[b green]나[/b green]\n  {body}", ""]
                else:
                    question = json.loads(message["content"])["question"]
                    if question:
                        body = re.sub(r"\s*([①-⑩])", r"\n\1", question).strip()
                        body = escape(body).replace("\n", "\n  ")
                        agent_block = f"[b cyan]Agent[/b cyan]\n  {body}"
                        lines += [agent_block, ""]
            if self._assessing:
                current = ["응답을 준비하고 있습니다…"]
            elif self._scope_error:
                current = [
                    f"범위 판단 실패: {escape(self._scope_error)}\nEnter로 다시 시도하세요."
                ]
            elif self._draft is not None:
                current = [
                    "[b cyan]범위 초안[/b cyan]",
                    "",
                    f"[b]{escape(self._draft.title)}[/b]",
                    "",
                    "[b]설계 범위[/b]",
                    escape(self._draft.scope),
                    "",
                    "[b]평가 초점[/b]",
                    escape(self._draft.focus),
                    "",
                    f"[dim]{READY_HINT}[/dim]" if self._confirmed else "",
                ]

        lines += current
        self.query_one("#transcript", Static).update("\n".join(lines))
        context = current or ([agent_block] if agent_block else [])
        if error:
            context = [f"[b red]{escape(error)}[/b red]", *context]
        self.query_one("#input_context", Static).update("\n".join(context))
        brief_input = self.query_one("#brief", Input)
        brief_input.placeholder = (
            slot.placeholder
            if slot
            else "이 주제로 진행하려면 y, 수정하려면 요구사항을 입력하세요."
            if self._draft is not None
            else "답변을 입력하세요."
        )
        brief_input.display = not self._confirmed
        brief_input.disabled = self._assessing or self._generating or self._confirmed
