from collections.abc import Callable

import pytest
from helpers import edited

from archgen.domain.nfr import NFRExport
from archgen.harness.checks import (
    check_criteria_count,
    check_cross_ref,
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


def cross_ref_findings(export: NFRExport, document_ids: set[str]) -> set[tuple[str, str]]:
    findings = check_cross_ref(document_ids)(export)
    assert all(f.severity is Severity.ERROR for f in findings)
    assert len(findings) == len({(f.code, f.path) for f in findings}), (
        "같은 지적이 중복됐다"
    )
    return {(f.code, f.path) for f in findings}


def test_cross_ref_passes_the_golden_set(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    assert check_cross_ref(golden_document_ids)(golden_export) == []


def test_cross_ref_flags_a_criterion_without_an_nfr(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """criterion이 NFR을 잃으면 그 NFR도 평가되지 않는다."""

    def drop_nfr(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["related_nfr_ids"] = []

    assert cross_ref_findings(edited(golden_export, drop_nfr), golden_document_ids) == {
        ("CRITERION_NFR_REFERENCE_MISSING", "rubric.criteria[0].related_nfr_ids"),
        ("NFR_NOT_COVERED", "confirmed_nfrs[0]"),
    }


def test_cross_ref_flags_a_criterion_with_two_nfrs(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """점수 하나로 NFR 둘을 판정하면 채점이 갈린다. NFR-2는 C1·C2 두 곳에서 평가된다."""

    def add_nfr(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["related_nfr_ids"] = ["NFR-1", "NFR-2"]

    assert cross_ref_findings(edited(golden_export, add_nfr), golden_document_ids) == {
        ("CRITERION_MULTI_NFR", "rubric.criteria[0].related_nfr_ids"),
        ("NFR_MULTI_COVERED", "confirmed_nfrs[1]"),
    }


def test_cross_ref_flags_a_criterion_pointing_at_an_unknown_nfr(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    def point_elsewhere(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["related_nfr_ids"] = ["NFR-9"]

    export = edited(golden_export, point_elsewhere)

    assert cross_ref_findings(export, golden_document_ids) == {
        ("NFR_REFERENCE_INVALID", "rubric.criteria[0].related_nfr_ids"),
        ("NFR_NOT_COVERED", "confirmed_nfrs[0]"),
    }


def test_cross_ref_flags_a_tradeoff_pointing_at_an_unknown_nfr(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    def point_elsewhere(raw: dict) -> None:
        raw["tradeoffs"][1]["related_nfr_ids"] = ["NFR-9"]

    assert cross_ref_findings(
        edited(golden_export, point_elsewhere), golden_document_ids
    ) == {("NFR_REFERENCE_INVALID", "tradeoffs[1].related_nfr_ids")}


def test_cross_ref_flags_an_nfr_scored_by_two_criteria(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """빠진 NFR이 없어 NFR_NOT_COVERED로는 드러나지 않는 중복 평가."""
    export = with_criteria(golden_export, 4)  # C4가 C1을 복제해 NFR-1을 또 평가한다

    assert cross_ref_findings(export, golden_document_ids) == {
        ("NFR_MULTI_COVERED", "confirmed_nfrs[0]")
    }


@pytest.mark.parametrize("section", ["confirmed_nfrs", "tradeoffs"])
def test_cross_ref_flags_evidence_pointing_at_an_unknown_document(
    golden_export: NFRExport, golden_document_ids: set[str], section: str
) -> None:
    """출처를 지어낸 인용."""

    def cite_missing(raw: dict) -> None:
        raw[section][0]["evidence_refs"].append("D99")

    assert cross_ref_findings(
        edited(golden_export, cite_missing), golden_document_ids
    ) == {("EVIDENCE_REF_UNKNOWN", f"{section}[0].evidence_refs")}


def test_cross_ref_flags_every_citation_when_no_document_was_crawled(
    golden_export: NFRExport,
) -> None:
    """크롤이 전부 실패했는데 인용이 남아 있으면 모두 지어낸 것이다."""
    cited = [
        f"{section}[{i}].evidence_refs"
        for section in ("confirmed_nfrs", "tradeoffs")
        for i, item in enumerate(getattr(golden_export, section))
        if item.evidence_refs
    ]
    findings = check_cross_ref(set())(golden_export)

    assert {f.code for f in findings} == {"EVIDENCE_REF_UNKNOWN"}
    assert sorted({f.path for f in findings}) == sorted(cited)


def duplicate_nfr(raw: dict) -> None:
    # NFR은 참조 대상이라 id만 바꾸면 연결이 깨진다. 같은 NFR을 하나 더 둔다.
    raw["confirmed_nfrs"].append(raw["confirmed_nfrs"][0])


def duplicate_tradeoff_id(raw: dict) -> None:
    raw["tradeoffs"][1]["id"] = raw["tradeoffs"][0]["id"]


def duplicate_criterion_id(raw: dict) -> None:
    raw["rubric"]["criteria"][1]["id"] = raw["rubric"]["criteria"][0]["id"]


@pytest.mark.parametrize(
    ("edit", "path"),
    [
        (duplicate_nfr, "confirmed_nfrs[3].id"),
        (duplicate_tradeoff_id, "tradeoffs[1].id"),
        (duplicate_criterion_id, "rubric.criteria[1].id"),
    ],
)
def test_cross_ref_flags_a_duplicated_id(
    golden_export: NFRExport,
    golden_document_ids: set[str],
    edit: Callable[[dict], None],
    path: str,
) -> None:
    """id가 겹치면 참조가 어느 쪽을 가리키는지 모호해진다. 두 번째 것을 지적한다."""
    found = cross_ref_findings(edited(golden_export, edit), golden_document_ids)

    assert found == {("ID_DUPLICATED", path)}


def test_cross_ref_does_not_count_a_repeated_ref_as_two_criteria(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """같은 criterion 안의 반복은 CRITERION_MULTI_NFR 하나로 충분하다."""

    def repeat(raw: dict) -> None:
        raw["rubric"]["criteria"][0]["related_nfr_ids"] = ["NFR-1", "NFR-1"]

    assert cross_ref_findings(edited(golden_export, repeat), golden_document_ids) == {
        ("CRITERION_MULTI_NFR", "rubric.criteria[0].related_nfr_ids")
    }


@pytest.mark.parametrize("section", ["confirmed_nfrs", "tradeoffs"])
def test_cross_ref_flags_an_item_without_evidence(
    golden_export: NFRExport, golden_document_ids: set[str], section: str
) -> None:
    """근거 없는 NFR·trade-off는 LLM 기억에서 나온 것이다."""

    def drop_evidence(raw: dict) -> None:
        raw[section][0]["evidence_refs"] = []

    assert cross_ref_findings(
        edited(golden_export, drop_evidence), golden_document_ids
    ) == {("EVIDENCE_REF_MISSING", f"{section}[0].evidence_refs")}


def test_cross_ref_flags_a_tradeoff_without_an_nfr(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """어느 NFR에도 붙지 않은 trade-off는 렌더에서 조용히 빠진다."""

    def detach(raw: dict) -> None:
        raw["tradeoffs"][0]["related_nfr_ids"] = []

    assert cross_ref_findings(edited(golden_export, detach), golden_document_ids) == {
        ("TRADEOFF_NFR_REFERENCE_MISSING", "tradeoffs[0].related_nfr_ids")
    }


def test_cross_ref_rejects_document_ids_given_as_a_string() -> None:
    """문자열이면 "D1" in "D1 D2"가 부분 문자열로 참이 되어 조용히 통과한다."""
    with pytest.raises(TypeError):
        check_cross_ref("D1 D2 D3")


def test_cross_ref_keeps_the_document_ids_it_was_built_with(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """검사를 만든 뒤 호출한 쪽이 집합을 비워도 결과가 바뀌지 않는다."""
    check = check_cross_ref(golden_document_ids)
    golden_document_ids.clear()

    assert check(golden_export) == []


def test_cross_ref_ignores_whitespace_the_llm_added_to_an_id(
    golden_export: NFRExport, golden_document_ids: set[str]
) -> None:
    """id에만 공백이 붙고 참조는 깨끗해도 연결은 맞다."""

    def pad(raw: dict) -> None:
        raw["confirmed_nfrs"][0]["id"] = " NFR-1 "
        raw["confirmed_nfrs"][0]["evidence_refs"] = [" D2", "D3 "]

    assert check_cross_ref(golden_document_ids)(edited(golden_export, pad)) == []
