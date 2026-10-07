import pytest

from archgen.domain.brief import InterviewBrief, Seniority


@pytest.mark.parametrize("blank", ["", "   ", "\n"])
def test_brief_rejects_a_blank_topic(blank: str) -> None:
    """주제가 비면 Planner 프롬프트가 `- 주제: `로 나간다."""
    with pytest.raises(ValueError):
        InterviewBrief(seniority=Seniority.MIDDLE, topic=blank)


def test_brief_strips_the_topic() -> None:
    assert InterviewBrief(seniority=Seniority.MIDDLE, topic="  채팅  ").topic == "채팅"


@pytest.mark.parametrize("blank", ["", "   ", "\n"])
def test_blank_notes_mean_no_notes(blank: str) -> None:
    """공백뿐인 중점 요구사항이 프롬프트에 빈 지시로 들어가지 않게 한다."""
    assert (
        InterviewBrief(seniority=Seniority.MIDDLE, topic="채팅", notes=blank).notes
        is None
    )


def test_brief_strips_the_notes() -> None:
    brief = InterviewBrief(seniority=Seniority.MIDDLE, topic="채팅", notes="  가용성 ")

    assert brief.notes == "가용성"
