import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.catalog import NFRCatalog, load_catalog
from archgen.domain.research import CANDIDATES_MAX, CANDIDATES_MIN, MAX_QUERIES
from archgen.paths import CATALOG_DIR
from archgen.research.planner import build_planner_messages

BRIEF = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간 채팅 시스템 설계")
FOCUSED = InterviewBrief(
    seniority=Seniority.SENIOR, topic=BRIEF.topic, notes="장애 시 가용성"
)


@pytest.fixture
def catalog() -> NFRCatalog:
    return load_catalog(CATALOG_DIR)


def system_and_user(brief: InterviewBrief, catalog: NFRCatalog) -> tuple[str, str]:
    system, user = build_planner_messages(brief, catalog)
    assert (system["role"], user["role"]) == ("system", "user")
    return system["content"], user["content"]


def test_messages_are_one_system_then_one_user(catalog: NFRCatalog) -> None:
    roles = [message["role"] for message in build_planner_messages(BRIEF, catalog)]

    assert roles == ["system", "user"]


def test_system_message_does_not_depend_on_the_brief(catalog: NFRCatalog) -> None:
    """지시는 실행마다 같아야 API 프롬프트 캐시를 탄다. 바뀌는 입력은 user에만 둔다."""
    assert system_and_user(BRIEF, catalog)[0] == system_and_user(FOCUSED, catalog)[0]


def test_user_message_carries_the_brief(catalog: NFRCatalog) -> None:
    _, user = system_and_user(BRIEF, catalog)

    assert BRIEF.topic in user
    assert str(BRIEF.seniority) in user


def test_system_message_embeds_the_whole_catalog_block(catalog: NFRCatalog) -> None:
    """카탈로그는 M0의 직렬화 결과를 그대로 넣는다. 일부만 들어가면 후보가 치우친다."""
    assert catalog.to_prompt_block() in system_and_user(BRIEF, catalog)[0]


def test_system_message_lists_the_three_source_tiers_in_order(
    catalog: NFRCatalog,
) -> None:
    system, _ = system_and_user(BRIEF, catalog)
    tiers = [system.index(f"{n}순위") for n in (1, 2, 3)]

    assert tiers == sorted(tiers)


def test_system_message_numbers_match_the_plan_schema(catalog: NFRCatalog) -> None:
    """프롬프트가 요구하는 개수와 ResearchPlan이 받아들이는 개수가 어긋나면 파싱이 실패한다."""
    system, _ = system_and_user(BRIEF, catalog)

    assert f"{CANDIDATES_MIN}~{CANDIDATES_MAX}개" in system
    assert f"{MAX_QUERIES}개 이하" in system


def test_system_message_states_catalog_is_a_reference_not_a_menu(
    catalog: NFRCatalog,
) -> None:
    """Catalog를 메뉴로 읽으면 주제와 무관하게 6개를 기계적으로 고른다."""
    assert "메뉴가 아니다" in system_and_user(BRIEF, catalog)[0]


def test_user_focus_appears_only_when_given(catalog: NFRCatalog) -> None:
    _, with_notes = system_and_user(FOCUSED, catalog)
    _, without_notes = system_and_user(BRIEF, catalog)

    assert "- 사용자 중점 요구사항: 장애 시 가용성" in with_notes.splitlines()
    assert "사용자 중점 요구사항" not in without_notes


def test_multi_line_notes_stay_on_one_line(catalog: NFRCatalog) -> None:
    """둘째 줄부터 입력 목록 밖으로 떨어지지 않게 한 줄로 접는다."""
    focused = InterviewBrief(
        seniority=Seniority.SENIOR, topic=BRIEF.topic, notes="장애 시 가용성\n  지연"
    )

    _, user = system_and_user(focused, catalog)

    assert "- 사용자 중점 요구사항: 장애 시 가용성 지연" in user.splitlines()


def test_messages_are_the_same_for_the_same_input(catalog: NFRCatalog) -> None:
    """같은 입력이면 같은 메시지여야 Day 8 캐시 재생과 비교가 성립한다."""
    assert build_planner_messages(BRIEF, catalog) == build_planner_messages(
        BRIEF, catalog
    )


@pytest.mark.parametrize("brief", [BRIEF, FOCUSED])
@pytest.mark.parametrize("leftover", ["{{", "}}", "{%", "%}", "\n\n\n", " \n"])
def test_messages_have_no_template_leftovers(
    catalog: NFRCatalog, brief: InterviewBrief, leftover: str
) -> None:
    for content in system_and_user(brief, catalog):
        assert leftover not in content
