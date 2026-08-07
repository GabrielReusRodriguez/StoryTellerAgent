from unittest.mock import MagicMock, patch

from story_teller_agent import cli


def test_main_prints_stream(capsys) -> None:
    agent = MagicMock()
    agent.tell_stream.return_value = iter(["Érase ", "una vez"])

    with patch("story_teller_agent.cli.StoryTellerAgent", return_value=agent) as ctor:
        cli.main([])

    ctor.assert_called_once_with(
        topic_creator=True, base_url=None, api_key=None
    )
    agent.tell_stream.assert_called_once_with()
    out = capsys.readouterr().out
    assert "Érase una vez" in out
    assert out.startswith("...\n")
    assert out.rstrip().endswith("...")


def test_main_passes_base_url(capsys) -> None:
    agent = MagicMock()
    agent.tell_stream.return_value = iter(["ok"])

    with patch("story_teller_agent.cli.StoryTellerAgent", return_value=agent) as ctor:
        cli.main(["--base-url", "http://localhost:8000/api/v1"])

    ctor.assert_called_once_with(
        topic_creator=True,
        base_url="http://localhost:8000/api/v1",
        api_key=None,
    )
    assert "ok" in capsys.readouterr().out


def test_main_passes_api_key(capsys) -> None:
    agent = MagicMock()
    agent.tell_stream.return_value = iter(["ok"])

    with patch("story_teller_agent.cli.StoryTellerAgent", return_value=agent) as ctor:
        cli.main(["--api-key", "secret-token"])

    ctor.assert_called_once_with(
        topic_creator=True, base_url=None, api_key="secret-token"
    )
    assert "ok" in capsys.readouterr().out
