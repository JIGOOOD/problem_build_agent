import json
import signal
import time
from types import SimpleNamespace

import pytest

import try_research


def test_llm_deadline_stops_a_call_that_keeps_waiting() -> None:
    original_handler = signal.getsignal(signal.SIGALRM)
    started = time.monotonic()

    with (
        pytest.raises(TimeoutError, match="LLM 호출이 실제 경과 시간 0.05초를 초과"),
        try_research.llm_deadline(0.05),
    ):
        time.sleep(10)

    assert time.monotonic() - started < 1
    assert signal.getsignal(signal.SIGALRM) == original_handler
    assert signal.getitimer(signal.ITIMER_REAL)[0] == 0


def test_run_saves_raw_retry_responses_plan_and_searches(tmp_path, monkeypatch) -> None:
    invalid = {"topic_summary": "채팅", "search_queries": [{"query": "chat"}]}
    valid = {
        "topic_summary": "채팅 서비스",
        "nfr_candidates": [
            {"kind": kind, "reason": "채팅 설계에 필요하다"}
            for kind in ["latency", "availability", "consistency"]
        ],
        "search_queries": [
            {"query": "chat", "related_nfr": None},
            *[
                {"query": f"chat {kind}", "related_nfr": kind}
                for kind in ["latency", "availability", "consistency"]
            ],
        ],
    }

    class FakeModel:
        def __init__(self):
            self.responses = iter([invalid, valid])

        def bind(self, **kwargs):
            return self

        def invoke(self, messages):
            return SimpleNamespace(
                content=json.dumps(next(self.responses), ensure_ascii=False),
                response_metadata={"finish_reason": "stop"},
                usage_metadata={"input_tokens": 10, "output_tokens": 20},
            )

    class FakeTavily:
        def __init__(self, **kwargs):
            pass

        def search(self, **kwargs):
            return {"results": [{"url": "https://example.com/chat", "title": "채팅"}]}

    monkeypatch.setattr(try_research, "build_chat_model", lambda *a, **kw: FakeModel())
    monkeypatch.setattr(try_research, "TavilyClient", FakeTavily)
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-secret")

    run_dir = try_research.run(log_root=tmp_path)

    first = json.loads((run_dir / "llm-01.json").read_text())
    second = json.loads((run_dir / "llm-02.json").read_text())
    assert json.loads(first["content"]) == invalid
    assert json.loads(second["content"]) == valid
    assert first["finish_reason"] == "stop"
    assert second["usage"]["output_tokens"] == 20
    assert json.loads((run_dir / "plan.json").read_text()) == valid
    searches = json.loads((run_dir / "searches.json").read_text())
    assert len(searches) == 4
    assert searches[0]["results"][0]["url"] == "https://example.com/chat"
    assert searches[1]["results"] == []
    log = (run_dir / "run.log").read_text()
    assert "1회 재시도" in log
    assert "nfr_candidates: Field required" in log
    assert "전체 실행 시간:" in log
    assert "test-tavily-secret" not in "".join(p.read_text() for p in run_dir.iterdir())


def test_failed_call_keeps_error_and_traceback_in_run_directory(tmp_path, monkeypatch):
    class TimedOutModel:
        def bind(self, **kwargs):
            return self

        def invoke(self, messages):
            raise TimeoutError("실제 경과 시간 60초 초과")

    monkeypatch.setattr(
        try_research, "build_chat_model", lambda *a, **kw: TimedOutModel()
    )
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-secret")

    with pytest.raises(TimeoutError, match="60초 초과"):
        try_research.run(log_root=tmp_path)

    run_dir = next(tmp_path.iterdir())
    call = json.loads((run_dir / "llm-01.json").read_text())
    assert call["status"] == "error"
    assert call["error_type"] == "TimeoutError"
    assert call["error"] == "실제 경과 시간 60초 초과"
    assert call["seconds"] >= 0
    log = (run_dir / "run.log").read_text()
    assert "Traceback (most recent call last)" in log
    assert "TimeoutError: 실제 경과 시간 60초 초과" in log
    assert "전체 실행 시간:" in log
