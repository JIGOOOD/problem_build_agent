import asyncio
from unittest.mock import AsyncMock

import pytest
from textual.widgets import Input, LoadingIndicator, Static

from archgen.domain.brief import Seniority
from archgen.tui.app import ArchGenApp


@pytest.mark.asyncio
async def test_interactive_fake_mode_runs_without_api_keys(tmp_path, monkeypatch):
    import json
    from unittest.mock import Mock

    from archgen.core import service

    monkeypatch.setattr(service, "FAKE_STEP_SECONDS", 1)
    forbidden = Mock(side_effect=AssertionError("Fake TUI에서 외부 호출"))
    for name in ("build_chat_model", "TavilyClient", "create_fetch_client"):
        monkeypatch.setattr(service, name, forbidden)
    monkeypatch.setattr(service, "PROJECT_ROOT", tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    app = ArchGenApp(fake=True, log_path=tmp_path / "input.log")
    async with app.run_test() as pilot:
        assert "Fake" in app.sub_title and "고정 채팅 예시" in app.sub_title
        await answer(pilot, "미들")
        await answer(pilot, "주문/결제 시스템")
        await answer(pilot, "멱등성")
        app.action_generate()
        await pilot.pause()
        assert app.query_one("#loading", LoadingIndicator).display
        assert "경과" in str(app.query_one("#progress", Static).render())
        app.action_generate()
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert "생성 완료" in str(app.query_one("#progress", Static).render())
        assert not app.query_one("#loading", LoadingIndicator).display
        forbidden.assert_not_called()
        runs = list((tmp_path / ".archgen" / "fake-generation").iterdir())
        assert len(runs) == 1
        raw = json.loads((runs[0] / "input.json").read_text())
        assert raw["topic"] == "주문/결제 시스템" and raw["notes"] == "멱등성"
        assert (runs[0] / "nfr_rubric.md").is_file()


@pytest.mark.asyncio
async def test_tui_runs_real_generation_graph_with_fake_llm(
    tmp_path, monkeypatch, golden_export, golden_document_ids
):
    import json
    from threading import Event
    from unittest.mock import Mock

    from langchain_core.language_models.fake_chat_models import FakeListChatModel

    from archgen.core import service
    from archgen.domain.nfr import NFRSelection
    from archgen.domain.research import Document, ResearchResult

    responses = [
        NFRSelection(**golden_export.model_dump(exclude={"rubric"})).model_dump_json(),
        golden_export.rubric.model_dump_json(),
    ]
    entered = [Event(), Event()]
    release = [Event(), Event()]
    original_call = FakeListChatModel._call

    def gated_call(model, *args, **kwargs):
        step = model.i
        entered[step].set()
        if not release[step].wait(5):
            raise TimeoutError("Fake LLM 대기 해제 실패")
        return original_call(model, *args, **kwargs)

    monkeypatch.setattr(FakeListChatModel, "_call", gated_call)
    monkeypatch.setattr(
        FakeListChatModel, "get_num_tokens_from_messages", lambda *a: 9000
    )
    monkeypatch.setattr(
        service,
        "build_chat_model",
        lambda tier, **kwargs: FakeListChatModel(
            responses=responses, callbacks=kwargs["callbacks"]
        ),
    )
    monkeypatch.setattr(service, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("TAVILY_API_KEY", "fake-key")
    monkeypatch.setattr(service, "TavilyClient", Mock())
    monkeypatch.setattr(
        service,
        "run_research",
        Mock(
            return_value=ResearchResult(
                topic_summary="채팅",
                nfr_candidates=[],
                documents=[
                    Document(
                        id=i, title=i, url=f"https://example.com/{i}", content="보존 근거"
                    )
                    for i in sorted(golden_document_ids)
                ],
            )
        ),
    )

    app = ArchGenApp(log_path=tmp_path / "input.log")
    async with app.run_test() as pilot:
        await answer(pilot, "미들")
        await answer(pilot, "채팅 서비스")
        await answer(pilot, "")
        app.action_generate()
        try:
            for step, phase in enumerate(["NFR 선정 중", "평가 기준 작성 중"]):
                assert await asyncio.to_thread(entered[step].wait, 5)
                await pilot.pause()
                assert phase in str(app.query_one("#progress", Static).render())
                assert app.query_one("#loading", LoadingIndicator).display
                release[step].set()
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert "생성 완료" in str(app.query_one("#progress", Static).render())
            assert not app.query_one("#loading", LoadingIndicator).display
            root = next((tmp_path / ".archgen" / "generation").iterdir())
            assert (root / "nfr_rubric.md").is_file()
            assert json.loads((root / "status.json").read_text())["status"] == "complete"
            assert len(list(root.glob("llm-*-response.json"))) == 2
        finally:
            for gate in release:
                gate.set()


@pytest.mark.asyncio
async def test_generation_shows_live_stage_elapsed_time_and_prevents_duplicates(
    tmp_path, monkeypatch
):
    import archgen.tui.app as module

    clock = [10.0]
    monkeypatch.setattr(module, "monotonic", lambda: clock[0])
    app = ArchGenApp(log_path=tmp_path / "input.log")
    started, release = asyncio.Event(), asyncio.Event()

    async def generate(brief, *, on_progress):
        await asyncio.to_thread(on_progress, "자료 조사 중")
        started.set()
        await release.wait()
        return {"status": "complete", "events": [], "output_dir": "/tmp/result"}

    app.generation.start = AsyncMock(side_effect=generate)
    async with app.run_test() as pilot:
        await answer(pilot, "미들")
        await answer(pilot, "채팅 서비스")
        await answer(pilot, "")
        app.action_generate()
        await asyncio.wait_for(started.wait(), timeout=2)
        await pilot.pause()

        progress = app.query_one("#progress", Static)
        assert "자료 조사 중" in str(progress.render())
        assert app.query_one("#loading", LoadingIndicator).display
        clock[0] = 14.0
        await pilot.pause(1.1)
        assert "경과 4초" in str(progress.render())
        app.action_generate()
        await pilot.pause()
        app.generation.start.assert_awaited_once()

        release.set()
        await pilot.pause()
        assert "생성 완료" in str(progress.render())
        assert not app.query_one("#loading", LoadingIndicator).display
        clock[0] = 20.0
        await pilot.pause(1.1)
        assert "경과 4초" in str(progress.render())


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
        assert (
            app.query_one("#brief", Input).placeholder == app.filler.current.placeholder
        )


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
async def test_generate_starts_generation_once_filled() -> None:
    app = ArchGenApp()
    app.generation.start = AsyncMock(
        return_value={
            "status": "complete",
            "events": ["finalize: completed"],
            "output_dir": "/tmp/result",
        }
    )

    async with app.run_test() as pilot:
        await answer(pilot, "시니어")
        await answer(pilot, "주문/결제 시스템")
        await answer(pilot, "멱등성 중요")

        app.action_generate()
        await pilot.pause()

        assert "finalize: completed" in transcript_of(app)
        brief = app.generation.start.call_args.args[0]
        assert brief.seniority is Seniority.SENIOR
        assert brief.topic == "주문/결제 시스템"
        assert brief.notes == "멱등성 중요"


@pytest.mark.asyncio
async def test_generation_failure_is_reported_without_crashing_app(tmp_path):
    app = ArchGenApp(log_path=tmp_path / "input.log")
    app.generation.start = AsyncMock(side_effect=TimeoutError("LLM timeout"))

    async with app.run_test() as pilot:
        await answer(pilot, "미들")
        await answer(pilot, "채팅 서비스")
        await answer(pilot, "")
        app.action_generate()
        await pilot.pause()

        app.generation.start.assert_awaited_once()
        assert app.is_running
        assert "생성 실패: LLM timeout" in app.log_path.read_text()
        assert "생성 실패" in str(app.query_one("#progress", Static).render())
        assert not app.query_one("#loading", LoadingIndicator).display
