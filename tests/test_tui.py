import pytest
from textual.widgets import Input, Static

from archgen.tui.app import ArchGenApp


@pytest.mark.asyncio
async def test_tui_mounts_the_brief_input() -> None:
    app = ArchGenApp()

    async with app.run_test():
        assert app.query_one("#brief", Input)
        assert app.query_one("#transcript", Static)


@pytest.mark.asyncio
async def test_generate_runs_the_langgraph_scaffold() -> None:
    app = ArchGenApp()

    async with app.run_test() as pilot:
        app.answers.append("Design a ticketing service")
        app.action_generate()
        await pilot.pause()

        transcript = app.query_one("#transcript", Static)
        assert "workflow scaffold completed" in str(transcript.render())
