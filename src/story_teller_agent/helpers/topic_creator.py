import random
from pathlib import Path

from story_teller_agent.helpers.paths import CONFIG_DIR


class TopicCreator:
    def __init__(self) -> None:
        self.subjects = self._load_lines(CONFIG_DIR / "subjects.txt")
        self.actions = self._load_lines(CONFIG_DIR / "actions.txt")
        self.objects = self._load_lines(CONFIG_DIR / "objects.txt")
        self.object_properties = self._load_lines(CONFIG_DIR / "object_properties.txt")
        self.subject_objectives = self._load_lines(CONFIG_DIR / "subject_objectives.txt")

    @staticmethod
    def _load_lines(path: Path) -> list[str]:
        with path.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def create_topic(self) -> str:
        """Create a topic for the story."""
        subject = random.choice(self.subjects)
        action = random.choice(self.actions)
        obj = random.choice(self.objects)
        object_property = random.choice(self.object_properties)
        subject_objective = random.choice(self.subject_objectives)
        return (
            f" Crea un cuento corto sobre {subject} {action} {obj} "
            f"{object_property} para {subject_objective}"
        )
