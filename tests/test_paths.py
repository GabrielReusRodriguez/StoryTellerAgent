from story_teller_agent.helpers import paths


class TestGetConfigDir:
    def test_returns_repo_config_in_development(self) -> None:
        config_dir = paths.get_config_dir()
        assert config_dir.is_dir()
        assert config_dir.name == "config"
        assert (config_dir / "prompt_params.json").is_file()

    def test_config_dir_constant_matches(self) -> None:
        assert paths.CONFIG_DIR == paths.get_config_dir()
