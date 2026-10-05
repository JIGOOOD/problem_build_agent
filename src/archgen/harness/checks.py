"""규칙으로 판정할 수 있는 Pre-Render 검사. 각 검사는 NFRExport를 받아 Finding을 낸다.

실행마다 달라지는 입력(크롤한 문서 목록 등)이 필요한 검사는 그 입력으로 검사를 만들어 돌려준다.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Set as AbstractSet

from archgen.domain.nfr import NFRExport, RubricCriterion
from archgen.harness.findings import Finding, FindingCode, Severity
from archgen.harness.runner import Check

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


def check_cross_ref(document_ids: AbstractSet[str]) -> Check:
    """core.cross-ref — id 참조가 실제 대상을 가리키는가.

    문서 목록은 LLM 출력이 아니라 크롤 결과라서, 실행마다 그 목록으로 검사를 만든다.
    """
    if isinstance(document_ids, str):
        # "D1" in "D1 D2"가 부분 문자열로 참이 되어 모든 인용이 조용히 통과한다.
        raise TypeError("document_ids는 문서 id 집합이어야 한다")
    # 만든 뒤 호출한 쪽이 집합을 바꿔도 이 검사는 만들 때의 목록으로 판정한다.
    known = frozenset(document_ids)

    def check(export: NFRExport) -> list[Finding]:
        return (
            _duplicated_ids(export)
            + _criterion_links(export)
            + _tradeoff_links(export)
            + _coverage(export)
            + _evidence(export, known)
        )

    return check


def _duplicated_ids(export: NFRExport) -> list[Finding]:
    """id가 겹치면 참조가 어느 쪽을 가리키는지 모호하다. 두 번째부터 지적한다."""
    sections = [
        ("confirmed_nfrs", [nfr.id for nfr in export.confirmed_nfrs]),
        ("tradeoffs", [tradeoff.id for tradeoff in export.tradeoffs]),
        ("rubric.criteria", [criterion.id for criterion in export.rubric.criteria]),
    ]
    findings = []
    for section, ids in sections:
        seen: set[str] = set()
        for i, item_id in enumerate(ids):
            if item_id in seen:
                findings.append(
                    _error(
                        FindingCode.ID_DUPLICATED,
                        f"{section}[{i}].id",
                        f"{section}에 id {item_id}가 이미 있다.",
                    )
                )
            seen.add(item_id)
    return findings


def _criterion_links(export: NFRExport) -> list[Finding]:
    """criterion 하나는 존재하는 NFR 정확히 하나를 평가한다."""
    nfr_ids = {nfr.id for nfr in export.confirmed_nfrs}
    findings = []
    for i, criterion in enumerate(export.rubric.criteria):
        path = f"rubric.criteria[{i}].related_nfr_ids"
        refs = criterion.related_nfr_ids
        if not refs:
            findings.append(
                _error(
                    FindingCode.CRITERION_NFR_REFERENCE_MISSING,
                    path,
                    f"{criterion.id}가 평가하는 NFR이 없다.",
                )
            )
        elif len(refs) > 1:
            findings.append(
                _error(
                    FindingCode.CRITERION_MULTI_NFR,
                    path,
                    f"{criterion.id}가 NFR {refs}를 함께 평가한다. 하나만 평가해야 한다.",
                )
            )
        findings += _unknown_nfrs(refs, nfr_ids, path)
    return findings


def _tradeoff_links(export: NFRExport) -> list[Finding]:
    nfr_ids = {nfr.id for nfr in export.confirmed_nfrs}
    findings = []
    for i, tradeoff in enumerate(export.tradeoffs):
        path = f"tradeoffs[{i}].related_nfr_ids"
        if not tradeoff.related_nfr_ids:
            findings.append(
                _error(
                    FindingCode.TRADEOFF_NFR_REFERENCE_MISSING,
                    path,
                    f"{tradeoff.id}가 어느 NFR에도 연결되지 않았다.",
                )
            )
        findings += _unknown_nfrs(tradeoff.related_nfr_ids, nfr_ids, path)
    return findings


def _unknown_nfrs(refs: list[str], nfr_ids: set[str], path: str) -> list[Finding]:
    if unknown := [ref for ref in refs if ref not in nfr_ids]:
        return [
            _error(
                FindingCode.NFR_REFERENCE_INVALID,
                path,
                f"confirmed_nfrs에 없는 NFR {unknown}를 가리킨다.",
            )
        ]
    return []


def _coverage(export: NFRExport) -> list[Finding]:
    """확정 NFR은 정확히 하나의 criterion에서 평가된다."""
    covered = Counter(
        ref
        for criterion in export.rubric.criteria
        for ref in set(criterion.related_nfr_ids)
    )
    findings = []
    for k, nfr in enumerate(export.confirmed_nfrs):
        path = f"confirmed_nfrs[{k}]"
        if covered[nfr.id] == 0:
            findings.append(
                _error(
                    FindingCode.NFR_NOT_COVERED,
                    path,
                    f"{nfr.id}를 평가하는 criterion이 없다.",
                )
            )
        elif covered[nfr.id] > 1:
            findings.append(
                _error(
                    FindingCode.NFR_MULTI_COVERED,
                    path,
                    f"{nfr.id}를 criterion {covered[nfr.id]}개가 평가한다. 하나여야 한다.",
                )
            )
    return findings


def _evidence(export: NFRExport, document_ids: AbstractSet[str]) -> list[Finding]:
    """NFR과 trade-off는 근거가 있고, 그 근거는 크롤한 문서만 가리킨다."""
    cited = [(f"confirmed_nfrs[{k}]", n) for k, n in enumerate(export.confirmed_nfrs)]
    cited += [(f"tradeoffs[{i}]", t) for i, t in enumerate(export.tradeoffs)]
    findings = []
    for where, item in cited:
        if not item.evidence_refs:
            findings.append(
                _error(
                    FindingCode.EVIDENCE_REF_MISSING,
                    f"{where}.evidence_refs",
                    f"{item.id}에 근거 문서가 없다.",
                )
            )
        elif unknown := [ref for ref in item.evidence_refs if ref not in document_ids]:
            findings.append(
                _error(
                    FindingCode.EVIDENCE_REF_UNKNOWN,
                    f"{where}.evidence_refs",
                    f"{item.id}가 크롤하지 않은 문서 {unknown}를 인용한다.",
                )
            )
    return findings


def _error(code: FindingCode, path: str, message: str) -> Finding:
    return Finding(code=code, severity=Severity.ERROR, path=path, message=message)
