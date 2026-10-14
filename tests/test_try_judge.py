import json
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage

import try_judge as manual


@pytest.mark.parametrize(
    "content,passed",
    [
        ('{"findings": []}', True),
        (
            '{"findings": [{"code": "LEVEL_AMBIGUOUS", "severity": "ERROR", "path": "rubric.criteria.0", "message": "모호함"}]}',
            False,
        ),
        ("bad json", False),
    ],
)
def test_golden_judge_saves_input_response_and_findings(
    tmp_path, monkeypatch, golden_export, content, passed
):
    model = Mock()
    model.bind.return_value = model
    model.invoke.return_value = AIMessage(content=[{"type": "text", "text": content}])
    factory = Mock(return_value=model)
    monkeypatch.setattr(manual, "build_chat_model", factory)

    if passed:
        root = manual.run(log_root=tmp_path)
    else:
        with pytest.raises(RuntimeError, match="Finding"):
            manual.run(log_root=tmp_path)
        root = next(tmp_path.iterdir())

    assert factory.call_args.args == ("large",)
    spec = model.bind.call_args.kwargs["response_format"]
    assert spec["type"] == "json_schema"
    assert spec["json_schema"]["name"] == "JudgeResponse"
    assert spec["json_schema"]["strict"] is True
    payload = json.loads(model.invoke.call_args.args[0][1]["content"])
    assert payload["export"] == golden_export.model_dump(mode="json")
    assert payload["research"]["documents"]
    assert "quotes" not in payload["research"]["documents"][0]
    assert (root / "llm-input.json").exists()
    assert (root / "llm-response.json").exists()
    assert (root / "findings.json").exists()
    assert (root / "run.log").exists()
    assert json.loads((root / "status.json").read_text())["passed"] is passed
