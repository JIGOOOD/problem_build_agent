"""렌더된 md를 다시 읽어 원본 NFRExport와 맞는지 확인한다 (Post-Render).

렌더러는 LLM이 아니라 코드라서, 여기서 어긋나면 LLM 출력이 아니라 렌더러를 고쳐야 한다.
"""

from __future__ import annotations

import re

from archgen.domain.brief import InterviewBrief
from archgen.domain.nfr import ConfirmedNFR, NFRExport, RubricCriterion
from archgen.harness.findings import Finding, FindingCode, Severity
from archgen.render.renderer import _format_target

_SUMMARY_ROW_END = "☐0 ☐1 ☐2 ☐3 |"
_LEVEL_HEADER = "| Level | 기준 |\n|---|---|\n"


def read_back(md: str) -> dict:
    """렌더된 md를 다시 구조로 읽는다. 구조가 무너져도 예외 없이 읽을 수 있는 만큼만 읽는다."""
    lines = md.splitlines()
    # 머리말은 첫 표(요약표) 앞까지다.
    head = md.split("\n|", 1)[0].splitlines()
    header = {
        "topic": head[0].removeprefix("# ")
        if head and head[0].startswith("# ")
        else None,
        "seniority": _labeled(head, "대상 연차"),
        "total_weight": _labeled(head, "배점"),
        "nfr_heading": "## NFR" in head,
        "scoring_rule": any(line.startswith("> **채점 규칙**") for line in head),
    }
    summary = [_cells(line)[:3] for line in lines if line.endswith(_SUMMARY_ROW_END)]
    criteria = []
    for chunk in md.split("\n### ")[1:]:
        heading = chunk.splitlines()[0] if chunk else ""
        criterion_id, _, rest = heading.partition(". ")
        title, _, weight = rest.rpartition(" · ")
        table = ""
        if _LEVEL_HEADER in chunk:
            table = chunk.split(_LEVEL_HEADER, 1)[1].split("\n\n", 1)[0]
        criteria.append(
            {
                "id": criterion_id,
                "title": title,
                "weight": weight.removesuffix("점"),
                "description": "\n".join(_block(chunk, "평가 항목")),
                "requirement": _block(chunk, "요구 수준"),
                "tradeoffs": _bullets(_block(chunk, "관련 trade-off")),
                "levels": [tuple(_cells(row)) for row in table.strip().splitlines()],
            }
        )
    return {"header": header, "summary": summary, "criteria": criteria}


def check_rendered(md: str, export: NFRExport, brief: InterviewBrief) -> list[Finding]:
    """md에 옮겨진 값이 원본과 같은가. 다르면 렌더러 버그다."""
    rendered = read_back(md)
    findings = _header_findings(rendered["header"], export, brief)
    expected_summary = [[c.id, c.title, str(c.weight)] for c in export.rubric.criteria]
    if rendered["summary"] != expected_summary:
        findings.append(
            _error(
                FindingCode.RENDER_SUMMARY_MISMATCH,
                "rubric.criteria",
                "요약표 행이 criterion 목록(id·title·배점)과 다르다.",
            )
        )
    # 섹션 id 목록 전체를 순서까지 비교해야 누락·중복·순서 뒤바뀜을 모두 잡는다.
    section_ids = [section["id"] for section in rendered["criteria"]]
    expected_ids = [c.id for c in export.rubric.criteria]
    if section_ids != expected_ids:
        findings.append(
            _error(
                FindingCode.RENDER_SECTIONS_MISMATCH,
                "rubric.criteria",
                f"criterion 섹션: {_difference(section_ids, expected_ids)}",
            )
        )
    # 안쪽 비교는 id별 첫 섹션으로 한다. 빠진 섹션은 위에서 이미 지적했다.
    sections: dict[str, dict] = {}
    for section in rendered["criteria"]:
        sections.setdefault(section["id"], section)
    for i, criterion in enumerate(export.rubric.criteria):
        if criterion.id in sections:
            findings += _section_findings(
                sections[criterion.id], criterion, f"rubric.criteria[{i}]", export
            )
    return findings


def _header_findings(
    header: dict, export: NFRExport, brief: InterviewBrief
) -> list[Finding]:
    """머리말: 주제, 대상 연차, 배점 합, `## NFR` 헤딩, 채점 규칙."""
    expected = {
        # 주제는 헤딩이라 줄바꿈·연속 공백을 접어서 쓴다.
        "topic": " ".join(brief.topic.split()),
        "seniority": str(brief.seniority),
        "total_weight": str(sum(c.weight for c in export.rubric.criteria)),
        "nfr_heading": True,
        "scoring_rule": True,
    }
    names = {
        "topic": "주제",
        "seniority": "대상 연차",
        "total_weight": "배점",
        "nfr_heading": "`## NFR` 헤딩",
        "scoring_rule": "채점 규칙",
    }
    return [
        _error(
            FindingCode.RENDER_HEADER_MISMATCH,
            "header",
            f"머리말 {names[key]}: 원본과 다르다.",
        )
        for key, value in expected.items()
        if header[key] != value
    ]


def _section_findings(
    section: dict, criterion: RubricCriterion, path: str, export: NFRExport
) -> list[Finding]:
    """criterion 섹션 하나를 원본과 비교한다. md의 부분마다 code가 하나다."""
    cid = criterion.id
    findings = []
    # 헤딩은 줄바꿈·연속 공백을 접어서 쓴다.
    if section["title"] != " ".join(criterion.title.split()):
        findings.append(
            _error(
                FindingCode.RENDER_HEADING_MISMATCH,
                f"{path}.title",
                f"{cid} 헤딩의 title이 다르다.",
            )
        )
    if section["weight"] != str(criterion.weight):
        findings.append(
            _error(
                FindingCode.RENDER_HEADING_MISMATCH,
                f"{path}.weight",
                f"{cid} 헤딩의 배점이 다르다.",
            )
        )
    if section["description"] != criterion.description:
        findings.append(
            _error(
                FindingCode.RENDER_DESCRIPTION_MISMATCH,
                f"{path}.description",
                f"{cid}의 평가 항목이 다르다.",
            )
        )

    nfrs = {nfr.id: (k, nfr) for k, nfr in enumerate(export.confirmed_nfrs)}
    if criterion.related_nfr_ids and criterion.related_nfr_ids[0] in nfrs:
        k, nfr = nfrs[criterion.related_nfr_ids[0]]
        if "\n".join(section["requirement"]) != _requirement(nfr):
            findings.append(
                _error(
                    FindingCode.RENDER_REQUIREMENT_MISMATCH,
                    f"confirmed_nfrs[{k}]",
                    f"{cid}의 요구 수준이 {nfr.id}와 다르다.",
                )
            )
        tradeoffs = [
            t.description for t in export.tradeoffs if nfr.id in t.related_nfr_ids
        ]
        if section["tradeoffs"] != tradeoffs:
            findings.append(
                _error(
                    FindingCode.RENDER_TRADEOFF_MISMATCH,
                    f"{path}.tradeoffs",
                    f"{cid}의 관련 trade-off: {_difference(section['tradeoffs'], tradeoffs)}",
                )
            )

    # 기준은 고정값 4가 아니라 원본 레벨 목록이다. 4개인지는 하네스 core.levels가 본다.
    levels = [
        (str(level.score), level.descriptor.strip())
        for level in sorted(criterion.levels, key=lambda level: level.score)
    ]
    if section["levels"] != levels:
        findings.append(
            _error(
                FindingCode.RENDER_LEVELS_MISMATCH,
                f"{path}.levels",
                f"{cid}의 레벨표: {_difference(section['levels'], levels)}",
            )
        )
    return findings


def _difference(got: list, expected: list) -> str:
    """두 목록이 어디서 처음 달라지는지 한 문장으로."""
    if len(got) != len(expected):
        return f"{len(got)}개로 읽혔다. 원본은 {len(expected)}개다."
    i = next(i for i, (a, b) in enumerate(zip(got, expected, strict=True)) if a != b)
    return f"{i + 1}번째 항목이 원본과 다르다."


def _requirement(nfr: ConfirmedNFR) -> str:
    target = _format_target(nfr.target)
    if target:
        return f"`{nfr.kind}` — {target}\n{nfr.statement}"
    return f"`{nfr.kind}` — {nfr.statement}"


def _labeled(lines: list[str], label: str) -> str | None:
    """`**label** 값` 줄에서 값만 꺼낸다. 줄 끝의 `\\` 줄바꿈 표시는 뗀다."""
    prefix = f"**{label}** "
    for line in lines:
        if line.startswith(prefix):
            return line.removeprefix(prefix).removesuffix("\\")
    return None


def _block(chunk: str, label: str) -> list[str]:
    """`**label**` 다음 줄부터 빈 줄 전까지."""
    marker = f"**{label}**\n"
    if marker not in chunk:
        return []
    return chunk.split(marker, 1)[1].split("\n\n", 1)[0].splitlines()


def _bullets(lines: list[str]) -> list[str]:
    """`- `로 시작하지 않는 줄은 앞 항목이 이어진 것이다."""
    items: list[str] = []
    for line in lines:
        if line.startswith("- ") or not items:
            items.append(line.removeprefix("- "))
        else:
            items[-1] += "\n" + line
    return items


def _cells(row: str) -> list[str]:
    """이스케이프된 \\|에서는 칸을 나누지 않고, 나눈 뒤 \\|와 <br>을 원래 문자로 되돌린다."""
    inner = row.strip().removeprefix("|").removesuffix("|")
    return [
        cell.strip().replace("\\|", "|").replace("<br>", "\n")
        for cell in re.split(r"(?<!\\)\|", inner)
    ]


def _error(code: FindingCode, path: str, message: str) -> Finding:
    return Finding(code=code, severity=Severity.ERROR, path=path, message=message)
