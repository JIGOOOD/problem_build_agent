"""검사가 남기는 지적 하나. 하네스와 Judge가 같은 형식을 쓴다."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, StringConstraints

# 공백만 있는 값도 비어 있는 것으로 본다.
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Severity(StrEnum):
    """ERROR는 repair 대상, WARN은 기록만 한다."""

    ERROR = "ERROR"
    WARN = "WARN"


class FindingCode(StrEnum):
    """Finding code 전체 목록. 검사를 추가할 때 여기에 먼저 등록한다."""

    # core.weight-sum
    WEIGHT_OUT_OF_RANGE = "WEIGHT_OUT_OF_RANGE"  # criterion weight가 1~100 밖
    WEIGHT_SUM_INVALID = "WEIGHT_SUM_INVALID"  # weight 합이 100이 아님
    # core.criteria-count
    CRITERIA_COUNT_OUT_OF_RANGE = "CRITERIA_COUNT_OUT_OF_RANGE"  # criterion이 2~4개 밖
    # core.levels
    LEVEL_MISSING = "LEVEL_MISSING"  # score 0~3 중 빠진 게 있음
    LEVEL_DUPLICATED = "LEVEL_DUPLICATED"  # 같은 score가 두 번 이상
    LEVEL_DESCRIPTOR_MISSING = "LEVEL_DESCRIPTOR_MISSING"  # descriptor가 비어 있음
    # 한 criterion 안에서 서술이 겹침
    LEVEL_DESCRIPTOR_DUPLICATED = "LEVEL_DESCRIPTOR_DUPLICATED"
    # core.cross-ref
    ID_DUPLICATED = "ID_DUPLICATED"  # 같은 종류 안에서 id가 겹침
    # criterion이 평가하는 NFR이 없음
    CRITERION_NFR_REFERENCE_MISSING = "CRITERION_NFR_REFERENCE_MISSING"
    CRITERION_MULTI_NFR = "CRITERION_MULTI_NFR"  # criterion 하나가 NFR 둘 이상을 평가
    NFR_REFERENCE_INVALID = "NFR_REFERENCE_INVALID"  # 없는 NFR id를 가리킴
    NFR_NOT_COVERED = "NFR_NOT_COVERED"  # 어느 criterion도 평가하지 않는 NFR
    NFR_MULTI_COVERED = "NFR_MULTI_COVERED"  # 둘 이상의 criterion이 평가하는 NFR
    EVIDENCE_REF_UNKNOWN = "EVIDENCE_REF_UNKNOWN"  # 크롤한 적 없는 문서를 인용
    EVIDENCE_REF_MISSING = "EVIDENCE_REF_MISSING"  # 근거 문서가 하나도 없음
    # trade-off가 어느 NFR에도 연결되지 않음
    TRADEOFF_NFR_REFERENCE_MISSING = "TRADEOFF_NFR_REFERENCE_MISSING"
    # Post-Render — 렌더된 md를 되읽어 원본과 비교한다. 렌더러 코드 버그라 repair 대상이 아니다.
    # code 하나가 md의 한 부분을 가리킨다.
    # 머리말: 주제·대상 연차·배점 합·`## NFR` 헤딩·채점 규칙
    RENDER_HEADER_MISMATCH = "RENDER_HEADER_MISMATCH"
    # 요약표 행이 criterion [id, title, 배점] 목록과 다름
    RENDER_SUMMARY_MISMATCH = "RENDER_SUMMARY_MISMATCH"
    # criterion 섹션 id 목록이 다름 (누락·중복·순서)
    RENDER_SECTIONS_MISMATCH = "RENDER_SECTIONS_MISMATCH"
    RENDER_HEADING_MISMATCH = "RENDER_HEADING_MISMATCH"  # 헤딩의 title·배점이 다름
    RENDER_DESCRIPTION_MISMATCH = "RENDER_DESCRIPTION_MISMATCH"  # 평가 항목이 다름
    RENDER_REQUIREMENT_MISMATCH = "RENDER_REQUIREMENT_MISMATCH"  # 요구 수준이 NFR과 다름
    RENDER_TRADEOFF_MISMATCH = "RENDER_TRADEOFF_MISMATCH"  # 관련 trade-off 목록이 다름
    RENDER_LEVELS_MISMATCH = "RENDER_LEVELS_MISMATCH"  # 레벨표 (score, 서술) 목록이 다름


class Finding(BaseModel):
    """어느 위치(path)에서 어떤 규칙(code)이 깨졌는지."""

    code: NonBlank
    severity: Severity
    path: NonBlank
    message: NonBlank
