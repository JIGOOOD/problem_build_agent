from collections.abc import Callable

import pytest

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRExport
from archgen.render.renderer import render_rubric

BRIEF = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간 채팅 시스템 설계")


def edited(export: NFRExport, edit: Callable[[dict], None]) -> NFRExport:
    raw = export.model_dump()
    edit(raw)
    return NFRExport.model_validate(raw)


def criterion_sections(md: str) -> dict[str, str]:
    """`### NFR-C1. ...` 헤딩부터 다음 헤딩 전까지를 criterion id로 묶는다."""
    sections = {}
    for chunk in md.split("\n### ")[1:]:
        criterion_id = chunk.split(".", 1)[0]
        sections[criterion_id] = chunk
    return sections


def test_rubric_starts_with_the_topic_as_the_top_heading(
    golden_export: NFRExport,
) -> None:
    """면접관이 가장 먼저 보는 정보라 문서 제목으로 둔다."""
    assert render_rubric(golden_export, BRIEF).startswith(f"# {BRIEF.topic}\n")


def test_nfr_section_heading_sits_under_the_topic(golden_export: NFRExport) -> None:
    """criterion(###)은 NFR 섹션(##) 아래에 온다."""
    lines = render_rubric(golden_export, BRIEF).splitlines()
    first_criterion = next(i for i, line in enumerate(lines) if line.startswith("### "))

    assert lines.index("## NFR") < first_criterion


def header_lines(md: str) -> list[str]:
    """요약표 앞까지의 머리말 줄."""
    return md.split("\n|", 1)[0].splitlines()


def test_header_shows_seniority_and_scoring_rule_on_their_own_lines(
    golden_export: NFRExport,
) -> None:
    lines = header_lines(render_rubric(golden_export, BRIEF))

    assert any(line.startswith(f"**대상 연차** {BRIEF.seniority}") for line in lines)
    assert any("채점 규칙" in line for line in lines)


def test_header_total_is_the_sum_of_weights(golden_export: NFRExport) -> None:
    """고정 문구가 아니라 데이터에서 계산해 본문 배점과 어긋나지 않게 한다."""

    def reweigh(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["weight"] = 40  # 합 95

    md = render_rubric(edited(golden_export, reweigh), BRIEF)

    assert any(line.startswith("**배점** 95") for line in header_lines(md))


def test_summary_table_has_one_row_per_criterion(golden_export: NFRExport) -> None:
    md = render_rubric(golden_export, BRIEF)
    rows = [line for line in md.splitlines() if line.endswith("☐0 ☐1 ☐2 ☐3 |")]

    assert len(rows) == len(golden_export.rubric.criteria)
    for row, criterion in zip(rows, golden_export.rubric.criteria, strict=True):
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        assert cells[:3] == [criterion.id, criterion.title, str(criterion.weight)]


def test_every_criterion_gets_a_heading_with_its_weight(golden_export: NFRExport) -> None:
    md = render_rubric(golden_export, BRIEF)

    for criterion in golden_export.rubric.criteria:
        heading = f"### {criterion.id}. {criterion.title} · {criterion.weight}점"
        assert heading in md.splitlines()


def test_every_criterion_has_a_four_row_level_table(golden_export: NFRExport) -> None:
    sections = criterion_sections(render_rubric(golden_export, BRIEF))

    for criterion in golden_export.rubric.criteria:
        # 레벨표 헤더와 구분선 다음부터 표가 끝날 때까지의 행 전부
        table = sections[criterion.id].split("| Level | 기준 |\n|---|---|\n", 1)[1]
        rows = table.split("\n\n", 1)[0].strip().splitlines()

        assert [row.split("|")[1].strip() for row in rows] == ["0", "1", "2", "3"]


def test_qualitative_requirement_shows_the_statement_once(
    golden_export: NFRExport,
) -> None:
    """정성 목표는 statement의 요약이라 둘 다 쓰면 같은 말을 반복한다."""
    md = render_rubric(golden_export, BRIEF)
    sections = criterion_sections(md)

    for criterion in golden_export.rubric.criteria:
        nfr = next(
            n for n in golden_export.confirmed_nfrs if n.id in criterion.related_nfr_ids
        )
        assert f"`{nfr.kind}` — {nfr.statement}" in sections[criterion.id]
        assert nfr.qualitative_target not in md


def with_target(value: float, unit: str | None, condition: str | None):
    def quantify(raw: dict) -> None:
        nfr = raw["confirmed_nfrs"][1]  # NFR-2, NFR-C2가 평가
        nfr["qualitative_target"] = None
        nfr["target"] = {"value": value, "unit": unit, "condition": condition}

    return quantify


def test_quantitative_requirement_shows_the_target_then_the_statement(
    golden_export: NFRExport,
) -> None:
    export = edited(golden_export, with_target(500, "ms", "p99"))
    section = criterion_sections(render_rubric(export, BRIEF))["NFR-C2"]
    nfr = export.confirmed_nfrs[1]

    assert f"`{nfr.kind}` — p99 500 ms\n{nfr.statement}" in section


@pytest.mark.parametrize(
    ("value", "unit", "condition", "shown"),
    [
        (1_000_000, "rps", None, "1,000,000 rps"),  # 지수 표기(1e+06)가 아니다
        (10_000, "msg/s", "peak", "peak 10,000 msg/s"),
        (1234.5, "ms", None, "1,234.5 ms"),
        (0.0001, "s", None, "0.0001 s"),
        (99.99, "%", None, "99.99%"),  # %만 붙여 쓴다
        (3, None, None, "3"),
    ],
)
def test_target_numbers_are_written_for_people(
    golden_export: NFRExport,
    value: float,
    unit: str | None,
    condition: str | None,
    shown: str,
) -> None:
    """천 단위 콤마, 지수 표기 없음, 숫자와 단위 사이는 띄운다."""
    export = edited(golden_export, with_target(value, unit, condition))
    section = criterion_sections(render_rubric(export, BRIEF))["NFR-C2"]

    assert f"`{export.confirmed_nfrs[1].kind}` — {shown}\n" in section


def test_levels_are_listed_from_zero_to_three(golden_export: NFRExport) -> None:
    """LLM이 레벨을 거꾸로 내도 채점표는 0점부터 읽힌다."""

    def reverse(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["levels"].reverse()

    export = edited(golden_export, reverse)
    levels = read_back(render_rubric(export, BRIEF))["criteria"][0]["levels"]
    by_score = sorted(export.rubric.criteria[0].levels, key=lambda level: level.score)

    assert levels == [(str(level.score), level.descriptor) for level in by_score]


def test_related_tradeoffs_are_listed_under_their_criterion(
    golden_export: NFRExport,
) -> None:
    sections = criterion_sections(render_rubric(golden_export, BRIEF))

    for criterion in golden_export.rubric.criteria:
        related = [
            t
            for t in golden_export.tradeoffs
            if set(t.related_nfr_ids) & set(criterion.related_nfr_ids)
        ]
        assert related, "골든셋 criterion은 모두 trade-off가 있다"
        for tradeoff in related:
            assert f"- {tradeoff.description}" in sections[criterion.id]


def test_tradeoff_block_is_omitted_when_there_is_none(golden_export: NFRExport) -> None:
    """빈 섹션을 남기지 않는다."""

    def detach_from_nfr3(raw: dict) -> None:
        raw["tradeoffs"] = [
            t for t in raw["tradeoffs"] if "NFR-3" not in t["related_nfr_ids"]
        ]

    sections = criterion_sections(
        render_rubric(edited(golden_export, detach_from_nfr3), BRIEF)
    )

    assert "관련 trade-off" not in sections["NFR-C3"]
    assert "관련 trade-off" in sections["NFR-C1"]


@pytest.mark.parametrize("blank_run", ["\n\n\n", " \n"])
def test_rendered_markdown_has_no_stray_whitespace(
    golden_export: NFRExport, blank_run: str
) -> None:
    """템플릿 제어문이 남긴 빈 줄·줄 끝 공백이 없어야 한다."""
    assert blank_run not in render_rubric(golden_export, BRIEF)


def read_back(md: str) -> dict:
    """렌더된 md를 다시 구조로 읽는다. 원본 NFRExport와 필드별로 비교하기 위한 것."""

    def block(chunk: str, label: str) -> list[str]:
        if f"**{label}**\n" not in chunk:
            return []
        return chunk.split(f"**{label}**\n", 1)[1].split("\n\n", 1)[0].splitlines()

    def cells(row: str) -> list[str]:
        return [cell.strip() for cell in row.strip().strip("|").split("|")]

    lines = md.splitlines()
    summary = [cells(line)[:3] for line in lines if line.endswith("☐0 ☐1 ☐2 ☐3 |")]
    criteria = []
    for chunk in md.split("\n### ")[1:]:
        heading = chunk.splitlines()[0]
        criterion_id, rest = heading.split(". ", 1)
        title, weight = rest.rsplit(" · ", 1)
        table = chunk.split("| Level | 기준 |\n|---|---|\n", 1)[1].split("\n\n", 1)[0]
        criteria.append(
            {
                "id": criterion_id,
                "title": title,
                "weight": weight.removesuffix("점"),
                "description": "\n".join(block(chunk, "평가 항목")),
                "requirement": block(chunk, "요구 수준"),
                "tradeoffs": [
                    line.removeprefix("- ") for line in block(chunk, "관련 trade-off")
                ],
                "levels": [tuple(cells(row)) for row in table.strip().splitlines()],
            }
        )
    return {"summary": summary, "criteria": criteria}


def test_rendered_rubric_reads_back_to_the_export(golden_export: NFRExport) -> None:
    """md에 옮겨진 값이 원본과 한 글자도 다르지 않아야 한다."""
    rendered = read_back(render_rubric(golden_export, BRIEF))
    nfrs = {nfr.id: nfr for nfr in golden_export.confirmed_nfrs}

    assert rendered["summary"] == [
        [c.id, c.title, str(c.weight)] for c in golden_export.rubric.criteria
    ]
    assert len(rendered["criteria"]) == len(golden_export.rubric.criteria)
    for got, criterion in zip(
        rendered["criteria"], golden_export.rubric.criteria, strict=True
    ):
        nfr = nfrs[criterion.related_nfr_ids[0]]
        assert got["id"] == criterion.id
        assert got["title"] == criterion.title
        assert got["weight"] == str(criterion.weight)
        assert got["description"] == criterion.description
        # 정성 목표: `kind` — statement 한 줄
        assert got["requirement"] == [f"`{nfr.kind}` — {nfr.statement}"]
        assert got["tradeoffs"] == [
            t.description for t in golden_export.tradeoffs if nfr.id in t.related_nfr_ids
        ]
        assert got["levels"] == [
            (str(level.score), level.descriptor) for level in criterion.levels
        ]
