import pytest
from pydantic import ValidationError

from archgen.domain.nfr import NFRExport, Rubric
from archgen.harness.findings import Finding, Severity
from archgen.harness.runner import Runner


def an_export() -> NFRExport:
    return NFRExport(rubric=Rubric())


def a_finding(code: str) -> Finding:
    return Finding(
        code=code,
        severity=Severity.ERROR,
        path="rubric.criteria[0]",
        message="검사가 남긴 설명",
    )


def test_runner_collects_findings_from_every_check_in_order() -> None:
    seen: list[NFRExport] = []

    def first(export: NFRExport) -> list[Finding]:
        seen.append(export)
        return [a_finding("A"), a_finding("B")]

    def clean(export: NFRExport) -> list[Finding]:
        seen.append(export)
        return []

    def last(export: NFRExport) -> list[Finding]:
        seen.append(export)
        return [a_finding("C")]

    export = an_export()
    findings = Runner([first, clean, last]).run(export)

    assert [f.code for f in findings] == ["A", "B", "C"]
    assert seen == [export, export, export]


def test_runner_without_checks_reports_nothing() -> None:
    assert Runner([]).run(an_export()) == []


def test_runner_lets_a_crashing_check_fail_loudly() -> None:
    """검사가 터진 건 코드 버그다. Finding으로 바꾸면 repair가 헛돈다."""

    def broken(_export: NFRExport) -> list[Finding]:
        raise KeyError("검사 코드 버그")

    with pytest.raises(KeyError):
        Runner([broken]).run(an_export())


def test_severity_is_error_or_warn_only() -> None:
    """ERROR는 repair, WARN은 기록. 등급이 늘면 repair 분기를 다시 정해야 한다."""
    assert {s.value for s in Severity} == {"ERROR", "WARN"}


@pytest.mark.parametrize("blank", ["", "   "])
@pytest.mark.parametrize("field", ["code", "path", "message"])
def test_finding_rejects_a_blank_field(field: str, blank: str) -> None:
    """빈 지적은 repair 피드백에도 code별 집계에도 쓸 수 없다."""
    payload = a_finding("A").model_dump() | {field: blank}

    with pytest.raises(ValidationError):
        Finding.model_validate(payload)


def test_finding_rejects_an_unknown_severity() -> None:
    with pytest.raises(ValidationError):
        Finding(code="A", severity="FATAL", path="rubric", message="설명")
