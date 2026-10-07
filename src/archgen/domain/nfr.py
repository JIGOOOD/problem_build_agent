"""LLM이 만들어내는 루브릭 산출물. 스키마는 docs/rubric-format.md를 따른다."""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator

# id와 id를 가리키는 참조. LLM이 붙인 앞뒤 공백은 양쪽에서 똑같이 잘라내 서로 어긋나지
# 않게 하고, 잘라낸 뒤 비면 거부한다. 빈 id끼리는 참조가 맞아 cross-ref를 조용히 통과한다.
Id = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
# 사람이 읽는 본문. 비어 있으면 하네스를 통과해 채점표에 빈칸으로 렌더되므로 여기서 거부한다.
# 레벨 descriptor는 하네스 core.levels(LEVEL_DESCRIPTOR_MISSING)가 지적하므로 여기에 두지 않는다.
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class NFRTarget(BaseModel):
    """근거 문서에서 그대로 읽어낸 정량 목표."""

    # NaN·무한대는 그대로 렌더되면 `NaN ms`가 된다.
    value: float | None = Field(default=None, allow_inf_nan=False)
    unit: str | None = None
    condition: str | None = None


class ConfirmedNFR(BaseModel):
    """크롤한 근거로 확인을 마친 NFR."""

    id: Id
    kind: Text
    statement: Text
    rationale: Text
    target: NFRTarget | None = None
    qualitative_target: Text | None = None
    evidence_refs: list[Id] = []

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

    id: Id
    related_nfr_ids: list[Id] = []
    description: Text
    evidence_refs: list[Id] = []


class RubricLevel(BaseModel):
    """criterion의 0~3점 구간 하나."""

    score: int = Field(ge=0, le=3)
    descriptor: str


class RubricCriterion(BaseModel):
    """NFR 하나만 담당하는 채점 단위."""

    id: Id
    title: Text
    description: Text
    related_nfr_ids: list[Id] = []
    weight: int  # 자연수 배점. 범위와 합은 하네스 core.weight-sum이 본다.
    levels: list[RubricLevel] = []

    @field_validator("weight", mode="before")
    @classmethod
    def _reject_bool_weight(cls, value: object) -> object:
        """pydantic은 true를 1로 바꿔 받는다. 배점이 조용히 1점이 되는 걸 막는다."""
        if isinstance(value, bool):
            # TypeError는 ValidationError로 바뀌지 않고 그대로 새어 나간다.
            raise ValueError("weight는 bool이 아니라 자연수여야 한다")  # noqa: TRY004
        return value


class Rubric(BaseModel):
    """루브릭의 NFR 섹션."""

    criteria: list[RubricCriterion] = []


class NFRExport(BaseModel):
    """NFR Agent가 주제 하나에 대해 내놓는 전체 산출물."""

    confirmed_nfrs: list[ConfirmedNFR] = []
    tradeoffs: list[Tradeoff] = []
    rubric: Rubric
