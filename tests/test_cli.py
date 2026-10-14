from archgen.cli import main


def test_fake_option_opens_the_interactive_tui(monkeypatch):
    from unittest.mock import Mock

    import archgen.tui.app

    factory = Mock()
    monkeypatch.setattr(archgen.tui.app, "ArchGenApp", factory)

    assert main(["--fake"]) == 0
    factory.assert_called_once_with(fake=True)
    factory.return_value.run.assert_called_once()


def test_harnesses_command_is_available(capsys) -> None:
    assert main(["harnesses"]) == 0
    assert "No validation harnesses" in capsys.readouterr().out
