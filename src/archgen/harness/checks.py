"""규칙으로 판정할 수 있는 Pre-Render 검사. 각 검사는 NFRExport를 받아 Finding을 낸다."""

from __future__ import annotations

from collections import Counter

from archgen.domain.nfr import NFRExport, RubricCriterion
from archgen.harness.findings import Finding, FindingCode, Severity

WEIGHT_TOTAL = 100
# 면접에서 NFR에 쓰는 10~15분 안에 다룰 수 있는 개수. 기본은 3개.
CRITERIA_MIN, CRITERIA_MAX = 2, 4
SCORES = (0, 1, 2, 3)


def check_weight_sum(export: NFRExport) -> list[Finding]:
    """core.weight-sum — 각 weight가 1~100이고 합이 정확히 100인가."""
    criteria = export.rubric.criteria
    findings = [
        _error(
            FindingCode.WEIGHT_OUT_OF_RANGE,
            f"rubric.criteria[{i}].weight",
            f"{c.id}의 weight {c.weight}가 1~{WEIGHT_TOTAL} 밖이다.",
        )
        for i, c in enumerate(criteria)
        if not 1 <= c.weight <= WEIGHT_TOTAL
    ]

    total = sum(c.weight for c in criteria)
    if total != WEIGHT_TOTAL:
        findings.append(
            _error(
                FindingCode.WEIGHT_SUM_INVALID,
                "rubric.criteria",
                f"criterion weight 합이 {total}이다. {WEIGHT_TOTAL}이어야 한다.",
            )
        )
    return findings


def check_criteria_count(export: NFRExport) -> list[Finding]:
    """core.criteria-count — criterion이 2~4개인가."""
    count = len(export.rubric.criteria)
    if CRITERIA_MIN <= count <= CRITERIA_MAX:
        return []
    return [
        _error(
            FindingCode.CRITERIA_COUNT_OUT_OF_RANGE,
            "rubric.criteria",
            f"criterion이 {count}개다. {CRITERIA_MIN}~{CRITERIA_MAX}개여야 한다.",
        )
    ]


def check_levels(export: NFRExport) -> list[Finding]:
    """core.levels — criterion마다 score 0~3이 한 번씩, descriptor가 비지 않고 겹치지 않는가."""
    findings: list[Finding] = []
    for i, criterion in enumerate(export.rubric.criteria):
        path = f"rubric.criteria[{i}].levels"
        findings += _score_findings(criterion, path)
        findings += _descriptor_findings(criterion, path)
    return findings


def _score_findings(criterion: RubricCriterion, path: str) -> list[Finding]:
    counts = Counter(level.score for level in criterion.levels)
    findings = []
    if missing := [s for s in SCORES if s not in counts]:
        findings.append(
            _error(
                FindingCode.LEVEL_MISSING,
                path,
                f"{criterion.id}에 score {missing}가 없다.",
            )
        )
    if duplicated := sorted(s for s, n in counts.items() if n > 1):
        findings.append(
            _error(
                FindingCode.LEVEL_DUPLICATED,
                path,
                f"{criterion.id}에 score {duplicated}가 두 번 이상 있다.",
            )
        )
    return findings


def _descriptor_findings(criterion: RubricCriterion, path: str) -> list[Finding]:
    findings = []
    seen: set[str] = set()
    for j, level in enumerate(criterion.levels):
        # 공백 차이로 중복을 빠져나가지 못하게 정규화해서 비교한다.
        text = " ".join(level.descriptor.split())
        where = f"{path}[{j}].descriptor"
        if not text:
            findings.append(
                _error(
                    FindingCode.LEVEL_DESCRIPTOR_MISSING,
                    where,
                    f"{criterion.id}의 score {level.score} 서술이 비어 있다.",
                )
            )
        elif text in seen:
            findings.append(
                _error(
                    FindingCode.LEVEL_DESCRIPTOR_DUPLICATED,
                    where,
                    f"{criterion.id}의 score {level.score} 서술이 다른 레벨과 같다.",
                )
            )
        seen.add(text)
    return findings


def _error(code: FindingCode, path: str, message: str) -> Finding:
    return Finding(code=code, severity=Severity.ERROR, path=path, message=message)
