"""규칙으로 판정할 수 있는 Pre-Render 검사. 각 검사는 NFRExport를 받아 Finding을 낸다."""

from __future__ import annotations

from archgen.domain.nfr import NFRExport
from archgen.harness.findings import Finding, FindingCode, Severity

WEIGHT_TOTAL = 100
# 면접에서 NFR에 쓰는 10~15분 안에 다룰 수 있는 개수. 기본은 3개.
CRITERIA_MIN, CRITERIA_MAX = 2, 4


def check_weight_sum(export: NFRExport) -> list[Finding]:
    """core.weight-sum — 각 weight가 1~100이고 합이 정확히 100인가."""
    criteria = export.rubric.criteria
    findings = [
        Finding(
            code=FindingCode.WEIGHT_OUT_OF_RANGE,
            severity=Severity.ERROR,
            path=f"rubric.criteria[{i}].weight",
            message=f"{c.id}의 weight {c.weight}가 1~{WEIGHT_TOTAL} 밖이다.",
        )
        for i, c in enumerate(criteria)
        if not 1 <= c.weight <= WEIGHT_TOTAL
    ]

    total = sum(c.weight for c in criteria)
    if total != WEIGHT_TOTAL:
        findings.append(
            Finding(
                code=FindingCode.WEIGHT_SUM_INVALID,
                severity=Severity.ERROR,
                path="rubric.criteria",
                message=f"criterion weight 합이 {total}이다. {WEIGHT_TOTAL}이어야 한다.",
            )
        )
    return findings


def check_criteria_count(export: NFRExport) -> list[Finding]:
    """core.criteria-count — criterion이 2~4개인가."""
    count = len(export.rubric.criteria)
    if CRITERIA_MIN <= count <= CRITERIA_MAX:
        return []
    return [
        Finding(
            code=FindingCode.CRITERIA_COUNT_OUT_OF_RANGE,
            severity=Severity.ERROR,
            path="rubric.criteria",
            message=(
                f"criterion이 {count}개다. {CRITERIA_MIN}~{CRITERIA_MAX}개여야 한다."
            ),
        )
    ]
