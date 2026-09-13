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
    assert filler.current.choices == ("신입", "주니어", "미들", "시니어")


def test_required_slot_repeats_until_it_gets_a_value() -> None:
    filler = SlotFiller()

    for blank in ("", "   ", "\t"):
        result = filler.submit(blank)
        assert result.accepted is False
        assert "대상 연차" in result.error
        assert filler.current.key == "seniority", "빈 입력은 슬롯을 넘기지 않는다"


def test_seniority_rejects_an_unknown_level() -> None:
    filler = SlotFiller()

    result = filler.submit("경력 많음")

    assert result.accepted is False
    assert "신입" in result.error
    assert filler.current.key == "seniority"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("주니어", Seniority.JUNIOR),
        ("  시니어  ", Seniority.SENIOR),
        ("2", Seniority.JUNIOR),
        ("4", Seniority.SENIOR),
    ],
)
def test_seniority_accepts_a_label_or_its_number(raw: str, expected: Seniority) -> None:
    filler = SlotFiller()

    assert filler.submit(raw).accepted
    assert filler.current.key == "topic" # 다음 질문으로 넘어갔는지
    assert filler.values["seniority"] == expected


def test_topic_is_required_too() -> None:
    filler = SlotFiller()
    fill(filler, "미들")

    result = filler.submit("  ")

    assert result.accepted is False
    assert "주제" in result.error
    assert filler.current.key == "topic"


def test_notes_are_optional_and_finish_the_interview() -> None:
    filler = SlotFiller()
    fill(filler, "시니어", "주문/결제 시스템", "")

    assert filler.is_complete
    assert filler.current is None

    brief = filler.build_brief()
    assert brief.seniority is Seniority.SENIOR
    assert brief.topic == "주문/결제 시스템"
    assert brief.notes is None


def test_notes_are_kept_when_provided() -> None:
    filler = SlotFiller()
    fill(filler, "1", "채팅 서비스", "  멀티 리전 고려  ")

    brief = filler.build_brief()
    assert brief.seniority is Seniority.ENTRY
    assert brief.notes == "멀티 리전 고려"


def test_build_brief_before_completion_is_an_error() -> None:
    filler = SlotFiller()
    fill(filler, "주니어")

    with pytest.raises(ValueError, match="주제"):
        filler.build_brief()


def test_filled_answers_are_exposed_for_the_transcript() -> None:
    filler = SlotFiller()
    fill(filler, "미들", "피드 랭킹", "")

    assert filler.filled == (
        ("대상 연차", "미들"),
        ("주제", "피드 랭킹"),
        ("중점 비기능적 요구사항", "(없음)"),
    )


def test_brief_converts_to_the_graph_input() -> None:
    filler = SlotFiller()
    fill(filler, "시니어", "주문/결제 시스템", "중복 결제 시 일관성 유지 로직 등")

    assert filler.build_brief().to_lines() == [
        "대상 연차: 시니어",
        "주제: 주문/결제 시스템",
        "중점 비기능적 요구사항: 중복 결제 시 일관성 유지 로직 등",
    ]
