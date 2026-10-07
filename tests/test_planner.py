import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import NFRCatalog, load_catalog
from archgen.domain.research import CANDIDATES_MAX, CANDIDATES_MIN, MAX_QUERIES
from archgen.paths import CATALOG_DIR
from archgen.research.planner import build_planner_prompt

BRIEF = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간 채팅 시스템 설계")


@pytest.fixture
def catalog() -> NFRCatalog:
    return load_catalog(CATALOG_DIR)


def test_prompt_carries_the_brief(catalog: NFRCatalog) -> None:
    prompt = build_planner_prompt(BRIEF, catalog)

    assert BRIEF.topic in prompt
    assert str(BRIEF.seniority) in prompt


def test_prompt_embeds_the_whole_catalog_block(catalog: NFRCatalog) -> None:
    """카탈로그는 M0의 직렬화 결과를 그대로 넣는다. 일부만 들어가면 후보가 치우친다."""
    assert catalog.to_prompt_block() in build_planner_prompt(BRIEF, catalog)


def test_prompt_lists_the_three_source_tiers_in_order(catalog: NFRCatalog) -> None:
    prompt = build_planner_prompt(BRIEF, catalog)
    tiers = [prompt.index(f"{n}순위") for n in (1, 2, 3)]

    assert tiers == sorted(tiers)


def test_prompt_numbers_match_the_plan_schema(catalog: NFRCatalog) -> None:
    """프롬프트가 요구하는 개수와 ResearchPlan이 받아들이는 개수가 어긋나면 파싱이 실패한다."""
    prompt = build_planner_prompt(BRIEF, catalog)

    assert f"{CANDIDATES_MIN}~{CANDIDATES_MAX}개" in prompt
    assert f"{MAX_QUERIES}개 이하" in prompt


def test_prompt_states_catalog_is_a_reference_not_a_menu(catalog: NFRCatalog) -> None:
    """Catalog를 메뉴로 읽으면 주제와 무관하게 6개를 기계적으로 고른다."""
    assert "메뉴가 아니다" in build_planner_prompt(BRIEF, catalog)


def test_prompt_includes_user_focus_only_when_given(catalog: NFRCatalog) -> None:
    focused = InterviewBrief(
        seniority=Seniority.SENIOR, topic=BRIEF.topic, notes="장애 시 가용성"
    )

    with_notes = build_planner_prompt(focused, catalog)
    without_notes = build_planner_prompt(BRIEF, catalog)

    assert "- 사용자 중점 요구사항: 장애 시 가용성" in with_notes.splitlines()
    assert "사용자 중점 요구사항" not in without_notes


def test_multi_line_notes_stay_on_one_line(catalog: NFRCatalog) -> None:
    """둘째 줄부터 입력 목록 밖으로 떨어지지 않게 한 줄로 접는다."""
    focused = InterviewBrief(
        seniority=Seniority.SENIOR, topic=BRIEF.topic, notes="장애 시 가용성\n  지연"
    )

    lines = build_planner_prompt(focused, catalog).splitlines()

    assert "- 사용자 중점 요구사항: 장애 시 가용성 지연" in lines


def test_prompt_is_the_same_for_the_same_input(catalog: NFRCatalog) -> None:
    """같은 입력이면 같은 프롬프트여야 Day 8 캐시 재생과 비교가 성립한다."""
    assert build_planner_prompt(BRIEF, catalog) == build_planner_prompt(BRIEF, catalog)


@pytest.mark.parametrize("leftover", ["{{", "}}", "{%", "%}", "\n\n\n", " \n"])
def test_prompt_has_no_template_leftovers(catalog: NFRCatalog, leftover: str) -> None:
    assert leftover not in build_planner_prompt(BRIEF, catalog)
