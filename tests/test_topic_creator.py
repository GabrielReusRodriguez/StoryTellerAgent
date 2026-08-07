import random
from pathlib import Path

import pytest

from story_teller_agent.helpers.paths import CONFIG_DIR
from story_teller_agent.helpers.topic_creator import TopicCreator


class TestTopicCreatorLoadLines:
    def test_load_lines_strips_and_skips_blank(self, tmp_path: Path) -> None:
        path = tmp_path / "items.txt"
        path.write_text("  uno  \n\n\ndos\n  \n tres \n", encoding="utf-8")
        assert TopicCreator._load_lines(path) == ["uno", "dos", "tres"]

    def test_loads_config_lists(self) -> None:
        creator = TopicCreator()
        assert creator.subjects
        assert creator.actions
        assert creator.objects
        assert creator.object_properties
        assert creator.subject_objectives
        assert all(isinstance(s, str) for s in creator.subjects)


class TestTopicCreatorCreateTopic:
    def test_topic_contains_chosen_parts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        creator = TopicCreator()
        monkeypatch.setattr(
            creator,
            "subjects",
            ["un gato"],
        )
        monkeypatch.setattr(creator, "actions", ["encuentra"])
        monkeypatch.setattr(creator, "objects", ["un tesoro"])
        monkeypatch.setattr(creator, "object_properties", ["brillante"])
        monkeypatch.setattr(creator, "subject_objectives", ["ayudar a un amigo"])

        topic = creator.create_topic()
        assert topic == (
            " Crea un cuento corto sobre un gato encuentra un tesoro "
            "brillante para ayudar a un amigo"
        )

    def test_topic_uses_values_from_lists(self) -> None:
        creator = TopicCreator()
        random.seed(0)
        topic = creator.create_topic()
        assert topic.startswith(" Crea un cuento corto sobre ")
        assert " para " in topic
        # Each segment must come from the loaded lists
        assert any(s in topic for s in creator.subjects)
        assert any(a in topic for a in creator.actions)
        assert any(o in topic for o in creator.objects)

    def test_config_files_exist(self) -> None:
        for name in (
            "subjects.txt",
            "actions.txt",
            "objects.txt",
            "object_properties.txt",
            "subject_objectives.txt",
        ):
            assert (CONFIG_DIR / name).is_file(), f"missing {name}"
