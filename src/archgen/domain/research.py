"""Planner가 내놓는 조사 계획. 스키마는 docs/nfr-design.md를 따른다."""

from __future__ import annotations

import re
from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, Field, StringConstraints, model_validator

# 프롬프트와 스키마가 같은 숫자를 쓰도록 한곳에 둔다.
CANDIDATES_MIN, CANDIDATES_MAX = 3, 5
MAX_QUERIES = 6

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


class NFRCandidate(BaseModel):
    """문서로 검증하기 전의 NFR 가설."""

    kind: Kind
    reason: Text


class SearchQuery(BaseModel):
    """후보를 확인할 자료를 찾기 위한 검색어."""

    query: Text
    purpose: Text
    related_nfrs: list[Kind] = []


class ResearchPlan(BaseModel):
    """검색을 돌리기 전에 정하는 조사 범위."""

    topic_summary: Text
    # 개수는 중복을 걸러낸 뒤 검사한다(아래 검증기). 스키마에는 그대로 실어
    # 구조화 출력이 생성 단계에서 모델을 3~5개로 묶게 한다.
    nfr_candidates: Annotated[
        list[NFRCandidate],
        Field(json_schema_extra={"minItems": CANDIDATES_MIN, "maxItems": CANDIDATES_MAX}),
    ]
    search_queries: Annotated[list[SearchQuery], Field(max_length=MAX_QUERIES)]

    @model_validator(mode="after")
    def _tidy_candidate_references(self) -> Self:
        """겹친 후보·검색어는 먼저 나온 것만 남기고, 후보에 없는 kind 참조는 지운다.

        걸러낸 뒤 후보 수가 3~5개 밖이면 코드로 맞출 수 없으니 거부한다(재시도 대상).
        """
        unique: dict[str, NFRCandidate] = {}
        for candidate in self.nfr_candidates:
            unique.setdefault(candidate.kind, candidate)
        if not CANDIDATES_MIN <= len(unique) <= CANDIDATES_MAX:
            raise ValueError(
                f"nfr_candidates: 서로 다른 후보가 {len(unique)}개다. "
                f"후보는 서로 다른 kind로 {CANDIDATES_MIN}~{CANDIDATES_MAX}개여야 한다."
            )
        self.nfr_candidates = list(unique.values())

        # 같은 검색을 두 번 돌리지 않는다. 대소문자·공백 차이는 같은 검색어로 본다.
        queries: dict[str, SearchQuery] = {}
        for query in self.search_queries:
            queries.setdefault(" ".join(query.query.casefold().split()), query)
        self.search_queries = list(queries.values())

        # 검색어는 남긴다. 참조만 틀렸을 뿐 가져온 문서는 NFR Agent가 판단한다.
        for query in self.search_queries:
            refs = [ref for ref in query.related_nfrs if ref in unique]
            query.related_nfrs = list(dict.fromkeys(refs))
        return self
