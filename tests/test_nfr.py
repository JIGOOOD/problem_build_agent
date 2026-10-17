from collections.abc import Callable

import pytest
from pydantic import ValidationError

from archgen.domain.nfr import (
    ConfirmedNFR,
    NFRExport,
    RubricCriterion,
    RubricLevel,
    Tradeoff,
)


def test_golden_set_loads_without_losing_fields(golden_export: NFRExport) -> None:
    """골든셋 내용이 바뀌어도, 스키마가 필드를 흘리지 않는 한 통과한다."""
    export = golden_export

    assert export.confirmed_nfrs, "확정 NFR이 하나도 안 들어왔다"
    assert export.tradeoffs, "trade-off가 하나도 안 들어왔다"
    assert export.rubric.criteria, "criterion이 하나도 안 들어왔다"

    for nfr in export.confirmed_nfrs:
        assert nfr.id and nfr.kind and nfr.statement and nfr.rationale
        assert nfr.evidence_refs

    for criterion in export.rubric.criteria:
        assert criterion.id and criterion.title and criterion.weight
        assert criterion.related_nfr_ids
        assert [lv.score for lv in criterion.levels] == [0, 1, 2, 3]
        assert all(lv.descriptor for lv in criterion.levels)


def test_nfr_export_survives_a_dump_and_load_round_trip(
    golden_export: NFRExport,
) -> None:
    export = golden_export

    assert NFRExport.model_validate(export.model_dump()) == export


def test_nfr_export_survives_a_json_round_trip(golden_export: NFRExport) -> None:
    """LLM 응답과 eval 저장은 dict가 아니라 JSON 문자열을 지난다."""
    export = golden_export

    assert NFRExport.model_validate_json(export.model_dump_json()) == export


def a_confirmed_nfr(**overrides: object) -> dict:
    base = {
        "id": "NFR-1",
        "kind": "latency",
        "statement": "메시지는 낮은 지연으로 수신자에게 도달해야 한다.",
        "rationale": "D1이 전파 경로의 지연 목표를 명시한다.",
        "qualitative_target": "낮은 지연",
        "evidence_refs": ["D1"],
    }
    return base | overrides


A_TARGET = {"value": 500, "unit": "ms", "condition": "p99"}


@pytest.mark.parametrize(
    ("target", "qualitative_target", "accepted"),
    [
        (None, None, False),          # 채점할 목표가 없다
        (A_TARGET, None, True),       # 정량 목표만
        (None, "낮은 지연", True),      # 정성 목표만 — 골든셋이 쓰는 형태
        (A_TARGET, "낮은 지연", False), # 정성 목표는 수치가 없을 때만 쓴다
    ],
)
def test_confirmed_nfr_takes_exactly_one_kind_of_target(
    target: dict | None, qualitative_target: str | None, accepted: bool
) -> None:
    payload = a_confirmed_nfr(target=target, qualitative_target=qualitative_target)

    if accepted:
        assert ConfirmedNFR.model_validate(payload)
    else:
        with pytest.raises(ValidationError, match="target"):
            ConfirmedNFR.model_validate(payload)


def test_rubric_level_rejects_a_score_outside_zero_to_three() -> None:
    for score in (-1, 4):
        with pytest.raises(ValidationError):
            RubricLevel(score=score, descriptor="레벨 서술이 여기에 들어간다.")


def a_criterion(weight: object) -> dict:
    return {"id": "C1", "title": "제목", "description": "설명", "weight": weight}


@pytest.mark.parametrize("weight", [45, 45.0, "45"])
def test_rubric_criterion_takes_a_whole_number_weight(weight: object) -> None:
    """LLM이 45.0으로 내도 값은 정수라 받는다."""
    assert RubricCriterion.model_validate(a_criterion(weight)).weight == 45


@pytest.mark.parametrize("weight", [45.5, float("nan"), float("inf"), "45점", True])
def test_rubric_criterion_rejects_a_non_whole_number_weight(weight: object) -> None:
    """true가 1점으로 바뀌어 들어오면 조용히 잘못된 배점이 된다."""
    with pytest.raises(ValidationError):
        RubricCriterion.model_validate(a_criterion(weight))


def a_tradeoff(**overrides: object) -> dict:
    return {"id": "TO-1", "description": "설명"} | overrides


ID_OWNERS = [
    (ConfirmedNFR, a_confirmed_nfr),
    (Tradeoff, a_tradeoff),
    (RubricCriterion, lambda **o: a_criterion(45) | o),
]


@pytest.mark.parametrize(("model", "payload"), ID_OWNERS)
@pytest.mark.parametrize("blank", ["", "   "])
def test_ids_must_not_be_blank(model: type, payload: Callable, blank: str) -> None:
    """빈 id끼리는 참조가 서로 맞아서 cross-ref를 조용히 통과한다."""
    with pytest.raises(ValidationError):
        model.model_validate(payload(id=blank))


@pytest.mark.parametrize(("model", "payload"), ID_OWNERS)
def test_ids_are_stripped_of_surrounding_whitespace(
    model: type, payload: Callable
) -> None:
    """LLM이 붙인 공백 때문에 repair를 돌리지 않는다."""
    assert model.model_validate(payload(id=" NFR-1 ")).id == "NFR-1"


REF_FIELDS = [
    (ConfirmedNFR, a_confirmed_nfr, "evidence_refs"),
    (Tradeoff, a_tradeoff, "evidence_refs"),
    (Tradeoff, a_tradeoff, "related_nfr_ids"),
    (RubricCriterion, lambda **o: a_criterion(45) | o, "related_nfr_ids"),
]


@pytest.mark.parametrize(("model", "payload", "field"), REF_FIELDS)
def test_refs_are_stripped_like_the_ids_they_point_at(
    model: type, payload: Callable, field: str
) -> None:
    """id와 참조를 똑같이 정리해야 서로 어긋나지 않는다."""
    parsed = model.model_validate(payload(**{field: [" A-1", "A-2 "]}))

    assert getattr(parsed, field) == ["A-1", "A-2"]


@pytest.mark.parametrize(("model", "payload", "field"), REF_FIELDS)
@pytest.mark.parametrize("blank", ["", "   "])
def test_refs_must_not_be_blank(
    model: type, payload: Callable, field: str, blank: str
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload(**{field: ["A-1", blank]}))


TEXT_FIELDS = [
    (ConfirmedNFR, a_confirmed_nfr, "kind"),
    (ConfirmedNFR, a_confirmed_nfr, "statement"),
    (ConfirmedNFR, a_confirmed_nfr, "rationale"),
    (ConfirmedNFR, a_confirmed_nfr, "qualitative_target"),
    (Tradeoff, a_tradeoff, "description"),
    (RubricCriterion, lambda **o: a_criterion(45) | o, "title"),
    (RubricCriterion, lambda **o: a_criterion(45) | o, "description"),
]


@pytest.mark.parametrize(("model", "payload", "field"), TEXT_FIELDS)
@pytest.mark.parametrize("blank", ["", "   "])
def test_text_fields_must_not_be_blank(
    model: type, payload: Callable, field: str, blank: str
) -> None:
    """빈 본문은 하네스를 통과해 채점표에 빈칸으로 렌더된다."""
    with pytest.raises(ValidationError):
        model.model_validate(payload(**{field: blank}))


@pytest.mark.parametrize(("model", "payload", "field"), TEXT_FIELDS)
def test_text_fields_are_stripped(model: type, payload: Callable, field: str) -> None:
    """줄 끝 공백이 렌더된 md에 남지 않는다."""
    parsed = model.model_validate(payload(**{field: "  본문  "}))

    assert getattr(parsed, field) == "본문"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_target_value_must_be_a_finite_number(value: float) -> None:
    """NaN은 그대로 렌더되면 `NaN ms`가 된다."""
    with pytest.raises(ValidationError):
        ConfirmedNFR.model_validate(
            a_confirmed_nfr(
                qualitative_target=None, target={"value": value, "unit": "ms"}
            )
        )
