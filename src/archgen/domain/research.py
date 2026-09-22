"""Planner가 내놓는 조사 계획. 스키마는 docs/nfr-design.md를 따른다."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class NFRCandidate(BaseModel):
    """문서로 검증하기 전의 NFR 가설."""

    kind: str
    reason: str


class SearchQuery(BaseModel):
    """후보를 확인할 자료를 찾기 위한 검색어."""

    query: str
    purpose: str
    related_nfrs: list[str] = []


class ResearchPlan(BaseModel):
    """검색을 돌리기 전에 정하는 조사 범위."""

    topic_summary: str
    nfr_candidates: Annotated[list[NFRCandidate], Field(min_length=3, max_length=5)]
    search_queries: Annotated[list[SearchQuery], Field(max_length=6)]
