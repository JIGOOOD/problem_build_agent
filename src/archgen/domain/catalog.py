"""자주 나타나는 NFR의 참고 목록. 스키마는 docs/nfr-design.md를 따른다."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
"""공백만 든 값도 프롬프트에서는 빈 값이므로 문자열 필드는 전부 이 타입을 쓴다."""


class CatalogTradeoff(BaseModel):
    """이 NFR을 달성할 때 흔히 맞바꾸게 되는 대상과 그 이유."""

    model_config = ConfigDict(extra="forbid")

    against: NonBlank
    reason: NonBlank


class CatalogEntry(BaseModel):
    """Catalog 항목 하나. 빈 값은 프롬프트에 빈 줄로 나가므로 허용하지 않는다."""

    model_config = ConfigDict(extra="forbid")

    name: NonBlank
    category: NonBlank
    meaning: NonBlank
    important_when: list[NonBlank] = Field(min_length=1)
    examples: list[NonBlank] = Field(min_length=1)
    common_tradeoffs: list[CatalogTradeoff] = Field(min_length=1)


class NFRCatalog(BaseModel):
    """Planner와 NFR Agent가 참고하는 Catalog 전체."""

    entries: list[CatalogEntry] = Field(min_length=1)

    def to_research_prompt_block(self) -> str:
        """초기 후보·쿼리 생성에 필요한 이름·의미·중요한 경우만 전달한다."""
        lines: list[str] = []
        for entry in sorted(self.entries, key=lambda e: e.name):
            lines.append(f"- {entry.name}: {_one_line(entry.meaning)}")
            lines.append(f"  중요한 경우: {_join(entry.important_when)}")
        return "\n".join(lines)

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
    """디렉터리의 yaml을 전부 읽어 Catalog를 만든다.

    Catalog가 비거나 이름이 겹치면 프롬프트가 조용히 망가지므로 여기서 막는다.
    """
    if not directory.is_dir():
        raise ValueError(f"카탈로그 디렉터리가 없다: {directory}")

    entries = [
        CatalogEntry.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        for path in sorted(directory.iterdir())
        if path.suffix in (".yaml", ".yml")
    ]
    if not entries:
        raise ValueError(f"카탈로그가 비어 있다: {directory}")

    counted = Counter(entry.name for entry in entries)
    duplicated = sorted(name for name, times in counted.items() if times > 1)
    if duplicated:
        raise ValueError(f"카탈로그 name이 겹친다: {', '.join(duplicated)}")

    return NFRCatalog(entries=entries)
