"""실제 모델·검색·fetch를 생성 그래프에 연결한다."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import convert_to_messages
from tavily import TavilyClient

from archgen.config import build_chat_model, response_text
from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import load_catalog
from archgen.paths import CATALOG_DIR, PROJECT_ROOT
from archgen.research.runner import run_research
from archgen.retrieval.crawler import FetchTool, HttpFetcher, create_fetch_client
from archgen.retrieval.search import SearchTool

from .graph import GenerationState, build_generation_graph, new_thread_config


class _LLMTrace(BaseCallbackHandler):
    def __init__(self, directory: Path):
        self.directory = directory

    def save(self, run_id, suffix, value):
        (self.directory / f"llm-{run_id}-{suffix}.json").write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        self.save(
            run_id,
            "input",
            {
                "messages": [
                    [m.model_dump(mode="json") for m in batch] for batch in messages
                ]
            },
        )
        logging.getLogger("archgen").info("LLM 요청 %s", run_id)

    def on_llm_end(self, response, *, run_id, **kwargs):
        self.save(run_id, "response", response.model_dump(mode="json"))
        logging.getLogger("archgen").info("LLM 응답 %s", run_id)

    def on_llm_error(self, error, *, run_id, **kwargs):
        self.save(run_id, "error", {"type": type(error).__name__, "message": str(error)})
        logging.getLogger("archgen").error("LLM 실패 %s: %s", run_id, error)


def run_generation(
    brief: InterviewBrief, *, output_root: Path | None = None, judge_enabled: bool = False
) -> GenerationState:
    """Judge는 실제 오탐 검증 후 judge_enabled로 활성화한다."""
    root = (
        Path(output_root)
        if output_root is not None
        else PROJECT_ROOT / ".archgen" / "generation"
    )
    root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(
        tempfile.mkdtemp(prefix=datetime.now(UTC).strftime("%Y%m%d-%H%M%S-"), dir=root)
    )
    logger = logging.getLogger("archgen")
    old_level = logger.level
    handler = logging.FileHandler(run_dir / "run.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        logger.info(
            "실행 로그: %s | 생성 small | Judge %s",
            run_dir,
            "large" if judge_enabled else "off",
        )
        trace = _LLMTrace(run_dir)
        model = build_chat_model(
            "small",
            timeout=300,
            max_retries=0,
            tiktoken_model_name="gpt-4o",
            callbacks=[trace],
        )
        tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
        if not tavily_key:
            raise RuntimeError(".env에 TAVILY_API_KEY를 설정해 주세요.")
        catalog = load_catalog(CATALOG_DIR)

        def text_llm(model):
            bound = model.bind(response_format={"type": "json_object"})

            def invoke(messages):
                response = bound.invoke(messages)
                return response_text(response)

            return invoke

        llm = text_llm(model)
        judge_llm = (
            text_llm(
                build_chat_model("large", timeout=300, max_retries=0, callbacks=[trace])
            )
            if judge_enabled
            else None
        )
        with create_fetch_client() as client:
            search = SearchTool(TavilyClient(api_key=tavily_key))
            fetch = FetchTool(HttpFetcher(client))
            graph = build_generation_graph(
                research=lambda brief: run_research(brief, catalog, model, search, fetch),
                llm=llm,
                count_tokens=lambda messages: model.get_num_tokens_from_messages(
                    convert_to_messages(messages)
                ),
                catalog=catalog,
                output_dir=run_dir,
                judge_llm=judge_llm,
            )
            result = graph.invoke(
                {"brief": brief, "events": []}, config=new_thread_config()
            )
        return result
    except Exception as error:
        logger.exception("생성 실패")
        (run_dir / "error.json").write_text(
            json.dumps(
                {"type": type(error).__name__, "message": str(error)},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        raise
    finally:
        logger.removeHandler(handler)
        handler.close()
        logger.setLevel(old_level)


class GenerationService:
    async def start(self, brief: InterviewBrief) -> GenerationState:
        return await asyncio.to_thread(run_generation, brief)
