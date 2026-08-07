from pathlib import Path


def get_config_dir() -> Path:
    """Repo config/ in development; story_teller_agent/config when packaged."""
    package_root = Path(__file__).resolve().parents[1]
    repo_config = package_root.parents[1] / "config"
    if repo_config.is_dir():
        return repo_config
    packaged = package_root / "config"
    if packaged.is_dir():
        return packaged
    raise FileNotFoundError(
        f"Config directory not found (tried {repo_config} and {packaged})"
    )


CONFIG_DIR = get_config_dir()
