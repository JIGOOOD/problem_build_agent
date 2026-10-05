import pytest

from archgen.domain.nfr import NFRExport
from archgen.harness.checks import (
    check_criteria_count,
    check_levels,
    check_weight_sum,
)
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


def with_levels(
    export: NFRExport, levels: list[tuple[int, str]], criterion: int = 0
) -> NFRExport:
    """골든 criterion 하나의 레벨만 (score, descriptor) 목록으로 바꾼다."""
    raw = export.model_dump()
    raw["rubric"]["criteria"][criterion]["levels"] = [
        {"score": score, "descriptor": descriptor} for score, descriptor in levels
    ]
    return NFRExport.model_validate(raw)


def scored(*scores: int) -> list[tuple[int, str]]:
    """score마다 서로 다른 descriptor를 붙인다."""
    return [(s, f"{s}점 수준의 답변을 설명하는 서술 {i}") for i, s in enumerate(scores)]


def level_findings(export: NFRExport) -> list[tuple[str, str]]:
    findings = check_levels(export)
    assert all(f.severity is Severity.ERROR for f in findings)
    return [(f.code, f.path) for f in findings]


def test_levels_pass_the_golden_set(golden_export: NFRExport) -> None:
    assert check_levels(golden_export) == []


@pytest.mark.parametrize("scores", [(0, 1, 3), (1, 2, 3), (0, 1, 2), ()])
def test_levels_flag_a_missing_score(
    golden_export: NFRExport, scores: tuple[int, ...]
) -> None:
    """빠진 score가 몇 개든 criterion당 한 번만 낸다."""
    export = with_levels(golden_export, scored(*scores))

    assert level_findings(export) == [("LEVEL_MISSING", "rubric.criteria[0].levels")]


def test_levels_flag_a_duplicated_score(golden_export: NFRExport) -> None:
    export = with_levels(golden_export, scored(0, 1, 2, 2, 3))

    assert level_findings(export) == [("LEVEL_DUPLICATED", "rubric.criteria[0].levels")]


def test_levels_flag_a_duplicate_that_hides_a_missing_score(
    golden_export: NFRExport,
) -> None:
    """레벨이 4개라 개수만 보면 멀쩡해 보인다."""
    export = with_levels(golden_export, scored(0, 1, 1, 3))

    assert set(level_findings(export)) == {
        ("LEVEL_MISSING", "rubric.criteria[0].levels"),
        ("LEVEL_DUPLICATED", "rubric.criteria[0].levels"),
    }


@pytest.mark.parametrize("blank", ["", "   "])
def test_levels_flag_a_blank_descriptor(golden_export: NFRExport, blank: str) -> None:
    levels = scored(0, 1, 2, 3)
    levels[2] = (2, blank)

    assert level_findings(with_levels(golden_export, levels)) == [
        ("LEVEL_DESCRIPTOR_MISSING", "rubric.criteria[0].levels[2].descriptor")
    ]


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("핵심 경로를 설명한다", "핵심 경로를 설명한다"),
        ("핵심 경로를  설명한다", " 핵심 경로를 설명한다 "),  # 공백만 다르다
    ],
)
def test_levels_flag_a_duplicated_descriptor(
    golden_export: NFRExport, first: str, second: str
) -> None:
    levels = scored(0, 1, 2, 3)
    levels[1] = (1, first)
    levels[2] = (2, second)

    assert level_findings(with_levels(golden_export, levels)) == [
        ("LEVEL_DESCRIPTOR_DUPLICATED", "rubric.criteria[0].levels[2].descriptor")
    ]


def test_levels_do_not_count_blank_descriptors_as_duplicates(
    golden_export: NFRExport,
) -> None:
    levels = scored(0, 1, 2, 3)
    levels[1] = (1, "")
    levels[2] = (2, "")

    assert level_findings(with_levels(golden_export, levels)) == [
        ("LEVEL_DESCRIPTOR_MISSING", "rubric.criteria[0].levels[1].descriptor"),
        ("LEVEL_DESCRIPTOR_MISSING", "rubric.criteria[0].levels[2].descriptor"),
    ]


def test_levels_point_at_the_criterion_that_broke(golden_export: NFRExport) -> None:
    export = with_levels(golden_export, scored(0, 1, 2), criterion=2)

    assert level_findings(export) == [("LEVEL_MISSING", "rubric.criteria[2].levels")]
