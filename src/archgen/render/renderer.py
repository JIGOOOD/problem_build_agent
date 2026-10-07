"""하네스를 통과한 NFRExport를 면접관이 쓸 Markdown 루브릭으로 옮긴다.

LLM 없이 코드로만 렌더한다. 섹션 순서·헤딩·표 구조를 템플릿이 고정한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from archgen.domain.brief import InterviewBrief
from archgen.domain.nfr import (
    ConfirmedNFR,
    NFRExport,
    NFRTarget,
    RubricCriterion,
    RubricLevel,
    Tradeoff,
)

_ENV = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
    # 변수 이름을 틀리면 빈 문자열로 조용히 넘어가지 않고 실패한다.
    undefined=StrictUndefined,
)


@dataclass(frozen=True)
class _Section:
    """criterion 하나를 렌더하는 데 필요한 것을 id 참조를 풀어 모아 둔다."""

    criterion: RubricCriterion
    nfr: ConfirmedNFR
    target: str | None
    tradeoffs: list[Tradeoff]
    # LLM이 레벨을 어떤 순서로 내든 채점표는 0점부터 읽히게 한다.
    levels: list[RubricLevel]


def render_rubric(export: NFRExport, brief: InterviewBrief) -> str:
    """cross-ref 하네스를 통과한 export를 받는다. 깨진 참조는 KeyError·IndexError로 드러난다."""
    nfrs = {nfr.id: nfr for nfr in export.confirmed_nfrs}
    sections = [
        _section(c, nfrs[c.related_nfr_ids[0]], export) for c in export.rubric.criteria
    ]
    return _ENV.get_template("nfr_rubric.md.j2").render(
        brief=brief,
        sections=sections,
        total_weight=sum(c.weight for c in export.rubric.criteria),
    )


def _section(
    criterion: RubricCriterion, nfr: ConfirmedNFR, export: NFRExport
) -> _Section:
    return _Section(
        criterion=criterion,
        nfr=nfr,
        target=_format_target(nfr.target),
        tradeoffs=[t for t in export.tradeoffs if nfr.id in t.related_nfr_ids],
        levels=sorted(criterion.levels, key=lambda level: level.score),
    )


def _format_target(target: NFRTarget | None) -> str | None:
    """정량 목표만 한 줄로 만든다. 정성 목표는 statement의 요약이라 따로 쓰지 않는다."""
    if target is None:
        return None
    value = _format_number(target.value) if target.value is not None else ""
    # 숫자와 단위는 띄워 쓰되 %만 붙인다: 500 ms, 10,000 msg/s, 99.9%
    joiner = "" if target.unit == "%" else " "
    measure = joiner.join(part for part in (value, target.unit) if part)
    return " ".join(part for part in (target.condition, measure) if part)


def _format_number(value: float) -> str:
    """천 단위 콤마를 넣고 지수 표기를 쓰지 않는다: 1,000,000 / 1,234.5 / 0.0001"""
    text = format(Decimal(str(value)), ",f")
    return text.rstrip("0").rstrip(".") if "." in text else text
