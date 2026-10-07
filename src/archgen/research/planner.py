"""Research Planner 프롬프트를 조립한다. 스펙은 docs/nfr-design.md의 Research Planner."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.research import CANDIDATES_MAX, CANDIDATES_MIN, MAX_QUERIES

_ENV = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
    # 변수 이름을 틀리면 빈 문자열로 조용히 넘어가지 않고 실패한다.
    undefined=StrictUndefined,
)
# 입력 목록의 한 항목이 한 줄을 차지하도록 줄바꿈·연속 공백을 접는다.
_ENV.filters["one_line"] = lambda text: " ".join(text.split())


def build_planner_prompt(brief: InterviewBrief, catalog: NFRCatalog) -> str:
    """같은 입력이면 같은 프롬프트를 낸다. 개수 제약은 ResearchPlan 스키마와 같은 상수를 쓴다."""
    return _ENV.get_template("planner.md.j2").render(
        brief=brief,
        catalog_block=catalog.to_prompt_block(),
        candidates_min=CANDIDATES_MIN,
        candidates_max=CANDIDATES_MAX,
        max_queries=MAX_QUERIES,
    )
