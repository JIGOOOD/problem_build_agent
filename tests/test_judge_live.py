"""실제 large Judge의 골든 루브릭 오탐 검증. 명시적으로 실행한다."""

import json
import os

import pytest

from try_judge import run


@pytest.mark.slow
@pytest.mark.skipif(
    os.getenv("ARCHGEN_LIVE_TEST") != "1", reason="실제 API 검증은 명시적으로 실행한다"
)
def test_live_judge_reports_no_findings_for_golden_rubric(tmp_path):
    run_dir = run(log_root=tmp_path)

    assert json.loads((run_dir / "findings.json").read_text()) == []
    assert json.loads((run_dir / "status.json").read_text())["passed"] is True
