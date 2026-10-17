import pytest
import yaml

from archgen.domain.nfr import NFRExport
from archgen.paths import GOLDEN_DIR

GOLDEN = GOLDEN_DIR / "chat.yaml"

# 골든셋 파일은 NFRExport의 상위집합이다. topic / target_level / documents는
# 파이프라인 상태이지 LLM 출력이 아니라서 스키마에 들어가지 않는다.
EXPORT_KEYS = ("confirmed_nfrs", "tradeoffs", "rubric")


def _golden_raw() -> dict:
    return yaml.safe_load(GOLDEN.read_text(encoding="utf-8"))


@pytest.fixture
def golden_export() -> NFRExport:
    """골든셋 형식이 바뀌면 여기만 고친다. 테스트마다 새 객체를 받는다."""
    raw = _golden_raw()
    return NFRExport.model_validate({key: raw[key] for key in EXPORT_KEYS})


@pytest.fixture
def golden_document_ids() -> set[str]:
    """골든셋이 근거로 쓴 문서 id. 파이프라인에서는 크롤러가 만든 목록이다."""
    return {document["id"] for document in _golden_raw()["documents"]}
