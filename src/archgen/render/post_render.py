"""렌더된 md를 다시 읽어 원본 NFRExport와 맞는지 확인한다 (Post-Render).

렌더러는 LLM이 아니라 코드라서, 여기서 어긋나면 LLM 출력이 아니라 렌더러를 고쳐야 한다.
"""

from __future__ import annotations

import re


def read_back(md: str) -> dict:
    """렌더된 md를 다시 구조로 읽는다. 원본 NFRExport와 필드별로 비교하기 위한 것."""

    def block(chunk: str, label: str) -> list[str]:
        if f"**{label}**\n" not in chunk:
            return []
        return chunk.split(f"**{label}**\n", 1)[1].split("\n\n", 1)[0].splitlines()

    def cells(row: str) -> list[str]:
        # 이스케이프된 \|에서는 칸을 나누지 않고, 나눈 뒤 \|와 <br>을 원래 문자로 되돌린다.
        inner = row.strip().removeprefix("|").removesuffix("|")
        return [
            cell.strip().replace("\\|", "|").replace("<br>", "\n")
            for cell in re.split(r"(?<!\\)\|", inner)
        ]

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
