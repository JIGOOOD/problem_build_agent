"""초기 조사 계획과 search/fetch/keep 도구 호출을 연결한다."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any, Protocol

from langchain_core.messages import AIMessage
from langchain_core.messages.utils import convert_to_openai_messages

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.research import (
    FETCH_BATCH,
    MAX_AGENT_STEPS,
    MAX_KEEP_CHARS,
    SUFFICIENT_DOCS,
    SUFFICIENT_DOCS_TOPIC,
    FetchResult,
    InitialResearchPlan,
    NFRCandidate,
    ResearchResult,
    SearchResult,
)
from archgen.research.agent import bind_initial_research_model, plan_initial_research
from archgen.research.keep import KeepTool
from archgen.retrieval.crawler import FetchTool
from archgen.retrieval.search import SearchTool
from archgen.templating import template_env


class ResearchLLM(Protocol):
    def bind(self, **kwargs: Any) -> ResearchLLM: ...

    def invoke(self, messages: list[dict[str, Any]]) -> AIMessage: ...

    def bind_tools(self, tools: list[dict[str, Any]]) -> ResearchLLM: ...


def _tool(name: str, description: str, properties: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "strict": True,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(properties),
                "additionalProperties": False,
            },
        },
    }


TOOLS = [
    _tool(
        "search",
        "query_id만 전달한다. 해당 ID의 초기 계획 검색어를 코드가 찾아 검색한다.",
        {
            "query_id": {"type": "string"},
        },
    ),
    _tool(
        "fetch",
        f"query_id만 전달한다. 코드가 해당 쿼리의 순위가 높은 미확인 URL을 {FETCH_BATCH}개씩 가져온다. 남은 URL이 적으면 남은 만큼 가져온다.",
        {
            "query_id": {"type": "string"},
        },
    ),
    _tool(
        "keep",
        f"새 문장 번호를 중요도순으로 전달한다. 재호출은 기존 선택을 유지하고 남은 예산에 누적한다. 중복 없이 문서당 {MAX_KEEP_CHARS}자 안에서 온전한 문장만 선택한다.",
        {
            "doc_id": {"type": "string"},
            "sentence_indices": {"type": "array", "items": {"type": "integer"}},
        },
    ),
]


def _validate_tool_args(name: str, args: dict) -> None:
    """현재 세 도구의 문자열·정수 배열 인자를 실행 전에 검사한다."""
    definition = next(
        tool["function"] for tool in TOOLS if tool["function"]["name"] == name
    )
    properties = definition["parameters"]["properties"]
    if not isinstance(args, dict) or set(args) != set(properties):
        raise ValueError(f"필수 키는 정확히 {', '.join(properties)}여야 한다.")
    for key, schema in properties.items():
        value = args[key]
        if schema["type"] == "string":
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{key}는 빈 값이 아닌 문자열이어야 한다.")
        elif (
            not isinstance(value, list)
            or not value
            or any(type(index) is not int or index < 0 for index in value)
        ):
            raise ValueError(f"{key}는 0 이상 정수의 비어 있지 않은 배열이어야 한다.")


@dataclass
class _Query:
    text: str
    kind: str | None
    searched: bool = False
    results: list[SearchResult] = field(default_factory=list)
    seen: set[str] = field(default_factory=set)


class _Session:
    def __init__(self, plan: InitialResearchPlan, search: SearchTool, fetch: FetchTool):
        self.plan = plan
        self.search = search
        self.fetch = fetch
        self.keep = KeepTool()
        self.queries = {
            f"query-{i}": _Query(query.query, query.related_nfr)
            for i, query in enumerate(plan.search_queries, start=1)
        }
        self.doc_queries: dict[str, str] = {}
        self.pending: list[str] = []
        self.lock = Lock()

    def _search(self, args: dict) -> list[SearchResult] | str:
        query_id = args["query_id"]
        query = self.queries[query_id]
        with self.lock:
            if query.searched:
                return "search 오류: 이미 검색한 쿼리다."
            query.searched = True
        return self.search.search(query.text, query_id=query_id)

    def _fetch(self, args: dict, allowed: dict[str, set[str]]) -> list[dict] | str:
        query_id = args["query_id"]
        query = self.queries[query_id]
        with self.lock:
            batch = [
                result
                for result in query.results
                if result.url in allowed[query_id] and result.url not in query.seen
            ]
            if not batch:
                return "fetch 오류: 이번 배치에서 가져올 미확인 URL이 없다."
            query.seen.update(result.url for result in batch)
        with ThreadPoolExecutor(max_workers=len(batch)) as pool:
            results = list(pool.map(self.fetch.fetch, [item.url for item in batch]))
        return [
            {"url": item.url, "rank": item.rank, "result": result}
            for item, result in zip(batch, results, strict=True)
        ]

    def _fetch_batch_urls(self) -> dict[str, set[str]]:
        allowed = {}
        for query_id, query in self.queries.items():
            unseen = [
                result.url for result in query.results if result.url not in query.seen
            ]
            allowed[query_id] = set(unseen[:FETCH_BATCH])
        return allowed

    def _call_tool(
        self, call: dict, allowed: dict[str, set[str]]
    ) -> list[SearchResult] | list[dict] | dict | str:
        name, args = call["name"], call["args"]
        try:
            _validate_tool_args(name, args)
            if name == "search":
                return self._search(args)
            if name == "fetch":
                return self._fetch(args, allowed)
            return self.keep.keep(**args)
        except (KeyError, TypeError, ValueError) as error:
            return f"{name} 오류: {error}"

    def _record_result(
        self,
        call: dict,
        result: list[SearchResult] | list[dict] | dict | str,
        message: dict,
    ) -> None:
        if isinstance(result, list) and call["name"] == "search":
            query_id = call["args"]["query_id"]
            self.queries[query_id].results = sorted(result, key=lambda item: item.rank)
            message["content"] = json.dumps(
                [item.model_dump() for item in result], ensure_ascii=False
            )
        elif isinstance(result, list):
            query_id = call["args"]["query_id"]
            payload = []
            for item in result:
                fetched = item["result"]
                if isinstance(fetched, FetchResult):
                    self.doc_queries.setdefault(fetched.doc_id, query_id)
                    self.keep.register(query_id, fetched, message)
                    self.pending.append(fetched.doc_id)
                    fetched = fetched.model_dump()
                payload.append({**item, "result": fetched})
            message["content"] = json.dumps(payload, ensure_ascii=False)
        elif isinstance(result, dict):
            message["content"] = json.dumps(result, ensure_ascii=False)
        else:
            message["content"] = result

    def execute(self, calls: list[dict]) -> list[dict]:
        """같은 단계는 묶어 실행하고, 결과는 원래 호출 순서로 전달한다."""
        previous_batch, self.pending = self.pending, []
        messages = [
            {"role": "tool", "tool_call_id": call["id"], "content": "알 수 없는 도구다."}
            for call in calls
        ]
        for name in ("search", "fetch", "keep"):
            indices = [i for i, call in enumerate(calls) if call["name"] == name]
            if not indices:
                continue
            allowed = self._fetch_batch_urls()
            if name == "keep":
                # keep은 선택 문서와 문장 목록을 갱신하므로 순서대로 실행한다.
                results = [self._call_tool(calls[index], allowed) for index in indices]
            else:
                with ThreadPoolExecutor(max_workers=len(indices)) as pool:
                    futures = [
                        pool.submit(self._call_tool, calls[index], allowed)
                        for index in indices
                    ]
                    results = [future.result() for future in futures]
            for index, result in zip(indices, results, strict=True):
                self._record_result(calls[index], result, messages[index])
        self.keep.finish_batch(previous_batch)
        return messages

    def progress(self) -> dict:
        """판정할 문서와 쿼리별 다음 행동을 LLM에게 알려준다."""
        allowed = self._fetch_batch_urls()
        queries = {}
        for query_id, query in self.queries.items():
            kept_ids = [
                doc_id
                for doc_id in self.keep.documents
                if self.doc_queries[doc_id] == query_id
            ]
            kept = len(kept_ids)
            required = SUFFICIENT_DOCS_TOPIC if query.kind is None else SUFFICIENT_DOCS
            queries[query_id] = {
                "related_nfr": query.kind,
                "searched": query.searched,
                "kept_documents": kept,
                "kept_doc_ids": kept_ids,
                "required_documents": required,
                "next_fetch_urls": [
                    {"rank": result.rank, "url": result.url}
                    for result in query.results
                    if kept < required and result.url in allowed[query_id]
                ],
            }
        return {
            "pending_documents": [
                {"doc_id": doc_id, "query_id": self.doc_queries[doc_id]}
                for doc_id in self.pending
                if doc_id not in self.keep.documents
            ],
            "queries": queries,
        }

    def result(self) -> ResearchResult:
        candidates = []
        for candidate in self.plan.nfr_candidates:
            query_id = next(
                qid for qid, query in self.queries.items() if query.kind == candidate.kind
            )
            doc_ids = [
                doc_id
                for doc_id in self.keep.documents
                if self.doc_queries[doc_id] == query_id
            ]
            if len(doc_ids) >= SUFFICIENT_DOCS:
                candidates.append(
                    NFRCandidate(
                        kind=candidate.kind, reason=candidate.reason, doc_ids=doc_ids
                    )
                )
        return ResearchResult(
            topic_summary=self.plan.topic_summary,
            nfr_candidates=candidates,
            documents=list(self.keep.documents.values()),
        )


def _build_messages(brief: InterviewBrief, session: _Session) -> list[dict]:
    env = template_env(Path(__file__).parent / "templates")
    system = env.get_template("tools_system.md.j2").render(
        queries={
            qid: {"query": q.text, "related_nfr": q.kind}
            for qid, q in session.queries.items()
        },
        fetch_batch=FETCH_BATCH,
        sufficient_docs=SUFFICIENT_DOCS,
        sufficient_docs_topic=SUFFICIENT_DOCS_TOPIC,
        max_agent_steps=MAX_AGENT_STEPS,
        max_keep_chars=MAX_KEEP_CHARS,
    )
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": brief.topic + (f"\n{brief.notes}" if brief.notes else ""),
        },
        {"role": "assistant", "content": session.plan.model_dump_json()},
    ]


def run_research(
    brief: InterviewBrief,
    catalog: NFRCatalog,
    llm: ResearchLLM,
    search: SearchTool,
    fetch: FetchTool,
) -> ResearchResult:
    calls = 0

    def invoke(model, messages):
        nonlocal calls
        calls += 1
        return model.invoke(messages)

    initial_model = bind_initial_research_model(llm)
    plan = plan_initial_research(
        brief, catalog, lambda messages: invoke(initial_model, messages).content
    )
    session = _Session(plan, search, fetch)
    messages = _build_messages(brief, session)
    system = messages[0]["content"]
    model = llm.bind_tools(TOOLS)
    while calls < MAX_AGENT_STEPS:
        messages[0]["content"] = (
            system
            + "\n\n# 현재 조사 상태\n"
            + json.dumps(session.progress(), ensure_ascii=False, indent=2)
        )
        response = invoke(model, messages)
        # 이전 도구 왕복은 상태에 반영됐다. 다음 판단에는 직전 결과만 전달한다.
        del messages[3:]
        messages.append(convert_to_openai_messages(response))
        if not response.tool_calls:
            break
        messages.extend(session.execute(response.tool_calls))
    session.keep.finish_batch(session.pending)
    return session.result()
