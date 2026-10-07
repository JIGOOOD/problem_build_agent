from collections.abc import Callable

import pytest
from helpers import edited

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRExport
from archgen.harness.findings import Severity
from archgen.render.post_render import check_rendered
from archgen.render.renderer import render_rubric

BRIEF = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간 채팅 시스템 설계")


def findings_for(md: str, export: NFRExport) -> set[tuple[str, str]]:
    findings = check_rendered(md, export, BRIEF)
    assert all(f.severity is Severity.ERROR for f in findings)
    return {(f.code, f.path) for f in findings}


def test_post_render_passes_what_the_renderer_made(golden_export: NFRExport) -> None:
    md = render_rubric(golden_export, BRIEF)

    assert check_rendered(md, golden_export, BRIEF) == []


def drop_line_containing(text: str) -> Callable[[str], str]:
    return lambda md: "\n".join(line for line in md.splitlines() if text not in line)


def replace_once(old: str, new: str) -> Callable[[str], str]:
    def tamper(md: str) -> str:
        assert old in md, "망가뜨릴 대상이 md에 없다"
        return md.replace(old, new, 1)

    return tamper


def drop_second_section(md: str) -> str:
    """NFR-C2 섹션(헤딩부터 다음 구분선 전까지)을 통째로 지운다."""
    head, rest = md.split("\n### NFR-C2.", 1)
    return head + "\n---" + rest.split("\n---", 1)[1]


def swap_first_two_sections(md: str) -> str:
    head, first, second, *rest = md.split("\n---\n")
    return "\n---\n".join([head, second, first, *rest])


def repeat_first_section(md: str) -> str:
    head, *sections = md.split("\n---\n")
    return "\n---\n".join([head, *sections, sections[0]])


@pytest.mark.parametrize(
    "tamper",
    [
        replace_once("# 실시간 채팅 시스템 설계\n", "# 엉뚱한 주제\n"),
        replace_once("**대상 연차** 미들", "**대상 연차** 시니어"),
        replace_once("**배점** 100", "**배점** 90"),
        replace_once("## NFR\n", ""),
        drop_line_containing("**채점 규칙**"),
    ],
)
def test_post_render_flags_a_wrong_header(
    golden_export: NFRExport, tamper: Callable[[str], str]
) -> None:
    """머리말: 주제, 대상 연차, 배점 합, `## NFR` 헤딩, 채점 규칙."""
    md = tamper(render_rubric(golden_export, BRIEF))

    assert findings_for(md, golden_export) == {("RENDER_HEADER_MISMATCH", "header")}


@pytest.mark.parametrize("tamper", [swap_first_two_sections, repeat_first_section])
def test_post_render_flags_sections_out_of_order_or_repeated(
    golden_export: NFRExport, tamper: Callable[[str], str]
) -> None:
    """섹션을 id로 찾기만 하면 순서와 중복을 놓친다. 목록 전체를 비교한다."""
    md = tamper(render_rubric(golden_export, BRIEF))

    assert findings_for(md, golden_export) == {
        ("RENDER_SECTIONS_MISMATCH", "rubric.criteria")
    }


def test_post_render_accepts_a_topic_folded_into_one_heading_line(
    golden_export: NFRExport,
) -> None:
    brief = InterviewBrief(seniority=Seniority.SENIOR, topic="실시간\n  채팅")
    md = render_rubric(golden_export, brief)

    assert check_rendered(md, golden_export, brief) == []


@pytest.mark.parametrize(
    ("tamper", "expected"),
    [
        (
            drop_line_containing("| NFR-C3 |"),
            {("RENDER_SUMMARY_MISMATCH", "rubric.criteria")},
        ),
        (
            drop_second_section,
            {("RENDER_SECTIONS_MISMATCH", "rubric.criteria")},
        ),
        (
            drop_line_containing("| 2 | 수락 완료의 경계를"),
            {("RENDER_LEVELS_MISMATCH", "rubric.criteria[0].levels")},
        ),
        (
            replace_once("— 서버가 수락한", "— 서버가 받은"),
            {("RENDER_REQUIREMENT_MISMATCH", "confirmed_nfrs[0]")},
        ),
        (
            replace_once("| 0 | 수락한 메시지를", "| 0 | 받은 메시지를"),
            {("RENDER_LEVELS_MISMATCH", "rubric.criteria[0].levels")},
        ),
        (
            replace_once("서버가 수락 완료한 메시지의", "서버가 받은 메시지의"),
            {("RENDER_DESCRIPTION_MISMATCH", "rubric.criteria[0].description")},
        ),
        (
            replace_once("전달 신뢰성 · 45점", "전달 신뢰성 · 40점"),
            {("RENDER_HEADING_MISMATCH", "rubric.criteria[0].weight")},
        ),
        (
            replace_once("### NFR-C1. 수락한", "### NFR-C1. 받은"),
            {("RENDER_HEADING_MISMATCH", "rubric.criteria[0].title")},
        ),
        (
            drop_line_containing("- 정족수를 요구하는"),
            {("RENDER_TRADEOFF_MISMATCH", "rubric.criteria[0].tradeoffs")},
        ),
    ],
)
def test_post_render_flags_a_rubric_the_renderer_got_wrong(
    golden_export: NFRExport,
    tamper: Callable[[str], str],
    expected: set[tuple[str, str]],
) -> None:
    """렌더러 버그를 흉내 내려고 정상 md를 한 군데만 망가뜨린다."""
    md = tamper(render_rubric(golden_export, BRIEF))

    assert findings_for(md, golden_export) == expected


def test_post_render_reports_instead_of_crashing_on_a_broken_document(
    golden_export: NFRExport,
) -> None:
    """md 구조가 통째로 무너져도 예외 대신 Finding으로 남긴다."""
    assert findings_for("", golden_export) == {
        ("RENDER_HEADER_MISMATCH", "header"),
        ("RENDER_SUMMARY_MISMATCH", "rubric.criteria"),
        ("RENDER_SECTIONS_MISMATCH", "rubric.criteria"),
    }


def test_post_render_accepts_single_newlines_inside_paragraphs(
    golden_export: NFRExport,
) -> None:
    """문단 안 줄바꿈은 md를 깨지 않는다. 잘못 지적하면 안 된다."""

    def wrap(raw: dict) -> None:
        raw["confirmed_nfrs"][0]["statement"] = "첫 줄의 요구.\n둘째 줄의 요구."
        raw["tradeoffs"][0]["description"] = "첫 줄의 상충.\n둘째 줄의 상충."
        raw["rubric"]["criteria"][0]["description"] = "첫 줄의 평가.\n둘째 줄의 평가."

    export = edited(golden_export, wrap)

    assert check_rendered(render_rubric(export, BRIEF), export, BRIEF) == []


def test_post_render_catches_a_blank_line_that_splits_a_tradeoff(
    golden_export: NFRExport,
) -> None:
    """빈 줄이 든 trade-off는 목록 항목이 끊긴다. 테스트가 못 다룬 입력을 실행 시점에 잡는다."""

    def split(raw: dict) -> None:
        raw["tradeoffs"][0]["description"] = "첫 문단의 상충.\n\n둘째 문단의 상충."

    export = edited(golden_export, split)
    found = findings_for(render_rubric(export, BRIEF), export)

    assert ("RENDER_TRADEOFF_MISMATCH", "rubric.criteria[0].tradeoffs") in found


def escaped_title(raw: dict) -> None:
    raw["rubric"]["criteria"][0]["title"] = "읽기 | 쓰기\n경로"


def escaped_descriptor(raw: dict) -> None:
    raw["rubric"]["criteria"][0]["levels"][1]["descriptor"] = "A | B\n둘째 줄"


def quantitative_target(raw: dict) -> None:
    nfr = raw["confirmed_nfrs"][1]
    nfr["qualitative_target"] = None
    nfr["target"] = {"value": 1_000_000, "unit": "rps", "condition": "peak"}


def reversed_levels(raw: dict) -> None:
    raw["rubric"]["criteria"][0]["levels"].reverse()


def weights_not_summing_to_100(raw: dict) -> None:
    """머리말 배점은 고정 문구 100이 아니라 weight 합이다."""
    raw["rubric"]["criteria"][0]["weight"] = 40


@pytest.mark.parametrize(
    "edit",
    [
        escaped_title,
        escaped_descriptor,
        quantitative_target,
        reversed_levels,
        weights_not_summing_to_100,
    ],
)
def test_post_render_accepts_what_the_renderer_rewrites_on_purpose(
    golden_export: NFRExport, edit: Callable[[dict], None]
) -> None:
    """이스케이프·헤딩 접기·목표 표기·레벨 정렬은 렌더러가 일부러 바꾸는 것이라 지적하지 않는다."""
    export = edited(golden_export, edit)

    assert check_rendered(render_rubric(export, BRIEF), export, BRIEF) == []


def test_post_render_codes_name_one_part_of_the_document() -> None:
    """code 하나가 md의 한 부분을 가리킨다. 이름만 보고 고칠 템플릿 블록을 안다."""
    from archgen.harness.findings import FindingCode

    assert {c.value for c in FindingCode if c.value.startswith("RENDER_")} == {
        "RENDER_SUMMARY_MISMATCH",
        "RENDER_HEADER_MISMATCH",
        "RENDER_SECTIONS_MISMATCH",
        "RENDER_HEADING_MISMATCH",
        "RENDER_DESCRIPTION_MISMATCH",
        "RENDER_REQUIREMENT_MISMATCH",
        "RENDER_TRADEOFF_MISMATCH",
        "RENDER_LEVELS_MISMATCH",
    }
