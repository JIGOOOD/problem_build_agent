"""하네스를 통과한 NFRExport를 면접관이 쓸 Markdown 루브릭으로 옮긴다.

LLM 없이 코드로만 렌더한다. 섹션 순서·헤딩·표 구조를 템플릿이 고정한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from archgen.domain.brief import InterviewBrief
from archgen.domain.nfr import (
    ConfirmedNFR,
    NFRExport,
    NFRTarget,
    RubricCriterion,
    RubricLevel,
)
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")


def _cell(text: str) -> str:
    """표 칸에 넣는다. `|`는 칸을 나누고 줄바꿈은 행을 끊으므로 바꿔 쓴다."""
    return "<br>".join(text.replace("|", "\\|").splitlines())


def _heading(text: str) -> str:
    """헤딩에 넣는다. 헤딩은 한 줄이어야 해서 줄바꿈·연속 공백을 공백 하나로 접는다."""
    return " ".join(text.split())


_ENV.filters["cell"] = _cell
_ENV.filters["heading"] = _heading


def _nfr_name(kind: str) -> str:
    return {"latency": "Low Latency", "throughput": "High Throughput"}.get(
        kind, kind.replace("_", " ").title()
    )


_ENV.filters["nfr_name"] = _nfr_name


@dataclass(frozen=True)
class _Section:
    """criterion 하나를 렌더하는 데 필요한 것을 id 참조를 풀어 모아 둔다."""

    criterion: RubricCriterion
    nfr: ConfirmedNFR
    target: str | None
    number: int
    # LLM이 레벨을 어떤 순서로 내든 채점표는 0점부터 읽히게 한다.
    levels: list[RubricLevel]


def render_rubric(export: NFRExport, brief: InterviewBrief) -> str:
    """cross-ref 하네스를 통과한 export를 받는다. 깨진 참조는 KeyError·IndexError로 드러난다."""
    nfrs = {nfr.id: nfr for nfr in export.confirmed_nfrs}
    sections = [
        _section(c, nfrs[c.related_nfr_ids[0]], i)
        for i, c in enumerate(export.rubric.criteria, 1)
    ]
    return _ENV.get_template("nfr_rubric.md.j2").render(
        brief=brief,
        sections=sections,
        nfrs=export.confirmed_nfrs,
        nfr_numbers={nfr.id: i for i, nfr in enumerate(export.confirmed_nfrs, 1)},
        total_weight=sum(c.weight for c in export.rubric.criteria),
    )


def _section(criterion: RubricCriterion, nfr: ConfirmedNFR, number: int) -> _Section:
    return _Section(
        criterion=criterion,
        nfr=nfr,
        target=_format_target(nfr.target),
        number=number,
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
