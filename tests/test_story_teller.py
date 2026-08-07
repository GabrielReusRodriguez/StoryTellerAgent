from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import os

import pytest

from story_teller_agent.story_teller import (
    DEFAULT_TOPIC,
    LEMONADE_API_KEY_ENV,
    LEMONADE_BASE_URL_ENV,
    StoryTellerAgent,
    apply_api_key,
    resolve_base_url,
)

TEST_BASE_URL = "http://example.test/api/v1"


def _chunk(text: str, *, is_complete: bool = False) -> SimpleNamespace:
    return SimpleNamespace(text=text, is_complete=is_complete)


@pytest.fixture
def mock_sdk() -> MagicMock:
    return MagicMock()


@pytest.fixture(autouse=True)
def clear_lemonade_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(LEMONADE_BASE_URL_ENV, raising=False)
    monkeypatch.delenv(LEMONADE_API_KEY_ENV, raising=False)


class TestResolveBaseUrl:
    def test_uses_explicit_argument(self) -> None:
        assert resolve_base_url(TEST_BASE_URL) == TEST_BASE_URL

    def test_uses_environment_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(LEMONADE_BASE_URL_ENV, "http://localhost:8000/api/v1")
        assert resolve_base_url() == "http://localhost:8000/api/v1"

    def test_argument_overrides_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LEMONADE_BASE_URL_ENV, "http://from-env/api/v1")
        assert resolve_base_url("http://from-arg/api/v1") == "http://from-arg/api/v1"

    def test_missing_raises(self) -> None:
        with pytest.raises(ValueError, match="LEMONADE_BASE_URL"):
            resolve_base_url()

    def test_blank_env_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(LEMONADE_BASE_URL_ENV, "   ")
        with pytest.raises(ValueError, match="LEMONADE_BASE_URL"):
            resolve_base_url()


class TestApplyApiKey:
    def test_sets_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        apply_api_key("  secret-key  ")
        assert os.environ[LEMONADE_API_KEY_ENV] == "secret-key"

    def test_none_leaves_env_unchanged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(LEMONADE_API_KEY_ENV, "existing")
        apply_api_key(None)
        assert os.environ[LEMONADE_API_KEY_ENV] == "existing"

    def test_blank_ignored(self, monkeypatch: pytest.MonkeyPatch) -> None:
        apply_api_key("   ")
        assert LEMONADE_API_KEY_ENV not in os.environ


class TestStoryTellerAgentInit:
    def test_uses_explicit_system_prompt(self, mock_sdk: MagicMock) -> None:
        with (
            patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk) as sdk_cls,
            patch("story_teller_agent.story_teller.AgentConfig") as config_cls,
        ):
            StoryTellerAgent(system_prompt="custom prompt", base_url=TEST_BASE_URL)
            config_cls.assert_called_once()
            assert config_cls.call_args.kwargs["system_prompt"] == "custom prompt"
            assert config_cls.call_args.kwargs["base_url"] == TEST_BASE_URL
            sdk_cls.assert_called_once()

    def test_loads_prompt_from_params_path(
        self, tmp_path: Path, mock_sdk: MagicMock
    ) -> None:
        params = tmp_path / "params.json"
        params.write_text(
            '{"min_age": 4, "max_age": 8, "language": "English"}',
            encoding="utf-8",
        )
        with (
            patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk),
            patch("story_teller_agent.story_teller.AgentConfig") as config_cls,
        ):
            StoryTellerAgent(prompt_params_path=params, base_url=TEST_BASE_URL)
            prompt = config_cls.call_args.kwargs["system_prompt"]
            assert "4" in prompt
            assert "8" in prompt
            assert "English" in prompt

    def test_topic_creator_enabled(self, mock_sdk: MagicMock) -> None:
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(
                topic_creator=True, system_prompt="x", base_url=TEST_BASE_URL
            )
            assert agent.topic_creator is not None

    def test_topic_creator_disabled(self, mock_sdk: MagicMock) -> None:
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(
                topic_creator=False, system_prompt="x", base_url=TEST_BASE_URL
            )
            assert agent.topic_creator is None

    def test_requires_base_url(self, mock_sdk: MagicMock) -> None:
        with (
            patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk),
            pytest.raises(ValueError, match="LEMONADE_BASE_URL"),
        ):
            StoryTellerAgent(system_prompt="x")

    def test_reads_lemonade_env(
        self, mock_sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LEMONADE_BASE_URL_ENV, TEST_BASE_URL)
        with (
            patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk),
            patch("story_teller_agent.story_teller.AgentConfig") as config_cls,
        ):
            StoryTellerAgent(system_prompt="x")
            assert config_cls.call_args.kwargs["base_url"] == TEST_BASE_URL

    def test_api_key_sets_env(
        self, mock_sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            StoryTellerAgent(
                system_prompt="x",
                base_url=TEST_BASE_URL,
                api_key="my-secret",
            )
        assert os.environ[LEMONADE_API_KEY_ENV] == "my-secret"

    def test_api_key_optional(self, mock_sdk: MagicMock) -> None:
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            StoryTellerAgent(system_prompt="x", base_url=TEST_BASE_URL)
        assert LEMONADE_API_KEY_ENV not in os.environ


class TestStoryTellerCreateTopic:
    def test_default_topic_without_creator(self, mock_sdk: MagicMock) -> None:
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(system_prompt="x", base_url=TEST_BASE_URL)
            assert agent.create_topic() == DEFAULT_TOPIC

    def test_uses_topic_creator(self, mock_sdk: MagicMock) -> None:
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(
                topic_creator=True, system_prompt="x", base_url=TEST_BASE_URL
            )
            agent.topic_creator = MagicMock()
            agent.topic_creator.create_topic.return_value = "tema generado"
            assert agent.create_topic() == "tema generado"


class TestStoryTellerTellStream:
    def test_filters_thinking_blocks(self, mock_sdk: MagicMock) -> None:
        mock_sdk.send_stream.return_value = iter(
            [
                _chunk("Hola "),
                _chunk("<think>"),
                _chunk("pensando"),
                _chunk("</think>"),
                _chunk("mundo"),
                _chunk("", is_complete=True),
            ]
        )
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(system_prompt="x", base_url=TEST_BASE_URL)
            assert "".join(agent.tell_stream("tema")) == "Hola mundo"
            mock_sdk.send_stream.assert_called_once_with("tema")

    def test_uses_create_topic_when_topic_missing(self, mock_sdk: MagicMock) -> None:
        mock_sdk.send_stream.return_value = iter([_chunk("ok")])
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(system_prompt="x", base_url=TEST_BASE_URL)
            list(agent.tell_stream())
            mock_sdk.send_stream.assert_called_once_with(DEFAULT_TOPIC)

    def test_skips_complete_chunks(self, mock_sdk: MagicMock) -> None:
        mock_sdk.send_stream.return_value = iter(
            [
                _chunk("visible"),
                _chunk("ignored-complete", is_complete=True),
            ]
        )
        with patch("story_teller_agent.story_teller.AgentSDK", return_value=mock_sdk):
            agent = StoryTellerAgent(system_prompt="x", base_url=TEST_BASE_URL)
            assert list(agent.tell_stream("t")) == ["visible"]
