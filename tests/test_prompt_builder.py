from pathlib import Path

import pytest

from story_teller_agent.helpers.prompt_builder import PromptBuilder, PromptParams


class TestPromptParams:
    def test_defaults(self) -> None:
        params = PromptParams()
        assert params.min_age == 5
        assert params.max_age == 10
        assert params.language == "Castellano"
        assert params.personalization == ""

    def test_frozen(self) -> None:
        params = PromptParams()
        with pytest.raises(AttributeError):
            params.min_age = 8  # type: ignore[misc]


class TestPromptBuilder:
    def test_build_includes_age_and_language(self) -> None:
        prompt = PromptBuilder(
            PromptParams(min_age=6, max_age=9, language="English")
        ).build()
        assert "6" in prompt
        assert "9" in prompt
        assert "English" in prompt
        assert "cuentos infantiles" in prompt

    def test_build_includes_personalization(self) -> None:
        prompt = PromptBuilder(
            PromptParams(personalization="Incluye dinosaurios")
        ).build()
        assert "Incluye dinosaurios" in prompt

    def test_from_file_loads_overrides(self, tmp_path: Path) -> None:
        path = tmp_path / "params.json"
        path.write_text(
            '{"min_age": 3, "max_age": 7, "language": "Català", "personalization": "x"}',
            encoding="utf-8",
        )
        builder = PromptBuilder.from_file(path)
        assert builder.params.min_age == 3
        assert builder.params.max_age == 7
        assert builder.params.language == "Català"
        assert builder.params.personalization == "x"

    def test_from_file_ignores_unknown_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "params.json"
        path.write_text('{"min_age": 4, "extra": "ignored"}', encoding="utf-8")
        builder = PromptBuilder.from_file(path)
        assert builder.params.min_age == 4
        assert builder.params.max_age == 10  # default

    def test_from_file_partial_uses_defaults(self, tmp_path: Path) -> None:
        path = tmp_path / "params.json"
        path.write_text("{}", encoding="utf-8")
        builder = PromptBuilder.from_file(path)
        assert builder.params == PromptParams()

    def test_from_file_rejects_non_object(self, tmp_path: Path) -> None:
        path = tmp_path / "params.json"
        path.write_text("[1, 2]", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON object"):
            PromptBuilder.from_file(path)

    def test_from_file_with_repo_config(self) -> None:
        from story_teller_agent.helpers.paths import CONFIG_DIR

        builder = PromptBuilder.from_file(CONFIG_DIR / "prompt_params.json")
        assert builder.params.min_age == 5
        assert builder.params.max_age == 10
        assert builder.params.language == "Castellano"
