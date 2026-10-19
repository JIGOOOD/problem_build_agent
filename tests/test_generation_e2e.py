import json
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage

from archgen.core.graph import build_generation_graph, new_thread_config
from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.domain.nfr import NFRSelection
from archgen.paths import CATALOG_DIR
from archgen.research.runner import run_research
from archgen.retrieval.crawler import FetchTool
from archgen.retrieval.search import SearchTool


def tools(name, arguments):
    return AIMessage(
        content="",
        tool_calls=[
            {"id": f"{name}-{i}", "name": name, "args": args, "type": "tool_call"}
            for i, args in enumerate(arguments)
        ],
    )


class ResearchModel:
    def __init__(self, fetch):
        self.fetch = fetch
        self.calls = 0

    def bind(self, **kwargs):
        return self

    def bind_tools(self, definitions):
        return self

    def invoke(self, messages):
        self.calls += 1
        if self.calls == 1:
            kinds = ["fault_tolerance", "latency", "scalability"]
            return AIMessage(
                content=json.dumps(
                    {
                        "topic_summary": "채팅 조사",
                        "nfr_candidates": [
                            {"kind": k, "reason": "설계에 영향"} for k in kinds
                        ],
                        "search_queries": [
                            {"query": "chat architecture", "related_nfr": None},
                            *[{"query": f"chat {k}", "related_nfr": k} for k in kinds],
                        ],
                    }
                )
            )
        if self.calls == 2:
            return tools("search", [{"query_id": "query-1"}])
        if self.calls == 3:
            return tools(
                "fetch",
                [
                    {
                        "query_id": "query-1",
                        "urls": [
                            "https://example.com/keep",
                            "https://example.com/discard",
                        ],
                    }
                ],
            )
        if self.calls == 4:
            kept = next(
                doc for doc in self.fetch.documents.values() if doc.url.endswith("/keep")
            )
            return tools("keep", [{"doc_id": kept.id, "sentence_indices": [0]}])
        return AIMessage(content="조사 완료")


@pytest.mark.parametrize("cite_discarded", [False, True])
def test_real_research_runner_to_markdown_with_fake_external_services(
    tmp_path, golden_export, cite_discarded
):
    catalog = load_catalog(CATALOG_DIR)
    search_client = Mock()
    search_client.search.return_value = {
        "results": [
            {"url": "https://example.com/keep", "title": "보존할 문서"},
            {"url": "https://example.com/discard", "title": "버릴 문서"},
        ]
    }
    fetch = FetchTool(
        lambda url: {"title": url, "content": "보존할 원문.\n\n선택하지 않은 원문."}
    )
    model = ResearchModel(fetch)
    research = Mock(
        side_effect=lambda brief: run_research(
            brief, catalog, model, SearchTool(search_client), fetch
        )
    )
    author_calls = []

    def author(messages):
        author_calls.append(messages)
        payload = json.loads(messages[1]["content"])
        if len(author_calls) != 1:
            return golden_export.rubric.model_dump_json()
        selected = NFRSelection(**golden_export.model_dump(exclude={"rubric"}))
        citation = (
            next(
                doc.id for doc in fetch.documents.values() if doc.url.endswith("/discard")
            )
            if cite_discarded
            else payload["research"]["documents"][0]["id"]
        )
        for item in [*selected.confirmed_nfrs, *selected.tradeoffs]:
            item.evidence_refs = [citation]
        return selected.model_dump_json()

    judge = Mock(return_value='{"findings": []}')
    graph = build_generation_graph(
        research=research,
        llm=author,
        count_tokens=lambda messages: 9000,
        catalog=catalog,
        output_dir=tmp_path,
        judge_llm=judge,
    )
    result = graph.invoke(
        {"brief": InterviewBrief(Seniority.MIDDLE, "채팅 서비스"), "events": []},
        config=new_thread_config(),
    )

    research.assert_called_once()
    search_client.search.assert_called_once()
    assert model.calls == 5
    assert len(fetch.documents) == 2
    assert len(result["research"].documents) == 1
    assert result["research"].documents[0].content == "보존할 원문."
    assert all("선택하지 않은 원문" not in call[1]["content"] for call in author_calls)
    assert result["status"] == ("failed" if cite_discarded else "complete")
    assert (tmp_path / "nfr_rubric.md").exists() == (not cite_discarded)
    if cite_discarded:
        assert result["repairs"] == 0
        assert "선정" in result["reason"]
        assert any(f.code == "EVIDENCE_REF_UNKNOWN" for f in result["findings"])
        judge.assert_not_called()
    else:
        assert result["findings"] == []
        assert len(author_calls) == 2
        judge.assert_called_once()
