import pytest

from archgen.domain.nfr import NFRExport
from archgen.harness.checks import check_criteria_count, check_weight_sum
from archgen.harness.findings import Severity


def with_criteria(export: NFRExport, count: int) -> NFRExport:
    """골든 criterion을 돌아가며 복제해 criterion 개수만 바꾼다.

    스키마 검증을 거치므로 파싱 단계에서 막히는 입력은 만들 수 없다.
    """
    raw = export.model_dump()
    golden = raw["rubric"]["criteria"]
    raw["rubric"]["criteria"] = [
        golden[i % len(golden)] | {"id": f"C{i + 1}"} for i in range(count)
    ]
    return NFRExport.model_validate(raw)


def with_weights(export: NFRExport, weights: list[int]) -> NFRExport:
    """criterion을 weights 개수만큼 두고 weight만 바꾼다."""
    raw = with_criteria(export, len(weights)).model_dump()
    for criterion, weight in zip(raw["rubric"]["criteria"], weights, strict=True):
        criterion["weight"] = weight
    return NFRExport.model_validate(raw)


def codes_and_paths(export: NFRExport) -> list[tuple[str, str]]:
    return [(f.code, f.path) for f in check_weight_sum(export)]


def test_weight_sum_passes_the_golden_set(golden_export: NFRExport) -> None:
    assert check_weight_sum(golden_export) == []


@pytest.mark.parametrize("weights", [[45, 30, 24], [45, 30, 26]])
def test_weight_sum_flags_a_total_off_by_one(
    golden_export: NFRExport, weights: list[int]
) -> None:
    findings = check_weight_sum(with_weights(golden_export, weights))

    assert [(f.code, f.path) for f in findings] == [
        ("WEIGHT_SUM_INVALID", "rubric.criteria")
    ]
    assert findings[0].severity is Severity.ERROR


def test_weight_sum_flags_an_empty_rubric(golden_export: NFRExport) -> None:
    """criterion이 없으면 합이 0이다. 조용히 통과시키지 않는다."""
    assert codes_and_paths(with_weights(golden_export, [])) == [
        ("WEIGHT_SUM_INVALID", "rubric.criteria")
    ]


@pytest.mark.parametrize("weights", [[100], [1, 99]])
def test_weight_range_accepts_one_to_hundred(
    golden_export: NFRExport, weights: list[int]
) -> None:
    assert codes_and_paths(with_weights(golden_export, weights)) == []


@pytest.mark.parametrize(
    "weights",
    [
        [100, 0],  # 0점짜리 criterion은 면접 시간만 쓴다
        [150, -50],  # 합은 맞지만 둘 다 범위 밖
        [101, -1],
    ],
)
def test_weight_range_flags_each_criterion_outside_the_range(
    golden_export: NFRExport, weights: list[int]
) -> None:
    out_of_range = [
        f"rubric.criteria[{i}].weight" for i, w in enumerate(weights) if not 1 <= w <= 100
    ]

    assert codes_and_paths(with_weights(golden_export, weights)) == [
        ("WEIGHT_OUT_OF_RANGE", path) for path in out_of_range
    ]


def test_weight_range_and_sum_are_both_reported_as_errors(
    golden_export: NFRExport,
) -> None:
    """한 위반이 다른 위반을 가리면 repair가 한 번에 못 고친다. 순서는 묻지 않는다."""
    findings = check_weight_sum(with_weights(golden_export, [0, 99]))

    assert {(f.code, f.path, f.severity) for f in findings} == {
        ("WEIGHT_OUT_OF_RANGE", "rubric.criteria[0].weight", Severity.ERROR),
        ("WEIGHT_SUM_INVALID", "rubric.criteria", Severity.ERROR),
    }
    assert len(findings) == 2


def test_criteria_count_passes_the_golden_set(golden_export: NFRExport) -> None:
    assert check_criteria_count(golden_export) == []


@pytest.mark.parametrize("count", [2, 4])
def test_criteria_count_accepts_two_to_four(golden_export: NFRExport, count: int) -> None:
    assert check_criteria_count(with_criteria(golden_export, count)) == []


@pytest.mark.parametrize("count", [0, 1, 5])
def test_criteria_count_flags_a_count_outside_two_to_four(
    golden_export: NFRExport, count: int
) -> None:
    """0개면 채점할 게 없고, 5개 이상이면 면접 10~15분 안에 못 다룬다."""
    findings = check_criteria_count(with_criteria(golden_export, count))

    assert [(f.code, f.path, f.severity) for f in findings] == [
        ("CRITERIA_COUNT_OUT_OF_RANGE", "rubric.criteria", Severity.ERROR)
    ]
