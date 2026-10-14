import json
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage

from archgen.core import service
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRSelection
from archgen.domain.research import Document, ResearchResult

BRIEF = InterviewBrief(Seniority.MIDDLE, "채팅 서비스")


def test_fake_generation_needs_no_keys_or_external_services(monkeypatch, tmp_path):
    monkeypatch.setattr(service, "FAKE_STEP_SECONDS", 0)
    forbidden = Mock(side_effect=AssertionError("Fake 모드에서 외부 서비스 호출"))
    for name in ("build_chat_model", "TavilyClient", "create_fetch_client"):
        monkeypatch.setattr(service, name, forbidden)
    for key in ("OPENROUTER_API_KEY", "TAVILY_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    progress = []

    result = service.run_generation(
        BRIEF, fake=True, output_root=tmp_path, on_progress=progress.append
    )

    assert result["status"] == "complete"
    forbidden.assert_not_called()
    root = next(tmp_path.iterdir())
    assert (root / "nfr_rubric.md").is_file()
    assert len(list(root.glob("llm-*-response.json"))) == 2
    assert json.loads((root / "input.json").read_text())["topic"] == BRIEF.topic
    assert "Fake" in (root / "run.log").read_text()
    assert "자료 조사 중" in progress and "평가 기준 작성 중" in progress


def test_runtime_reports_each_stage_before_work(runtime, monkeypatch, tmp_path):
    small, large, _ = runtime
    progress = []
    research_result = service.run_research.return_value
    responses = iter(small.invoke.side_effect)

    def research(*args):
        assert progress[-1] == "자료 조사 중"
        return research_result

    def generate(messages):
        expected = "NFR 선정 중" if small.invoke.call_count == 1 else "평가 기준 작성 중"
        assert progress[-1] == expected
        return next(responses)

    def judge(messages):
        assert progress[-1] == "평가 기준 검토 중"
        return AIMessage(content='{"findings": []}')

    monkeypatch.setattr(service, "run_research", research)
    small.invoke.side_effect = generate
    large.invoke.side_effect = judge
    result = service.run_generation(
        BRIEF, output_root=tmp_path, judge_enabled=True, on_progress=progress.append
    )

    assert result["status"] == "complete"
    assert progress == [
        "자료 조사 중",
        "NFR 선정 중",
        "평가 기준 작성 중",
        "기본 검증 중",
        "채점표 작성 중",
        "평가 기준 검토 중",
        "결과 저장 중",
    ]


@pytest.fixture
def runtime(monkeypatch, golden_export, golden_document_ids):
    small, large = Mock(), Mock()
    small.bind.return_value = small
    large.bind.return_value = large
    small.get_num_tokens_from_messages.return_value = 9000
    small.invoke.side_effect = [
        AIMessage(
            content=NFRSelection(
                **golden_export.model_dump(exclude={"rubric"})
            ).model_dump_json()
        ),
        AIMessage(content=golden_export.rubric.model_dump_json()),
    ]
    large.invoke.return_value = AIMessage(content='{"findings": []}')
    factory = Mock(side_effect=lambda tier, **kwargs: small if tier == "small" else large)
    monkeypatch.setattr(service, "build_chat_model", factory)
    monkeypatch.setenv("TAVILY_API_KEY", "fake-key")
    monkeypatch.setattr(service, "TavilyClient", Mock())
    research = ResearchResult(
        topic_summary="채팅",
        nfr_candidates=[],
        documents=[
            Document(id=i, title=i, url=f"https://example.com/{i}", content="보존 문장")
            for i in sorted(golden_document_ids)
        ],
    )
    monkeypatch.setattr(service, "run_research", Mock(return_value=research))
    return small, large, factory


@pytest.mark.parametrize("judge_enabled", [False, True])
def test_runtime_uses_small_for_generation_and_large_for_enabled_judge(
    runtime, tmp_path, judge_enabled
):
    small, large, factory = runtime

    result = service.run_generation(
        BRIEF, output_root=tmp_path, judge_enabled=judge_enabled
    )

    assert result["status"] == "complete"
    assert [call.args[0] for call in factory.call_args_list] == (
        ["small", "large"] if judge_enabled else ["small"]
    )
    assert small.invoke.call_count == 2
    assert large.invoke.call_count == int(judge_enabled)
    root = next(tmp_path.iterdir())
    assert (root / "nfr_rubric.md").exists()
    log = (root / "run.log").read_text()
    assert "research" in log and "finalize" in log
    assert "fake-key" not in log
    for call in factory.call_args_list:
        assert call.kwargs["max_retries"] == 0
        assert call.kwargs["timeout"] == 300


def test_runtime_records_real_langchain_callbacks_without_network(
    runtime, monkeypatch, tmp_path, golden_export
):
    from langchain_core.language_models.fake_chat_models import FakeListChatModel

    responses = [
        NFRSelection(**golden_export.model_dump(exclude={"rubric"})).model_dump_json(),
        golden_export.rubric.model_dump_json(),
    ]
    monkeypatch.setattr(
        FakeListChatModel, "get_num_tokens_from_messages", lambda *args: 9000
    )
    monkeypatch.setattr(
        service,
        "build_chat_model",
        lambda tier, **kwargs: FakeListChatModel(
            responses=responses, callbacks=kwargs["callbacks"]
        ),
    )

    result = service.run_generation(BRIEF, output_root=tmp_path)

    root = next(tmp_path.iterdir())
    inputs = list(root.glob("llm-*-input.json"))
    outputs = list(root.glob("llm-*-response.json"))
    assert result["status"] == "complete"
    assert len(inputs) == len(outputs) == 2
    for path in inputs:
        payload = json.loads(path.read_text())
        assert payload["messages"][0][0]["type"] == "system"
        assert payload["messages"][0][1]["type"] == "human"
    assert "LLM 요청" in (root / "run.log").read_text()
    assert "LLM 응답" in (root / "run.log").read_text()


@pytest.mark.parametrize(
    "failure",
    [
        "budget",
        "selection_json",
        "rubric_json",
        "timeout",
        "non_text",
        "judge_timeout",
        "missing_search_key",
        "auth",
    ],
)
def test_runtime_failure_preserves_logs_and_never_publishes_markdown(
    runtime, monkeypatch, tmp_path, failure
):
    import logging

    small, large, factory = runtime
    logger = logging.getLogger("archgen")
    old_handlers, old_level = list(logger.handlers), logger.level
    if failure == "budget":
        small.get_num_tokens_from_messages.return_value = 10001
    elif failure == "selection_json":
        small.invoke.side_effect = [AIMessage(content="bad json")]
    elif failure == "rubric_json":
        responses = list(small.invoke.side_effect)
        small.invoke.side_effect = [responses[0], AIMessage(content="bad json")]
    elif failure == "timeout":
        small.invoke.side_effect = TimeoutError("LLM timeout")
    elif failure == "non_text":
        small.invoke.side_effect = [
            AIMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/image"},
                    }
                ]
            )
        ]
    elif failure == "judge_timeout":
        large.invoke.side_effect = TimeoutError("Judge timeout")
    elif failure == "missing_search_key":
        monkeypatch.delenv("TAVILY_API_KEY")
    else:
        factory.side_effect = RuntimeError("API key expired")

    expected = {
        "budget": ValueError,
        "selection_json": ValueError,
        "rubric_json": ValueError,
        "timeout": TimeoutError,
        "non_text": TypeError,
        "judge_timeout": TimeoutError,
        "missing_search_key": RuntimeError,
        "auth": RuntimeError,
    }[failure]
    with pytest.raises(expected):
        service.run_generation(
            BRIEF, output_root=tmp_path, judge_enabled=failure == "judge_timeout"
        )

    root = next(tmp_path.iterdir())
    error = json.loads((root / "error.json").read_text())
    assert error["type"] and error["message"]
    assert "생성 실패" in (root / "run.log").read_text()
    assert not (root / "nfr_rubric.md").exists()
    assert logger.handlers == old_handlers
    assert logger.level == old_level
    if failure == "budget":
        small.invoke.assert_not_called()
