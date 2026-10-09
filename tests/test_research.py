import pytest
from pydantic import ValidationError

from archgen.domain.research import NFRCandidate


@pytest.mark.parametrize(
    ("raw", "kind"),
    [
        ("latency", "latency"),
        ("Latency", "latency"),
        ("Fault Tolerance", "fault_tolerance"),
        ("fault-tolerance", "fault_tolerance"),
        (" Fault  Tolerance ", "fault_tolerance"),
    ],
)
def test_candidate_kind_is_normalized_to_snake_case(raw: str, kind: str) -> None:
    """표기 흔들림은 코드로 고친다. 이걸로 LLM을 다시 부르면 비용만 든다."""
    assert NFRCandidate(kind=raw, reason="이유").kind == kind


@pytest.mark.parametrize("kind", ["", "   ", "1latency", "처리량"])
def test_candidate_kind_that_cannot_be_normalized_is_rejected(kind: str) -> None:
    """정리해도 snake_case가 안 되는 값만 재시도 대상으로 남긴다."""
    with pytest.raises(ValidationError):
        NFRCandidate(kind=kind, reason="이유")


@pytest.mark.parametrize(
    "raw",
    ["fault__tolerance", "fault_tolerance_", "_fault_tolerance", "Fault - Tolerance"],
)
def test_kind_underscores_are_collapsed(raw: str) -> None:
    """밑줄이 겹치거나 앞뒤에 남으면 Catalog 이름 fault_tolerance와 어긋난다."""
    assert NFRCandidate(kind=raw, reason="이유").kind == "fault_tolerance"


def test_candidate_starts_with_independent_empty_document_ids() -> None:
    first = NFRCandidate(kind="latency", reason="응답 시간")
    second = NFRCandidate(kind="availability", reason="가용성")

    assert first.doc_ids == []
    assert second.doc_ids == []
    first.doc_ids.append("doc-1")
    assert second.doc_ids == []
