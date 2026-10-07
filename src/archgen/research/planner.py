"""Research Planner 프롬프트를 조립한다. 스펙은 docs/nfr-design.md의 Research Planner."""

from __future__ import annotations

from pathlib import Path

from archgen.domain.brief import InterviewBrief
from archgen.domain.catalog import NFRCatalog
from archgen.domain.research import (
    CANDIDATES_MAX,
    CANDIDATES_MIN,
    MAX_QUERIES,
)
from archgen.templating import template_env

_ENV = template_env(Path(__file__).parent / "templates")
# 입력 목록의 한 항목이 한 줄을 차지하도록 줄바꿈·연속 공백을 접는다.
_ENV.filters["one_line"] = lambda text: " ".join(text.split())


Message = dict[str, str]


def build_planner_messages(brief: InterviewBrief, catalog: NFRCatalog) -> list[Message]:
    """system(바뀌지 않는 지시) + user(실행마다 바뀌는 입력).

    system이 brief와 무관해야 API 프롬프트 캐시를 탄다. 개수 제약은 ResearchPlan과 같은 상수를 쓴다.
    """
    system = _ENV.get_template("planner_system.md.j2").render(
        catalog_block=catalog.to_prompt_block(),
        candidates_min=CANDIDATES_MIN,
        candidates_max=CANDIDATES_MAX,
        max_queries=MAX_QUERIES,
    )
    user = _ENV.get_template("planner_user.md.j2").render(brief=brief)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
