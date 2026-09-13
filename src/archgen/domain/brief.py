"""The interview brief collected from the user before generation starts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Seniority(StrEnum):
    """Target experience level the generated problem should suit."""

    ENTRY = "신입"
    JUNIOR = "주니어"
    MIDDLE = "미들"
    SENIOR = "시니어"


@dataclass(frozen=True)
class InterviewBrief:
    """One completed slot-filling round."""

    seniority: Seniority
    topic: str
    notes: str | None = None

    def to_lines(self) -> list[str]:
        """Render the brief as the line list the generation graph consumes."""
        lines = [f"대상 연차: {self.seniority}", f"주제: {self.topic}"]
        if self.notes:
            lines.append(f"중점 비기능적 요구사항: {self.notes}")
        return lines
