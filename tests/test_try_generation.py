from unittest.mock import Mock

import pytest

import try_generation as manual
from archgen.domain.brief import Seniority


@pytest.mark.parametrize("status,exit_code", [("complete", 0), ("failed", 1)])
def test_manual_entrypoint_passes_brief_and_reports_output(
    monkeypatch, capsys, status, exit_code
):
    run = Mock(return_value={"status": status, "output_dir": "/tmp/run"})
    monkeypatch.setattr(manual, "run_generation", run)

    assert manual.main(["채팅", "--seniority", "Senior"]) == exit_code

    brief = run.call_args.args[0]
    assert brief.topic == "채팅"
    assert brief.seniority is Seniority.SENIOR
    assert "notes" not in vars(brief)
    assert "/tmp/run" in capsys.readouterr().out


def test_manual_entrypoint_reports_error_and_returns_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(
        manual, "run_generation", Mock(side_effect=TimeoutError("LLM timeout"))
    )

    assert manual.main([]) == 1

    assert "LLM timeout" in capsys.readouterr().err
