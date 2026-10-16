"""The interview brief collected from the user before generation starts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from archgen.paths import RESOURCES


class Seniority(StrEnum):
    """Target experience level the generated problem should suit."""

    MIDDLE = "Middle"
    SENIOR = "Senior"


@dataclass(frozen=True)
class InterviewBrief:
    """One completed slot-filling round."""

    seniority: Seniority
    topic: str
    notes: str | None = None

    def __post_init__(self) -> None:
        # TUI 밖(그래프·테스트)에서 만들어도 Planner 프롬프트에 빈 값이 나가지 않게 정리한다.
        topic = self.topic.strip()
        if not topic:
            raise ValueError("주제가 비어 있다.")
        notes = self.notes.strip() if self.notes else ""
        object.__setattr__(self, "topic", topic)
        object.__setattr__(self, "notes", notes or None)

    def to_lines(self) -> list[str]:
        """Render the brief as the line list the generation graph consumes."""
        lines = [f"대상 연차: {self.seniority}", f"주제: {self.topic}"]
        if self.notes:
            lines.append(f"중점 비기능적 요구사항: {self.notes}")
        return lines


def load_seniority_criteria() -> str:
    """연차별 비교에 필요한 전체 기준을 읽고 누락·중복·빈 섹션은 거부한다."""
    text = (RESOURCES / "seniority-criteria.md").read_text(encoding="utf-8")
    for seniority in Seniority:
        parts = text.split(f"\n## {seniority}\n")
        if len(parts) != 2:
            raise ValueError(f"{seniority} 평가 기준 섹션은 정확히 하나여야 한다.")
        if not parts[1].split("\n## ", 1)[0].strip():
            raise ValueError(f"{seniority} 평가 기준이 비어 있다.")
    return text
