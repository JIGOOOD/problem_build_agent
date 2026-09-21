from pathlib import Path

import yaml

from archgen.domain.nfr import NFRExport

GOLDEN = Path(__file__).resolve().parents[1] / "resources" / "golden" / "chat.yaml"

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
        assert nfr.target or nfr.qualitative_target
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
