"""Research Agent의 조사 계획, 도구 결과와 최종 근거."""

from __future__ import annotations

import logging
import re
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

_LOGGER = logging.getLogger(__name__)

# 프롬프트와 스키마가 같은 숫자를 쓰도록 한곳에 둔다.
CANDIDATES_MIN, CANDIDATES_MAX = 3, 5
MAX_QUERIES = 6
RESULTS_PER_QUERY = 10
FETCH_BATCH = 3
SUFFICIENT_DOCS = 2
SUFFICIENT_DOCS_TOPIC = 1
MAX_AGENT_STEPS = 20
MAX_CONTENT_CHARS = 12000
MAX_KEEP_CHARS = 2000

# 코드로 고칠 수 있는 것은 고치고, 고칠 수 없는 것만 거부한다. 거부하면 LLM 재시도(비용)가 든다.
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _to_snake_case(value: object) -> object:
    """`Fault Tolerance`, `fault-tolerance`, `fault__tolerance_`를 모두 `fault_tolerance`로 맞춘다."""
    if isinstance(value, str):
        return re.sub(r"[\s\-_]+", "_", value.lower()).strip("_")
    return value


# kind는 Catalog 이름·NFR Agent의 kind와 맞춰 볼 키다. 정리한 뒤에도 snake_case가 아니면 거부한다.
Kind = Annotated[
    str,
    BeforeValidator(_to_snake_case),
    StringConstraints(pattern=r"^[a-z][a-z0-9_]*$"),
]


class SearchResult(BaseModel):
    """검색 순서대로 선택한 URL과 그 URL을 찾은 쿼리."""

    query_id: str
    url: str
    title: str
    rank: int


class Sentence(BaseModel):
    index: int
    text: str


class FetchResult(BaseModel):
    doc_id: str
    url: str
    title: str
    sentences: list[Sentence]


class Document(BaseModel):
    id: str
    url: str
    title: str
    content: str


class NFRCandidate(BaseModel):
    """NFR 후보. 조사 전에는 근거 문서 목록이 비어 있다."""

    kind: Kind
    reason: Text
    doc_ids: list[str] = Field(default_factory=list)


class ResearchResult(BaseModel):
    topic_summary: str
    nfr_candidates: list[NFRCandidate]
    documents: list[Document]


class InitialSearchQuery(BaseModel):
    """Research Agent가 주제 또는 후보 하나를 검증할 검색어."""

    query: Text
    related_nfr: Kind | None


class InitialResearchPlan(BaseModel):
    """Research Agent가 검색을 시작하기 전에 만드는 초기 계획."""

    topic_summary: Text
    nfr_candidates: list[NFRCandidate]
    search_queries: list[InitialSearchQuery]

    @field_validator("search_queries", mode="before")
    @classmethod
    def _remove_blank_queries(cls, value: object) -> object:
        if not isinstance(value, list):
            return value
        return [
            item
            for item in value
            if not (
                isinstance(item, dict)
                and isinstance(item.get("query"), str)
                and not item["query"].strip()
            )
        ]

    @model_validator(mode="after")
    def _tidy_and_validate(self) -> Self:
        candidates: dict[str, NFRCandidate] = {}
        for candidate in self.nfr_candidates:
            candidates.setdefault(candidate.kind, candidate)
        queries: dict[str, InitialSearchQuery] = {}
        for query in self.search_queries:
            queries.setdefault(" ".join(query.query.casefold().split()), query)
        self.search_queries = []
        for query in queries.values():
            kind = query.related_nfr
            if kind is not None and kind not in candidates:
                if len(candidates) >= CANDIDATES_MAX:
                    _LOGGER.warning(
                        "후보 상한 초과로 검색어를 제거한다: kind=%s, query=%s",
                        kind,
                        query.query,
                    )
                    continue
                candidates[kind] = NFRCandidate(
                    kind=kind, reason=f"계획 검색어에서 추가된 후보: {query.query}"
                )
                _LOGGER.warning(
                    "계획 검색어에서 후보를 추가한다: kind=%s, query=%s",
                    kind,
                    query.query,
                )
            self.search_queries.append(query)
        self.nfr_candidates = list(candidates.values())
        if not CANDIDATES_MIN <= len(self.nfr_candidates) <= CANDIDATES_MAX:
            raise ValueError(
                f"nfr_candidates: 후보는 {CANDIDATES_MIN}~{CANDIDATES_MAX}개여야 한다. "
                f"현재 {len(self.nfr_candidates)}개다."
            )
        topic_count = sum(query.related_nfr is None for query in self.search_queries)
        if topic_count != 1:
            raise ValueError(
                f"search_queries: 주제 쿼리는 정확히 1개여야 한다. 현재 {topic_count}개다."
            )
        for kind in candidates:
            count = sum(query.related_nfr == kind for query in self.search_queries)
            if count != 1:
                raise ValueError(
                    f"search_queries: 후보 {kind}의 쿼리는 1개여야 한다. 현재 {count}개다."
                )
        if len(self.search_queries) > MAX_QUERIES:
            raise ValueError(f"search_queries: 쿼리는 {MAX_QUERIES}개 이하여야 한다.")
        return self
