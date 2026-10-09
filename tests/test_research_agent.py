import copy
import json
from threading import Barrier, Event, Lock
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import load_catalog
from archgen.paths import CATALOG_DIR
from archgen.research import runner
from archgen.research.keep import KeepTool
from archgen.research.runner import run_research
from archgen.retrieval.crawler import FetchTool
from archgen.retrieval.search import SearchTool

KINDS = ["latency", "availability", "consistency"]
PLAN = {
    "topic_summary": "채팅 메시지 전달 경로를 조사한다.",
    "nfr_candidates": [
        {"kind": kind, "reason": f"채팅에서 {kind}가 중요하다."} for kind in KINDS
    ],
    "search_queries": [
        {"query": "chat architecture", "related_nfr": None},
        *[{"query": f"chat {kind}", "related_nfr": kind} for kind in KINDS],
    ],
}


def tool_response(name, arguments):
    return AIMessage(
        content="",
        tool_calls=[
            {"id": f"{name}-{i}", "name": name, "args": args, "type": "tool_call"}
            for i, args in enumerate(arguments, start=1)
        ],
    )


class FakeLLM:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []

    def bind(self, **kwargs):
        return self

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        self.calls.append(copy.deepcopy(messages))
        response = next(self.responses)
        return response(messages) if callable(response) else response


def latest_tools(messages):
    start = max(i for i, message in enumerate(messages) if message["role"] == "assistant")
    return messages[start + 1 :]


URLS = {
    "topic": ["https://docs.example/topic/1"],
    "latency": [f"https://docs.example/latency/{i}" for i in [1, 2]],
    "availability": ["https://docs.example/availability/1"],
}
ALL_URLS = [url for urls in URLS.values() for url in urls]
SEARCH = tool_response(
    "search",
    [{"query_id": f"query-{i}"} for i, _ in enumerate(PLAN["search_queries"], start=1)],
)
FETCH = tool_response("fetch", [{"query_id": f"query-{i}"} for i in [1, 2, 3]])
FINISH = AIMessage(content="조사 완료")


def fetched_documents(messages):
    return [
        item["result"]
        for message in latest_tools(messages)
        for item in json.loads(message["content"])
        if isinstance(item["result"], dict)
    ]


def keep_fetched(messages):
    return tool_response(
        "keep",
        [
            {"doc_id": document["doc_id"], "sentence_indices": [3, 1]}
            for document in fetched_documents(messages)
        ],
    )


def run_scenario(*responses, search_barrier=None, fetch_barrier=None):
    class Tavily:
        def search(self, *, query, max_results):
            if search_barrier:
                search_barrier.wait(timeout=5)
            kind = next(
                q["related_nfr"] for q in PLAN["search_queries"] if q["query"] == query
            )
            urls = URLS.get(kind or "topic", [])
            return {"results": [{"url": url, "title": url} for url in urls]}

    def fetch(url):
        if fetch_barrier:
            fetch_barrier.wait(timeout=5)
        return {
            "title": url,
            "content": f"제외\n\n{url} p99 100ms\n\n제외\n\n{url} trade-off",
        }

    llm = FakeLLM(*responses)
    result = run_research(
        InterviewBrief(topic="실시간 채팅 서비스", seniority=Seniority.MIDDLE),
        load_catalog(CATALOG_DIR),
        llm,
        SearchTool(Tavily()),
        FetchTool(fetch),
    )
    return SimpleNamespace(llm=llm, result=result)


def planned(*responses):
    return run_scenario(AIMessage(content=json.dumps(PLAN)), *responses)


def test_initial_plan_uses_schema_bound_model_and_loop_uses_original_model():
    llm, initial, tools = Mock(), Mock(), Mock()
    llm.bind.return_value = initial
    llm.bind_tools.return_value = tools
    initial.invoke.return_value = AIMessage(content=json.dumps(PLAN))
    tools.invoke.return_value = FINISH

    run_research(
        InterviewBrief(topic="실시간 채팅 서비스", seniority=Seniority.MIDDLE),
        load_catalog(CATALOG_DIR),
        llm,
        Mock(),
        Mock(),
    )

    options = llm.bind.call_args.kwargs
    assert options["response_format"]["type"] == "json_schema"
    assert options["response_format"]["json_schema"]["strict"] is True
    initial.invoke.assert_called_once()
    llm.invoke.assert_not_called()
    llm.bind_tools.assert_called_once_with(runner.TOOLS)
    initial.bind_tools.assert_not_called()
    tools.invoke.assert_called_once()


def test_loop_prompt_requires_immediate_keep_decision_for_fetch_results():
    scenario = planned(FINISH)
    system = scenario.llm.calls[-1][0]["content"]
    assert "fetch 결과는 다음 회차에만 보이므로" in system
    assert "받은 즉시 같은 응답에서 keep 여부를 판정한다" in system
    assert "미루지 않는다" in system


def test_research_executes_search_calls_in_parallel():
    scenario = run_scenario(
        AIMessage(content=json.dumps(PLAN)),
        SEARCH,
        FINISH,
        search_barrier=Barrier(4),
    )

    assert len(latest_tools(scenario.llm.calls[-1])) == 4


def test_research_executes_fetch_calls_in_parallel():
    scenario = run_scenario(
        AIMessage(content=json.dumps(PLAN)),
        SEARCH,
        FETCH,
        FINISH,
        fetch_barrier=Barrier(len(ALL_URLS)),
    )

    assert len(fetched_documents(scenario.llm.calls[-1])) == len(ALL_URLS)


def test_research_passes_tool_results_with_matching_ids_in_call_order():
    scenario = planned(SEARCH, FETCH, keep_fetched, FINISH)

    for response, messages in zip([SEARCH, FETCH], scenario.llm.calls[2:4], strict=True):
        results = latest_tools(messages)
        assert [result["tool_call_id"] for result in results] == [
            call["id"] for call in response.tool_calls
        ]
        assert all(result["role"] == "tool" for result in results)
    search_results = latest_tools(scenario.llm.calls[2])
    for query_id, message in enumerate(search_results, start=1):
        assert all(
            result["query_id"] == f"query-{query_id}"
            for result in json.loads(message["content"])
        )
    assert [doc["url"] for doc in fetched_documents(scenario.llm.calls[3])] == ALL_URLS
    keep_results = latest_tools(scenario.llm.calls[4])
    assert [message["tool_call_id"] for message in keep_results] == [
        f"keep-{i}" for i in range(1, 5)
    ]
    assert [
        json.loads(message["content"])["kept_documents"] for message in keep_results
    ] == [1, 1, 2, 1]


def test_research_returns_selected_sentences_in_original_order():
    scenario = planned(SEARCH, FETCH, keep_fetched, FINISH)

    assert scenario.result.topic_summary == PLAN["topic_summary"]
    assert [document.model_dump() for document in scenario.result.documents] == [
        {
            "id": document["doc_id"],
            "url": url,
            "title": url,
            "content": f"{url} p99 100ms\n\n{url} trade-off",
        }
        for url, document in zip(
            ALL_URLS, fetched_documents(scenario.llm.calls[3]), strict=True
        )
    ]


def test_research_links_only_sufficient_candidate_evidence_and_keeps_topic_documents():
    scenario = planned(SEARCH, FETCH, keep_fetched, FINISH)

    assert [candidate.kind for candidate in scenario.result.nfr_candidates] == ["latency"]
    candidate = scenario.result.nfr_candidates[0]
    assert candidate.reason == PLAN["nfr_candidates"][0]["reason"]
    assert candidate.doc_ids == [
        document.id
        for document in scenario.result.documents
        if document.url in URLS["latency"]
    ]
    assert [document.url for document in scenario.result.documents] == ALL_URLS
    topic_doc_ids = {
        document.id
        for document in scenario.result.documents
        if document.url in URLS["topic"]
    }
    assert all(
        topic_doc_ids.isdisjoint(candidate.doc_ids)
        for candidate in scenario.result.nfr_candidates
    )


def test_research_keeps_excluded_candidate_documents_without_linking_them():
    scenario = planned(SEARCH, FETCH, keep_fetched, FINISH)

    assert "availability" not in [
        candidate.kind for candidate in scenario.result.nfr_candidates
    ]
    availability_docs = [
        document
        for document in scenario.result.documents
        if document.url in URLS["availability"]
    ]
    assert len(availability_docs) == 1
    assert all(
        availability_docs[0].id not in candidate.doc_ids
        for candidate in scenario.result.nfr_candidates
    )


def test_research_excludes_unselected_documents_from_result():
    def keep_only_topic(messages):
        first = fetched_documents(messages)[0]
        return tool_response(
            "keep", [{"doc_id": first["doc_id"], "sentence_indices": [1]}]
        )

    scenario = planned(SEARCH, FETCH, keep_only_topic, FINISH)

    assert [document.url for document in scenario.result.documents] == URLS["topic"]


def test_research_ignores_document_content_written_by_final_llm_response():
    forged = AIMessage(
        content=json.dumps({"documents": [{"id": "fake", "content": "위조 본문"}]})
    )

    scenario = planned(SEARCH, FETCH, keep_fetched, forged)

    assert len(scenario.result.documents) == len(ALL_URLS)
    assert all(
        document.id != "fake" and "위조 본문" not in document.content
        for document in scenario.result.documents
    )


def test_research_stops_at_20_calls_including_initial_plan_retry():
    scenario = run_scenario(
        AIMessage(content="{}"),
        AIMessage(content=json.dumps(PLAN)),
        SEARCH,
        FETCH,
        keep_fetched,
        *[tool_response("unknown", [{}]) for _ in range(15)],
    )

    assert len(scenario.llm.calls) == 20
    assert [candidate.kind for candidate in scenario.result.nfr_candidates] == ["latency"]
    assert [document.url for document in scenario.result.documents] == ALL_URLS
    assert [document.content for document in scenario.result.documents] == [
        f"{url} p99 100ms\n\n{url} trade-off" for url in ALL_URLS
    ]


def test_research_returns_partial_evidence_when_topic_documents_are_missing():
    search_latency = tool_response("search", [{"query_id": "query-2"}])
    fetch_latency = tool_response("fetch", [{"query_id": "query-2"}])

    scenario = planned(search_latency, fetch_latency, keep_fetched, FINISH)

    assert len(scenario.llm.calls) == 5
    assert [candidate.kind for candidate in scenario.result.nfr_candidates] == ["latency"]
    assert [document.url for document in scenario.result.documents] == URLS["latency"]
    assert scenario.result.nfr_candidates[0].doc_ids == [
        document.id for document in scenario.result.documents
    ]


def test_research_fetches_only_top_three_unseen_urls_per_query(monkeypatch):
    urls = [f"https://docs.example/latency/{i}" for i in range(1, 6)]
    monkeypatch.setitem(URLS, "latency", urls)
    batch = tool_response("fetch", [{"query_id": "query-2"}])

    scenario = planned(SEARCH, batch, batch, FINISH)

    first_results = json.loads(latest_tools(scenario.llm.calls[3])[0]["content"])
    assert [item["url"] for item in first_results] == urls[:3]
    assert [item["rank"] for item in first_results] == [1, 2, 3]
    assert all(item["result"]["sentences"] for item in first_results)
    next_results = json.loads(latest_tools(scenario.llm.calls[4])[0]["content"])
    assert [item["url"] for item in next_results] == urls[3:]
    assert [item["rank"] for item in next_results] == [4, 5]


def test_fetch_failure_counts_toward_batch_size_and_next_call_moves_on(monkeypatch):
    urls = [f"https://docs.example/latency/{i}" for i in range(1, 5)]
    monkeypatch.setitem(URLS, "latency", urls)
    original = FetchTool.fetch
    attempted = []

    def fetch(self, url):
        attempted.append(url)
        return "fetch 실패: HTTP 403" if url == urls[0] else original(self, url)

    monkeypatch.setattr(FetchTool, "fetch", fetch)
    batch = tool_response("fetch", [{"query_id": "query-2"}])
    scenario = planned(SEARCH, batch, batch, FINISH)

    first = json.loads(latest_tools(scenario.llm.calls[3])[0]["content"])
    assert [item["url"] for item in first] == urls[:3]
    assert first[0]["result"] == "fetch 실패: HTTP 403"
    assert all(item["result"]["sentences"] for item in first[1:])
    second = json.loads(latest_tools(scenario.llm.calls[4])[0]["content"])
    assert [item["url"] for item in second] == urls[3:]
    assert sorted(attempted) == urls


def test_duplicate_fetch_calls_in_one_response_do_not_exceed_three_urls(monkeypatch):
    urls = [f"https://docs.example/latency/{i}" for i in range(1, 7)]
    monkeypatch.setitem(URLS, "latency", urls)
    calls = tool_response("fetch", [{"query_id": "query-2"}] * 2)

    scenario = planned(SEARCH, calls, FINISH)

    results = latest_tools(scenario.llm.calls[3])
    batches = [json.loads(m["content"]) for m in results if m["content"].startswith("[")]
    assert len(batches) == 1
    assert [item["url"] for item in batches[0]] == urls[:3]
    assert sum(m["content"].startswith("fetch 오류:") for m in results) == 1


def test_research_system_prompt_includes_source_policy_and_document_criteria():
    scenario = planned(FINISH)

    system = scenario.llm.calls[1][0]["content"]
    assert "# Source Policy" in system
    for tier in [
        "1순위: 공식 기술 문서·공식 Engineering / Technical Blog",
        "2순위: 논문·기술 Conference 발표",
        "3순위: 신뢰할 수 있는 제3자 기술 블로그·시스템 디자인 면접 자료",
    ]:
        assert tier in system
    assert "해당 NFR(주제 쿼리는 주제 자체)을 설계 관점에서 다루며" in system
    assert "수치·요구 수준·설계 선택 중 하나 이상" in system
    assert "광고성 글, 무관한 글, NFR 언급 없이 기능 소개만 있는 글" in system
    assert "같은 조건이면 Source Policy 상위 출처를 먼저 고른다." in system


def test_tool_schema_uses_exact_api_keys_and_required_arguments():
    properties = {
        "doc_id": {"type": "string"},
        "sentence_indices": {"type": "array", "items": {"type": "integer"}},
    }

    schema = runner._tool("keep", "남길 문단을 선택한다.", properties)

    assert schema == {
        "type": "function",
        "function": {
            "name": "keep",
            "strict": True,
            "description": "남길 문단을 선택한다.",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": ["doc_id", "sentence_indices"],
                "additionalProperties": False,
            },
        },
    }


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("search", {"query_id": "query-1", "extra": 1}),
        ("search", {"QUERY_ID": "query-1"}),
        ("search", {"query_id": 12}),
        ("fetch", {"query_id": "query-1", "extra": 1}),
        ("fetch", {"query_id": ["query-1"]}),
        ("keep", {"doc_id": "doc-a", "sentence_indices": [True]}),
        ("keep", {"doc_id": "doc-a", "sentence_indices": "1"}),
    ],
)
def test_tool_arguments_are_validated_before_execution(name, args):
    search, fetch = Mock(), Mock()
    session = runner._Session(
        runner.InitialResearchPlan.model_validate(PLAN), search, fetch
    )
    session.keep = Mock()

    result = session._call_tool(
        {"name": name, "args": args}, {"query-1": {URLS["topic"][0]}}
    )

    assert isinstance(result, str) and result.startswith(f"{name} 오류:")
    search.search.assert_not_called()
    fetch.fetch.assert_not_called()
    session.keep.keep.assert_not_called()
    assert not session.queries["query-1"].searched
    assert not session.queries["query-1"].seen


def test_research_passes_search_fetch_and_keep_definitions_to_bind_tools(monkeypatch):
    registered = []

    def bind_tools(self, tools):
        registered.append(tools)
        return self

    monkeypatch.setattr(FakeLLM, "bind_tools", bind_tools)

    planned(FINISH)

    assert registered == [runner.TOOLS]
    assert [tool["function"]["name"] for tool in registered[0]] == [
        "search",
        "fetch",
        "keep",
    ]


@pytest.mark.parametrize(
    ("notes", "expected_user"),
    [
        (None, "실시간 채팅 서비스"),
        ("메시지 유실 최소화", "실시간 채팅 서비스\n메시지 유실 최소화"),
    ],
)
def test_research_forwards_initial_messages_and_preserves_loop_roles_and_notes(
    notes, expected_user
):
    llm = FakeLLM(AIMessage(content=json.dumps(PLAN)), FINISH)

    run_research(
        InterviewBrief(
            topic="실시간 채팅 서비스", seniority=Seniority.MIDDLE, notes=notes
        ),
        load_catalog(CATALOG_DIR),
        llm,
        Mock(spec=SearchTool),
        Mock(spec=FetchTool),
    )

    assert [message["role"] for message in llm.calls[0]] == ["system", "user"]
    messages = llm.calls[1]
    assert [message["role"] for message in messages] == ["system", "user", "assistant"]
    assert [set(message) for message in messages] == [{"role", "content"}] * 3
    assert messages[1]["content"] == expected_user
    assert json.loads(messages[2]["content"]) == {
        **PLAN,
        "nfr_candidates": [
            {**candidate, "doc_ids": []} for candidate in PLAN["nfr_candidates"]
        ],
    }


def test_research_system_prompt_contains_query_mapping_and_numeric_limits():
    scenario = planned(FINISH)

    system = scenario.llm.calls[1][0]["content"]
    query_block = system.split("쿼리 ID와 검색어:\n", 1)[1].split("\n\n", 1)[0]
    assert json.loads(query_block) == {
        f"query-{i}": query for i, query in enumerate(PLAN["search_queries"], start=1)
    }
    assert f"쿼리당 최대 {runner.FETCH_BATCH}개씩" in system
    assert (
        f"NFR 쿼리는 keep한 문서 {runner.SUFFICIENT_DOCS}개, "
        f"주제 쿼리는 {runner.SUFFICIENT_DOCS_TOPIC}개가 필요하다."
    ) in system
    assert f"LLM 호출은 최대 {runner.MAX_AGENT_STEPS}회다." in system


def test_research_does_not_search_an_already_searched_query_again(monkeypatch):
    searched = []
    original = SearchTool.search

    def search(self, query, *, query_id):
        searched.append(query_id)
        return original(self, query, query_id=query_id)

    monkeypatch.setattr(SearchTool, "search", search)

    planned(SEARCH, SEARCH, FINISH)

    assert searched == ["query-1", "query-2", "query-3", "query-4"]


def test_search_accepts_only_query_id_and_uses_the_planned_search_text():
    search = Mock()
    search.search.return_value = []
    session = runner._Session(
        runner.InitialResearchPlan.model_validate(PLAN), search, Mock()
    )

    messages = session.execute(
        [{"id": "search-1", "name": "search", "args": {"query_id": "query-2"}}]
    )

    assert messages[0]["content"] == "[]"
    search.search.assert_called_once_with("chat latency", query_id="query-2")
    parameters = runner.TOOLS[0]["function"]["parameters"]
    assert parameters["properties"] == {"query_id": {"type": "string"}}
    assert parameters["required"] == ["query_id"]


def test_search_returns_an_error_for_unknown_query_id_without_calling_search():
    search = Mock()
    session = runner._Session(
        runner.InitialResearchPlan.model_validate(PLAN), search, Mock()
    )

    messages = session.execute(
        [{"id": "search-1", "name": "search", "args": {"query_id": "query-missing"}}]
    )

    assert messages[0]["content"].startswith("search 오류:")
    assert "query-missing" in messages[0]["content"]
    search.search.assert_not_called()


@pytest.mark.parametrize(
    "response", [SEARCH, tool_response("unknown", [{}])], ids=["search", "unknown-tool"]
)
def test_research_tool_messages_have_only_api_message_keys(response):
    scenario = planned(response, FINISH)

    results = latest_tools(scenario.llm.calls[-1])
    assert len(results) == len(response.tool_calls)
    for message in results:
        assert set(message) == {"role", "tool_call_id", "content"}
        assert message["role"] == "tool"
        assert isinstance(message["content"], str)


def test_research_serializes_keep_updates_to_the_same_document(monkeypatch):
    original = KeepTool.keep
    lock, overlap = Lock(), Event()
    active = 0

    def keep(self, doc_id, sentence_indices):
        nonlocal active
        with lock:
            active += 1
            if active > 1:
                overlap.set()
        try:
            # 병렬 호출이라면 두 번째 호출이 첫 번째의 상태 갱신 중에 진입한다.
            overlap.wait(timeout=0.2)
            return original(self, doc_id, sentence_indices)
        finally:
            with lock:
                active -= 1

    def keep_twice(messages):
        doc_id = fetched_documents(messages)[0]["doc_id"]
        return tool_response(
            "keep",
            [
                {"doc_id": doc_id, "sentence_indices": [3, 1]},
                {"doc_id": doc_id, "sentence_indices": [0]},
            ],
        )

    monkeypatch.setattr(KeepTool, "keep", keep)

    scenario = planned(SEARCH, FETCH, keep_twice, FINISH)

    assert not overlap.is_set()
    assert [
        json.loads(message["content"])["kept_documents"]
        for message in latest_tools(scenario.llm.calls[-1])
    ] == [
        1,
        1,
    ]
    assert len(scenario.result.documents) == 1
    url = URLS["topic"][0]
    assert (
        scenario.result.documents[0].content
        == f"제외\n\n{url} p99 100ms\n\n{url} trade-off"
    )


@pytest.mark.parametrize("stage", ["search", "fetch"])
def test_research_parallel_calls_return_successful_payloads(stage):
    responses = [AIMessage(content=json.dumps(PLAN)), SEARCH]
    barriers = {"search_barrier": Barrier(4)}
    if stage == "fetch":
        responses.append(FETCH)
        barriers = {"fetch_barrier": Barrier(len(ALL_URLS))}

    scenario = run_scenario(*responses, FINISH, **barriers)

    payloads = [
        json.loads(message["content"]) for message in latest_tools(scenario.llm.calls[-1])
    ]
    if stage == "search":
        assert [len(results) for results in payloads] == [1, 2, 1, 0]
    else:
        payloads = fetched_documents(scenario.llm.calls[-1])
        assert [document["url"] for document in payloads] == ALL_URLS
        assert all(document["sentences"] for document in payloads)


def test_research_reports_pending_documents_and_remaining_urls_to_llm():
    scenario = planned(SEARCH, FETCH, keep_fetched, FINISH)

    def state_at(index):
        system = scenario.llm.calls[index][0]["content"]
        return json.loads(system.split("# 현재 조사 상태\n", 1)[1])

    before_fetch = state_at(2)
    assert before_fetch["queries"]["query-2"]["next_fetch_urls"] == [
        {"rank": i, "url": url} for i, url in enumerate(URLS["latency"], start=1)
    ]
    before_keep = state_at(3)
    fetched = fetched_documents(scenario.llm.calls[3])
    assert before_keep["pending_documents"] == [
        {"doc_id": document["doc_id"], "query_id": query_id}
        for document, query_id in zip(
            fetched, ["query-1", "query-2", "query-2", "query-3"], strict=True
        )
    ]
    assert before_keep["queries"]["query-2"]["next_fetch_urls"] == []
    after_keep = state_at(4)
    assert after_keep["pending_documents"] == []
    assert after_keep["queries"]["query-2"]["kept_documents"] == 2


def test_research_drops_processed_history_but_preserves_evidence():
    scenario = planned(SEARCH, FETCH, keep_fetched, FINISH)

    before_keep = scenario.llm.calls[3]
    assert all("sentences" in doc for doc in fetched_documents(before_keep))
    after_keep = scenario.llm.calls[4]
    assert len(after_keep) == 3 + 1 + len(ALL_URLS)
    assert [m["tool_call_id"] for m in after_keep if m["role"] == "tool"] == [
        f"keep-{i}" for i in range(1, 5)
    ]
    assert "sentences" not in json.dumps(after_keep)
    state = json.loads(after_keep[0]["content"].split("# 현재 조사 상태\n", 1)[1])
    kept_ids = [doc_id for q in state["queries"].values() for doc_id in q["kept_doc_ids"]]
    assert set(kept_ids) == {doc.id for doc in scenario.result.documents}
    assert all("p99 100ms" in doc.content for doc in scenario.result.documents)
