"""LLM이 만들어내는 루브릭 산출물. 스키마는 docs/rubric-format.md를 따른다."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field, model_validator


class NFRTarget(BaseModel):
    """근거 문서에서 그대로 읽어낸 정량 목표."""

    value: float | None = None
    unit: str | None = None
    condition: str | None = None


class ConfirmedNFR(BaseModel):
    """크롤한 근거로 확인을 마친 NFR."""

    id: str
    kind: str
    statement: str
    rationale: str
    target: NFRTarget | None = None
    qualitative_target: str | None = None
    evidence_refs: list[str] = []

    @model_validator(mode="after")
    def _require_exactly_one_target(self) -> Self:
        """목표가 없으면 채점할 수 없고, 둘 다 있으면 채점 기준이 갈린다."""
        if bool(self.target) == bool(self.qualitative_target):
            raise ValueError(
                "target 또는 qualitative_target 중 정확히 하나만 있어야 한다"
            )
        return self


class Tradeoff(BaseModel):
    """설계 선택 사이의 상충. 영향을 받는 NFR에 연결된다."""

    id: str
    related_nfr_ids: list[str] = []
    description: str
    evidence_refs: list[str] = []


class RubricLevel(BaseModel):
    """criterion의 0~3점 구간 하나."""

    score: int = Field(ge=0, le=3)
    descriptor: str


class RubricCriterion(BaseModel):
    """NFR 하나만 담당하는 채점 단위."""

    id: str
    title: str
    description: str
    related_nfr_ids: list[str] = []
    weight: float
    levels: list[RubricLevel] = []


class Rubric(BaseModel):
    """루브릭의 NFR 섹션."""

    criteria: list[RubricCriterion] = []


class NFRExport(BaseModel):
    """NFR Agent가 주제 하나에 대해 내놓는 전체 산출물."""

    confirmed_nfrs: list[ConfirmedNFR] = []
    tradeoffs: list[Tradeoff] = []
    rubric: Rubric
