from archgen.cli import main


def test_harnesses_command_is_available(capsys) -> None:
    assert main(["harnesses"]) == 0
    assert "No validation harnesses" in capsys.readouterr().out
