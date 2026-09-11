"""Slot-filling state machine driving the interview prompts in the TUI.

The filler owns *what* to ask and *whether* an answer is acceptable; the Textual
app only renders the current slot and forwards raw input. Required slots stay on
the current question until they receive a usable answer.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ..domain.brief import InterviewBrief, Seniority

EMPTY_DISPLAY = "(없음)"


class SlotError(ValueError):
    """Raised by a slot parser when the raw answer cannot be used."""


@dataclass(frozen=True)
class Slot:
    """One question in the interview."""

    key: str
    label: str
    prompt: str
    placeholder: str
    required: bool = True
    choices: tuple[str, ...] = ()
    parse: Callable[[str], object] = str


@dataclass(frozen=True)
class SlotResult:
    """Outcome of one answer: either accepted, or rejected with a reason."""

    accepted: bool
    error: str | None = None


def _parse_seniority(raw: str) -> Seniority:
    """Accept either a level label ("주니어") or its 1-based number ("2")."""
    levels = list(Seniority)
    if raw.isdigit() and 1 <= int(raw) <= len(levels):
        return levels[int(raw) - 1]
    try:
        return Seniority(raw)
    except ValueError:
        labels = " / ".join(f"{i}. {level}" for i, level in enumerate(levels, 1))
        raise SlotError(f"다음 중에서 골라 주세요 — {labels}") from None


SLOTS: tuple[Slot, ...] = (
    Slot(
        key="seniority",
        label="대상 연차",
        prompt="대상 연차를 골라 주세요 (번호 또는 이름).",
        placeholder="1. 신입  2. 주니어  3. 미들  4. 시니어",
        choices=tuple(level.value for level in Seniority),
        parse=_parse_seniority,
    ),
    Slot(
        key="topic",
        label="주제",
        prompt="어떤 주제로 문제를 만들까요?",
        placeholder="예: 주문/결제 시스템",
    ),
    Slot(
        key="notes",
        label="더 하고 싶은 말",
        prompt="더 하고 싶은 말이 있으면 적어 주세요. 없으면 Enter.",
        placeholder="예: 멱등성과 정합성을 깊게 보고 싶어요 (선택)",
        required=False,
    ),
)


@dataclass
class SlotFiller:
    """Walk the slots in order, collecting one validated answer per slot."""

    slots: tuple[Slot, ...] = SLOTS
    values: dict[str, object] = field(default_factory=dict)
    _index: int = 0

    @property
    def current(self) -> Slot | None:
        """The slot awaiting an answer, or ``None`` once every slot is filled."""
        if self.is_complete:
            return None
        return self.slots[self._index]

    @property
    def is_complete(self) -> bool:
        return self._index >= len(self.slots)

    @property
    def filled(self) -> tuple[tuple[str, str], ...]:
        """Answered slots as ``(label, display value)`` pairs for the transcript."""
        answered = self.slots[: self._index]
        return tuple(
            (slot.label, str(self.values.get(slot.key) or EMPTY_DISPLAY))
            for slot in answered
        )

    def submit(self, raw: str) -> SlotResult:
        """Record one answer, staying on the slot when the answer is unusable."""
        slot = self.current
        if slot is None:
            return SlotResult(accepted=False, error="이미 모든 항목을 받았습니다.")

        answer = raw.strip()
        if not answer:
            if slot.required:
                return SlotResult(
                    accepted=False, error=f"{slot.label}은(는) 필수 입력입니다."
                )
            value = None
        else:
            try:
                value = slot.parse(answer)
            except SlotError as error:
                return SlotResult(accepted=False, error=str(error))

        self.values[slot.key] = value
        self._index += 1
        return SlotResult(accepted=True)

    def build_brief(self) -> InterviewBrief:
        """Freeze the collected answers, refusing to build a half-filled brief."""
        missing = [slot.label for slot in self.slots[self._index :] if slot.required]
        if missing:
            raise ValueError(f"아직 받지 못한 필수 항목이 있습니다: {', '.join(missing)}")
        return InterviewBrief(
            seniority=self.values["seniority"],
            topic=self.values["topic"],
            notes=self.values.get("notes"),
        )
