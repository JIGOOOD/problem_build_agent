import pytest

from archgen.domain.brief import Seniority
from archgen.tui.slots import SlotFiller


def fill(filler: SlotFiller, *answers: str) -> None:
    for answer in answers:
        assert filler.submit(answer).accepted


def test_first_slot_asks_for_seniority_with_choices() -> None:
    filler = SlotFiller()

    assert filler.current.key == "seniority"
    assert filler.current.required is True
    assert filler.current.choices == ("Middle", "Senior")


def test_required_slot_repeats_until_it_gets_a_value() -> None:
    filler = SlotFiller()

    for blank in ("", "   ", "\t"):
        result = filler.submit(blank)
        assert result.accepted is False
        assert "대상 연차" in result.error
        assert filler.current.key == "seniority", "빈 입력은 슬롯을 넘기지 않는다"


@pytest.mark.parametrize(
    "raw",
    ["경력 많음", "신입", "주니어", "Staff+", "3", "4", "5", "1.Senior", "2.Middle"],
)
def test_seniority_rejects_an_unknown_level(raw: str) -> None:
    filler = SlotFiller()

    result = filler.submit(raw)

    assert result.accepted is False
    assert "Middle" in result.error
    assert filler.current.key == "seniority"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Middle", Seniority.MIDDLE),
        ("middle", Seniority.MIDDLE),
        ("MIDDLE", Seniority.MIDDLE),
        ("1.Middle", Seniority.MIDDLE),
        ("1.MIDDLE", Seniority.MIDDLE),
        ("1. Middle", Seniority.MIDDLE),
        ("senior", Seniority.SENIOR),
        ("SENIOR", Seniority.SENIOR),
        ("2.Senior", Seniority.SENIOR),
        ("2. SENIOR", Seniority.SENIOR),
        ("  Senior  ", Seniority.SENIOR),
        ("1", Seniority.MIDDLE),
        ("2", Seniority.SENIOR),
    ],
)
def test_seniority_accepts_a_label_or_its_number(raw: str, expected: Seniority) -> None:
    filler = SlotFiller()

    assert filler.submit(raw).accepted
    assert filler.current is None
    assert filler.values["seniority"] == expected


def test_seniority_finishes_slots_and_scope_builds_the_brief() -> None:
    filler = SlotFiller()
    fill(filler, "Senior")

    assert filler.is_complete
    assert filler.current is None
    assert not filler.submit("주제").accepted
    brief = filler.build_brief(
        "결제 처리 시스템", "결제 요청부터 결과 반영까지", "중복 결제 방지"
    )
    assert brief.seniority is Seniority.SENIOR
    assert brief.topic == "결제 처리 시스템"
    assert brief.scope == "결제 요청부터 결과 반영까지"
    assert brief.focus == "중복 결제 방지"


def test_build_brief_before_completion_is_an_error() -> None:
    filler = SlotFiller()
    with pytest.raises(ValueError, match="대상 연차"):
        filler.build_brief("결제", "결제 요청부터 결과 반영까지", "중복 방지")


def test_filled_answers_are_exposed_for_the_transcript() -> None:
    filler = SlotFiller()
    fill(filler, "Middle")

    assert filler.filled == (("대상 연차", "Middle"),)


def test_brief_converts_to_the_graph_input() -> None:
    filler = SlotFiller()
    fill(filler, "Senior")

    assert filler.build_brief(
        "결제 처리 시스템", "결제 요청부터 결과 반영까지", "상태 일관성"
    ).to_lines() == [
        "대상 연차: Senior",
        "주제: 결제 처리 시스템",
        "확정 범위: 결제 요청부터 결과 반영까지",
        "평가 초점: 상태 일관성",
    ]
