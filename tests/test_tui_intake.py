import asyncio
import json
from threading import Event
from unittest.mock import AsyncMock, Mock

import pytest
from textual.widgets import Input, Static

from archgen.intake.agent import ScopeDecision
from archgen.tui.app import ArchGenApp


def decision(*, question=None, title="결제 처리 시스템", scope=None, focus=None):
    judgment = {"applies": True, "reason": "사용자가 정한 범위와 남은 결정을 확인한다."}
    return ScopeDecision(
        multiple_domains=judgment,
        unclear_core_function=judgment,
        nfr_depends_on_scope=judgment,
        question=question,
        draft={"title": title, "scope": scope, "focus": focus}
        if scope is not None
        else None,
    )


async def submit(pilot, text):
    pilot.app.query_one("#brief", Input).value = text
    await pilot.press("enter")
    await pilot.pause()


@pytest.mark.asyncio
async def test_tui_asks_refines_and_generates_only_after_user_confirmation(
    monkeypatch, tmp_path
):
    scope = "생성된 주문의 결제 요청부터 PG webhook 상태 반영까지. 환불·정산 제외."
    focus = "중복 결제 방지와 상태 일관성"
    assessor = Mock(
        side_effect=[
            decision(question="어디를 다룰까요? ① 주문 ② 결제 ③ 두 시스템의 연동"),
            decision(scope=scope, focus=focus),
        ]
    )
    monkeypatch.setattr("archgen.tui.app.assess_scope", assessor)
    app = ArchGenApp(log_path=tmp_path / "input.log")
    app.generation.start = AsyncMock(
        return_value={"status": "complete", "events": [], "output_dir": "/tmp/result"}
    )

    async with app.run_test() as pilot:
        await submit(pilot, "Middle")
        await submit(pilot, "주문/결제 시스템")
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert "어디를 다룰까요" in str(app.query_one("#transcript", Static).render())
        context = app.query_one("#input_context", Static)
        assert "어디를 다룰까요" in str(context.render())
        assert "\n  ① 주문\n  ② 결제\n  ③ 두 시스템의 연동" in str(context.render())
        assert context.region.bottom <= app.query_one("#brief", Input).region.y
        assert context.parent.styles.dock == "bottom"
        assert not app.query_one("#brief", Input).disabled
        app.action_generate()
        app.generation.start.assert_not_awaited()

        answer = (
            "결제만, 주문 생성 이후 PG webhook 반영까지. 중복 결제 방지, 환불·정산 제외."
        )
        await submit(pilot, answer)
        await app.workers.wait_for_complete()
        await pilot.pause()
        transcript = str(app.query_one("#transcript", Static).render())
        assert "결제 처리 시스템" in transcript
        assert scope in transcript and focus in transcript
        assert f"\n\n나\n  {answer}\n\n" in transcript
        context = app.query_one("#input_context", Static)
        assert scope in str(context.render()) and focus in str(context.render())
        assert "설계 범위\n" in str(context.render())
        assert app.query_one("#transcript", Static).parent.max_scroll_y > 0
        assert app.query_one("#brief", Input).region.bottom <= app.screen.size.height
        app.generation.start.assert_not_awaited()
        history = assessor.call_args.kwargs["history"]
        assert json.loads(history[0]["content"])["question"]
        assert history[-1] == {"role": "user", "content": answer}

        assert (
            app.query_one("#brief", Input).placeholder
            == "이 주제로 진행하려면 y, 수정하려면 요구사항을 입력하세요."
        )
        app.action_generate()
        app.generation.start.assert_not_awaited()
        calls = assessor.call_count
        await submit(pilot, "y")
        assert not app.query_one("#brief", Input).display
        assert "Ctrl+G" in str(app.query_one("#input_context", Static).render())
        assert assessor.call_count == calls
        app.generation.start.assert_not_awaited()

        await pilot.press("ctrl+g")
        await app.workers.wait_for_complete()
        brief = app.generation.start.call_args.args[0]
        assert brief.topic == "결제 처리 시스템"
        assert brief.scope == scope and brief.focus == focus
        app.generation.start.assert_awaited_once()
        assert scope in app.log_path.read_text()


@pytest.mark.asyncio
async def test_edit_invalidates_draft_and_blocks_duplicate_calls_while_waiting(
    monkeypatch, tmp_path
):
    entered, release = Event(), Event()
    first = decision(scope="결제 요청부터 상태 반영까지", focus="중복 결제 방지")
    updated = decision(scope="결제와 환불 결과 반영까지", focus="중복 결제·환불 방지")

    def assess(brief, *, history):
        if len(history) == 2:
            return first
        entered.set()
        if not release.wait(5):
            raise TimeoutError("테스트 응답 해제 실패")
        return updated

    assessor = Mock(side_effect=assess)
    monkeypatch.setattr("archgen.tui.app.assess_scope", assessor)
    app = ArchGenApp(log_path=tmp_path / "input.log")
    app.generation.start = AsyncMock(
        return_value={"status": "complete", "events": [], "output_dir": "/tmp/result"}
    )
    async with app.run_test() as pilot:
        try:
            await submit(pilot, "Middle")
            await submit(pilot, "결제 시스템")
            await app.workers.wait_for_complete()
            await submit(pilot, "환불도 포함해 주세요.")
            assert await asyncio.to_thread(entered.wait, 2)
            app.action_generate()
            app.action_generate()
            assert app.query_one("#brief", Input).disabled
            app.generation.start.assert_not_awaited()
            assert assessor.call_count == 2
            release.set()
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert updated.draft.scope in str(
                app.query_one("#transcript", Static).render()
            )
            app.generation.start.assert_not_awaited()
            await submit(pilot, "y")
            await pilot.press("ctrl+g")
            await app.workers.wait_for_complete()
            assert app.generation.start.call_args.args[0].scope == updated.draft.scope
        finally:
            release.set()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error", [TimeoutError("모델 시간 초과"), ValueError("응답 스키마 위반")]
)
async def test_scope_failure_keeps_dialogue_and_allows_retry_without_generation(
    monkeypatch, tmp_path, error
):
    question = decision(question="결제와 주문 중 어디를 다룰까요?")
    final = decision(scope="결제 요청부터 결과 반영까지", focus="중복 결제 방지")
    assessor = Mock(side_effect=[question, error, final])
    monkeypatch.setattr("archgen.tui.app.assess_scope", assessor)
    app = ArchGenApp(log_path=tmp_path / "input.log")
    app.generation.start = AsyncMock()
    async with app.run_test() as pilot:
        await submit(pilot, "Middle")
        await submit(pilot, "주문/결제 시스템")
        await app.workers.wait_for_complete()
        await submit(pilot, "결제만")
        await app.workers.wait_for_complete()
        await pilot.pause()
        transcript = str(app.query_one("#transcript", Static).render())
        assert "범위 판단 실패" in transcript and "결제만" in transcript
        assert not app.query_one("#brief", Input).disabled
        app.action_generate()
        app.generation.start.assert_not_awaited()
        await submit(pilot, "")
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert final.draft.scope in str(app.query_one("#transcript", Static).render())
        app.generation.start.assert_not_awaited()
        assert assessor.call_args.kwargs["history"][-1] == {
            "role": "user",
            "content": "결제만",
        }


@pytest.mark.asyncio
async def test_dialogue_placeholder_does_not_suggest_an_unrelated_topic(
    monkeypatch, tmp_path
):
    assessor = Mock(return_value=decision(question="어떤 기능을 다룰까요?"))
    monkeypatch.setattr("archgen.tui.app.assess_scope", assessor)
    app = ArchGenApp(log_path=tmp_path / "input.log")
    async with app.run_test() as pilot:
        await submit(pilot, "Middle")
        transcript = str(app.query_one("#transcript", Static).render())
        assert "Uber" not in transcript
        assert app.query_one("#brief", Input).placeholder == "답변을 입력하세요."
        await app.workers.wait_for_complete()
        await submit(pilot, "   ")
        assert "입력해 주세요" in str(app.query_one("#transcript", Static).render())
        assessor.assert_not_called()


@pytest.mark.asyncio
async def test_seniority_shows_fixed_topic_question_without_calling_agent(
    monkeypatch, tmp_path
):
    assessor = Mock(return_value=decision(question="주문과 결제 중 어디를 다룰까요?"))
    monkeypatch.setattr("archgen.tui.app.assess_scope", assessor)
    app = ArchGenApp(log_path=tmp_path / "input.log")
    app.generation.start = AsyncMock()
    async with app.run_test() as pilot:
        await submit(pilot, "Middle")
        await app.workers.wait_for_complete()
        assert app.filler.is_complete
        assessor.assert_not_called()
        assert "어떤 주제로 연습하고 싶으세요?" in str(
            app.query_one("#input_context", Static).render()
        )
        app.action_generate()
        app.generation.start.assert_not_awaited()

        await submit(pilot, "주문/결제 시스템")
        await app.workers.wait_for_complete()
        assessor.assert_called_once()
        assert assessor.call_args.kwargs["history"][-1] == {
            "role": "user",
            "content": "주문/결제 시스템",
        }
        app.generation.start.assert_not_awaited()
