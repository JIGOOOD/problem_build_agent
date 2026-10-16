import pytest
from helpers import edited

from archgen.domain.brief import InterviewBrief, Seniority
from archgen.domain.nfr import NFRExport
from archgen.render.post_render import read_back
from archgen.render.renderer import _nfr_name, render_rubric

BRIEF = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간 채팅 시스템 설계")


def test_render_matches_output_sample_columns_headings_and_clean_header(golden_export):
    from archgen.render.post_render import check_rendered

    export = golden_export.model_copy(deep=True)
    export.rubric.criteria[0].id = "criterion-custom"
    md = render_rubric(export, BRIEF)

    assert "## NFR\n\n| NFR | 평가 항목 | 배점 | 획득 |" in md
    assert ">" not in "\n".join(header_lines(md))
    for i, criterion in enumerate(export.rubric.criteria, 1):
        assert f"| {criterion.related_nfr_ids[0]} · " in md
        assert f"| C{i}. {criterion.title} | {criterion.weight} |" in md
        assert f"### C{i}. {criterion.title} · {criterion.weight}" in md
    assert "역량 축" not in md
    assert "competency_axis" not in golden_export.rubric.criteria[0].model_dump()
    assert export.rubric.criteria[0].id == "criterion-custom"
    assert check_rendered(md, export, BRIEF) == []


def criterion_sections(md: str) -> dict[str, str]:
    """`### C1. ...` 헤딩부터 다음 헤딩 전까지를 criterion id로 묶는다."""
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


def test_header_shows_seniority_without_extra_scoring_prose(
    golden_export: NFRExport,
) -> None:
    lines = header_lines(render_rubric(golden_export, BRIEF))

    assert any(line.startswith(f"**대상 연차** {BRIEF.seniority}") for line in lines)
    assert not any(line.startswith(">") for line in lines)


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
        nfr = next(
            n
            for n in golden_export.confirmed_nfrs
            if n.id == criterion.related_nfr_ids[0]
        )
        assert cells[:3] == [
            f"{nfr.id} · {_nfr_name(nfr.kind)}",
            f"{criterion.id}. {criterion.title}",
            str(criterion.weight),
        ]


def test_every_criterion_gets_a_heading_with_its_weight(golden_export: NFRExport) -> None:
    md = render_rubric(golden_export, BRIEF)

    for criterion in golden_export.rubric.criteria:
        heading = f"### {criterion.id}. {criterion.title} · {criterion.weight}"
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
    for criterion in golden_export.rubric.criteria:
        nfr = next(
            n for n in golden_export.confirmed_nfrs if n.id in criterion.related_nfr_ids
        )
        assert md.count(f"`{nfr.kind}` — {nfr.statement}") == 1
        assert nfr.qualitative_target not in md


def with_target(value: float, unit: str | None, condition: str | None):
    def quantify(raw: dict) -> None:
        nfr = raw["confirmed_nfrs"][1]  # NFR-2, C2가 평가
        nfr["qualitative_target"] = None
        nfr["target"] = {"value": value, "unit": unit, "condition": condition}

    return quantify


def test_quantitative_requirement_shows_the_target_then_the_statement(
    golden_export: NFRExport,
) -> None:
    export = edited(golden_export, with_target(500, "ms", "p99"))
    section = render_rubric(export, BRIEF)
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
    section = render_rubric(export, BRIEF)

    assert f"`{export.confirmed_nfrs[1].kind}` — {shown}\n" in section


def test_levels_are_listed_from_zero_to_three(golden_export: NFRExport) -> None:
    """LLM이 레벨을 거꾸로 내도 채점표는 0점부터 읽힌다."""

    def reverse(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["levels"].reverse()

    export = edited(golden_export, reverse)
    levels = read_back(render_rubric(export, BRIEF))["criteria"][0]["levels"]
    by_score = sorted(export.rubric.criteria[0].levels, key=lambda level: level.score)

    assert levels == [(str(level.score), level.descriptor) for level in by_score]


@pytest.mark.parametrize("blank_run", ["\n\n\n", " \n"])
def test_rendered_markdown_has_no_stray_whitespace(
    golden_export: NFRExport, blank_run: str
) -> None:
    """템플릿 제어문이 남긴 빈 줄·줄 끝 공백이 없어야 한다."""
    assert blank_run not in render_rubric(golden_export, BRIEF)


def test_rendered_rubric_reads_back_to_the_export(golden_export: NFRExport) -> None:
    """md에 옮겨진 값이 원본과 한 글자도 다르지 않아야 한다."""
    rendered = read_back(render_rubric(golden_export, BRIEF))
    nfrs = {nfr.id: nfr for nfr in golden_export.confirmed_nfrs}

    assert rendered["summary"] == [
        [
            f"{c.related_nfr_ids[0]} · {_nfr_name(nfrs[c.related_nfr_ids[0]].kind)}",
            f"{c.id}. {c.title}",
            str(c.weight),
        ]
        for c in golden_export.rubric.criteria
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
        group = next(
            g for g in rendered["nfrs"] if g["heading"].startswith(f"{nfr.id}. ")
        )
        assert group["requirement"] == [f"`{nfr.kind}` — {nfr.statement}"]
        assert got["levels"] == [
            (str(level.score), level.descriptor) for level in criterion.levels
        ]


def test_pipes_in_table_cells_do_not_split_the_row(golden_export: NFRExport) -> None:
    """`|`가 그대로 들어가면 칸이 하나 더 생겨 표가 어긋난다."""

    def add_pipes(raw: dict) -> None:
        criterion = raw["rubric"]["criteria"][0]
        criterion["title"] = "읽기 | 쓰기 경로"
        criterion["levels"][1]["descriptor"] = "A | B 중 하나만 고려한다."

    export = edited(golden_export, add_pipes)
    rendered = read_back(render_rubric(export, BRIEF))
    criterion = export.rubric.criteria[0]

    assert rendered["summary"][0][1] == f"C1. {criterion.title}"
    assert rendered["criteria"][0]["levels"] == [
        (str(level.score), level.descriptor) for level in criterion.levels
    ]


def test_newlines_in_table_cells_stay_inside_the_row(golden_export: NFRExport) -> None:
    """줄바꿈이 그대로 들어가면 표 행이 끊긴다. <br>로 칸 안에서 줄을 바꾼다."""

    def add_newlines(raw: dict) -> None:
        criterion = raw["rubric"]["criteria"][0]
        criterion["title"] = "읽기 경로\n쓰기 경로"
        criterion["levels"][2]["descriptor"] = (
            "첫째 조건을 설명한다.\n둘째 조건도 설명한다."
        )

    export = edited(golden_export, add_newlines)
    rendered = read_back(render_rubric(export, BRIEF))
    criterion = export.rubric.criteria[0]

    assert rendered["summary"][0][1] == f"C1. {criterion.title}"
    assert rendered["criteria"][0]["levels"] == [
        (str(level.score), level.descriptor) for level in criterion.levels
    ]


def test_newlines_in_headings_become_spaces(golden_export: NFRExport) -> None:
    """헤딩은 한 줄이어야 한다. 줄바꿈과 연속 공백을 공백 하나로 접는다."""

    def add_newline(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["title"] = "읽기 경로\n  쓰기 경로"

    export = edited(golden_export, add_newline)
    brief = InterviewBrief(seniority=Seniority.MIDDLE, topic="실시간\n채팅")
    md = render_rubric(export, brief)

    assert md.startswith("# 실시간 채팅\n")
    assert read_back(md)["criteria"][0]["title"] == "읽기 경로 쓰기 경로"


def test_same_nfr_groups_multiple_criteria_once(golden_export):
    from archgen.render.post_render import check_rendered

    export = golden_export.model_copy(deep=True)
    extra = export.rubric.criteria[-1].model_copy(deep=True)
    extra.id = "C4"
    extra.weight = 10
    export.rubric.criteria[-1].weight -= 10
    export.rubric.criteria.append(extra)
    md = render_rubric(export, BRIEF)

    assert md.count("## NFR-3. Scalability") == 1
    assert md.count("| NFR-3 · Scalability |") == 2
    assert "### C3." in md and "### C4." in md
    assert md.index("## NFR-3.") < md.index("### C3.") < md.index("### C4.")
    assert md.count(export.confirmed_nfrs[-1].statement) == 1
    assert "관련 trade-off" not in md
    assert export.tradeoffs
    assert check_rendered(md, export, BRIEF) == []


def test_groups_keep_criterion_numbers_when_input_is_interleaved(golden_export):
    from archgen.render.post_render import check_rendered

    export = golden_export.model_copy(deep=True)
    extra = export.rubric.criteria[0].model_copy(deep=True)
    extra.id = "C4"
    extra.weight = 10
    export.rubric.criteria[0].weight -= 10
    export.rubric.criteria.append(extra)
    md = render_rubric(export, BRIEF)

    assert md.index("### C1.") < md.index("### C4.") < md.index("## NFR-2.")
    assert check_rendered(md, export, BRIEF) == []


def test_nfr_display_numbers_ignore_source_ids(golden_export):
    from archgen.render.post_render import check_rendered

    export = golden_export.model_copy(deep=True)
    ids = {n.id: f"nfr-{n.kind}" for n in export.confirmed_nfrs}
    for nfr in export.confirmed_nfrs:
        nfr.id = ids[nfr.id]
    for item in [*export.rubric.criteria, *export.tradeoffs]:
        item.related_nfr_ids = [ids[ref] for ref in item.related_nfr_ids]
    extra = export.rubric.criteria[-1].model_copy(deep=True)
    extra.id = "C4"
    extra.weight = 10
    export.rubric.criteria[-1].weight -= 10
    export.rubric.criteria.append(extra)
    original = export.model_dump()

    md = render_rubric(export, BRIEF)

    for i, nfr in enumerate(export.confirmed_nfrs, 1):
        assert f"| NFR-{i} · {_nfr_name(nfr.kind)} |" in md
        assert f"## NFR-{i}. {_nfr_name(nfr.kind)}" in md
        assert nfr.id not in md
    assert md.count("| NFR-3 · Scalability |") == 2
    assert check_rendered(md, export, BRIEF) == []
    assert export.model_dump() == original
