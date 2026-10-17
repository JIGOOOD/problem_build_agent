"""등록된 검사를 순서대로 돌려 Finding을 모은다."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from archgen.domain.nfr import NFRExport
from archgen.harness.findings import Finding

Check = Callable[[NFRExport], list[Finding]]


class Runner:
    """검사 하나가 지적을 내도 나머지 검사는 계속 돈다."""

    def __init__(self, checks: Sequence[Check]) -> None:
        self._checks = tuple(checks)

    def run(self, export: NFRExport) -> list[Finding]:
        return [finding for check in self._checks for finding in check(export)]
