import pytest
import yaml
from pydantic import ValidationError

from archgen.domain.nfr import ConfirmedNFR, NFRExport, RubricLevel
from archgen.paths import GOLDEN_DIR

GOLDEN = GOLDEN_DIR / "chat.yaml"

# 골든셋 파일은 NFRExport의 상위집합이다. topic / target_level / documents는
# 파이프라인 상태이지 LLM 출력이 아니라서 스키마에 들어가지 않는다.
EXPORT_KEYS = ("confirmed_nfrs", "tradeoffs", "rubric")


def golden_export() -> NFRExport:
    raw = yaml.safe_load(GOLDEN.read_text(encoding="utf-8"))
    return NFRExport.model_validate({key: raw[key] for key in EXPORT_KEYS})


def test_golden_set_loads_without_losing_fields() -> None:
    """골든셋 내용이 바뀌어도, 스키마가 필드를 흘리지 않는 한 통과한다."""
    export = golden_export()

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


def test_nfr_export_survives_a_dump_and_load_round_trip() -> None:
    export = golden_export()

    assert NFRExport.model_validate(export.model_dump()) == export


def test_nfr_export_survives_a_json_round_trip() -> None:
    """LLM 응답과 eval 저장은 dict가 아니라 JSON 문자열을 지난다."""
    export = golden_export()

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
