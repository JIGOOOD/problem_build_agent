"""여러 테스트 파일이 함께 쓰는 헬퍼. fixture가 아닌 일반 함수라 conftest 대신 여기에 둔다."""

from collections.abc import Callable

from archgen.domain.nfr import NFRExport


def edited(export: NFRExport, edit: Callable[[dict], None]) -> NFRExport:
    """골든셋 dict를 직접 고친 뒤 스키마 검증을 거쳐 되돌린다."""
    raw = export.model_dump()
    edit(raw)
    return NFRExport.model_validate(raw)
