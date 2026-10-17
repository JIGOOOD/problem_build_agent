"""API 복구 및 M5·M6 실제 검증 후 명시적으로 실행하는 전체 스모크."""

import os
from pathlib import Path

import pytest

from archgen.core.service import run_generation
from archgen.domain.brief import InterviewBrief, Seniority


@pytest.mark.slow
@pytest.mark.skipif(
    os.getenv("ARCHGEN_LIVE_TEST") != "1", reason="실제 API 검증은 명시적으로 실행한다"
)
def test_live_generation_with_search_fetch_and_large_judge(tmp_path):
    result = run_generation(
        InterviewBrief(Seniority.MIDDLE, "실시간 채팅 서비스"),
        output_root=tmp_path,
        judge_enabled=True,
    )

    assert result["status"] == "complete", result["findings"]
    assert result["research"].documents
    assert len(result["export"].confirmed_nfrs) >= 2
    assert (Path(result["output_dir"]) / "nfr_rubric.md").is_file()
    assert not any(f.severity == "ERROR" for f in result["findings"])
    assert "judge: disabled" not in "\n".join(result["events"])
