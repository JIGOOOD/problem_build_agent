"""규칙으로 판정할 수 있는 Pre-Render 검사. 각 검사는 NFRExport를 받아 Finding을 낸다."""

from __future__ import annotations

from archgen.domain.nfr import NFRExport
from archgen.harness.findings import Finding, Severity

WEIGHT_TOTAL = 100


def check_weight_sum(export: NFRExport) -> list[Finding]:
    """core.weight-sum — 각 weight가 1~100이고 합이 정확히 100인가."""
    criteria = export.rubric.criteria
    findings = [
        Finding(
            code="WEIGHT_OUT_OF_RANGE",
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
                code="WEIGHT_SUM_INVALID",
                severity=Severity.ERROR,
                path="rubric.criteria",
                message=f"criterion weight 합이 {total}이다. {WEIGHT_TOTAL}이어야 한다.",
            )
        )
    return findings
