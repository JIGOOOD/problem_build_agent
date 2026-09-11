import pytest
from textual.widgets import Input, Static

from archgen.domain.brief import Seniority
from archgen.tui.app import ArchGenApp


def transcript_of(app: ArchGenApp) -> str:
    return str(app.query_one("#transcript", Static).render())


async def answer(pilot, text: str) -> None:
    app = pilot.app
    app.query_one("#brief", Input).value = text
    await pilot.press("enter")
    await pilot.pause()


@pytest.mark.asyncio
async def test_tui_opens_on_the_seniority_slot() -> None:
    app = ArchGenApp()

    async with app.run_test():
        assert app.filler.current.key == "seniority"
        assert "대상 연차" in transcript_of(app)
        assert app.query_one("#brief", Input).placeholder == app.filler.current.placeholder


@pytest.mark.asyncio
async def test_required_slot_loops_until_answered() -> None:
    app = ArchGenApp()

    async with app.run_test() as pilot:
        await answer(pilot, "   ")

        assert app.filler.current.key == "seniority", "빈 입력으로는 넘어가지 않는다"
        assert "필수 입력" in transcript_of(app)

        await answer(pilot, "주니어")
        assert app.filler.current.key == "topic"


@pytest.mark.asyncio
async def test_optional_slot_completes_the_brief() -> None:
    app = ArchGenApp()

    async with app.run_test() as pilot:
        await answer(pilot, "3")
        await answer(pilot, "주문/결제 시스템")
        await answer(pilot, "")

        assert app.filler.is_complete
        brief = app.filler.build_brief()
        assert brief.seniority is Seniority.MIDDLE
        assert brief.notes is None


@pytest.mark.asyncio
async def test_generate_is_refused_while_slots_are_unfilled() -> None:
    app = ArchGenApp()

    async with app.run_test() as pilot:
        await answer(pilot, "시니어")
        app.action_generate()
        await pilot.pause()

        assert "workflow scaffold completed" not in transcript_of(app)


@pytest.mark.asyncio
async def test_generate_runs_the_langgraph_scaffold_once_filled() -> None:
    app = ArchGenApp()

    async with app.run_test() as pilot:
        await answer(pilot, "시니어")
        await answer(pilot, "주문/결제 시스템")
        await answer(pilot, "멱등성 중요")

        app.action_generate()
        await pilot.pause()

        assert "workflow scaffold completed" in transcript_of(app)
