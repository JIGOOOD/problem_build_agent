"""자주 나타나는 NFR의 참고 목록. 스키마는 docs/nfr-design.md를 따른다."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class CatalogTradeoff(BaseModel):
    """이 NFR을 달성할 때 흔히 맞바꾸게 되는 대상과 그 이유."""

    against: str
    reason: str


class CatalogEntry(BaseModel):
    """Catalog 항목 하나."""

    name: str
    category: str
    meaning: str
    important_when: list[str] = []
    examples: list[str] = []
    common_tradeoffs: list[CatalogTradeoff] = []


class NFRCatalog(BaseModel):
    """Planner와 NFR Agent가 참고하는 Catalog 전체."""

    entries: list[CatalogEntry] = []

    def to_prompt_block(self) -> str:
        """프롬프트에 끼워넣을 문자열. 같은 입력이면 같은 결과가 나와야 한다."""
        lines: list[str] = []
        current = ""
        for entry in sorted(self.entries, key=lambda e: (e.category, e.name)):
            if entry.category != current:
                current = entry.category
                lines.append(f"[{current}]")
            lines.append(f"- {entry.name}: {_one_line(entry.meaning)}")
            lines.append(f"  중요한 경우: {_join(entry.important_when)}")
            lines.append(f"  예: {_join(entry.examples)}")
            for tradeoff in entry.common_tradeoffs:
                lines.append(f"  상충 {tradeoff.against}: {_one_line(tradeoff.reason)}")
        return "\n".join(lines)


def _one_line(text: str) -> str:
    """한 필드가 한 줄을 차지하도록 줄바꿈을 공백으로 편다."""
    return " ".join(text.split())


def _join(items: list[str]) -> str:
    """여러 값을 한 줄로 잇는다."""
    return "; ".join(_one_line(item) for item in items)


def load_catalog(directory: Path) -> NFRCatalog:
    """디렉터리의 yaml을 전부 읽어 Catalog를 만든다."""
    entries = [
        CatalogEntry.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        for path in sorted(directory.glob("*.yaml"))
    ]
    return NFRCatalog(entries=entries)
