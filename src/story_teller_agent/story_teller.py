import os
from pathlib import Path
from typing import Iterator, Optional

from gaia.chat.sdk import AgentConfig, AgentSDK

from story_teller_agent.helpers.prompt_builder import PromptBuilder
from story_teller_agent.helpers.topic_creator import TopicCreator
from story_teller_agent.helpers.paths import CONFIG_DIR

LEMONADE_BASE_URL_ENV = "LEMONADE_BASE_URL"
LEMONADE_API_KEY_ENV = "LEMONADE_API_KEY"
DEFAULT_MODEL = "Gemma-4-12B-it-GGUF"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_IMAGINATION = 1.0

DEFAULT_TOPIC = """Sorprendeme con un cuento corto"""


def resolve_base_url(base_url: Optional[str] = None) -> str:
    """Resolve Lemonade URL from argument or LEMONADE_BASE_URL env var."""
    resolved = (base_url or os.environ.get(LEMONADE_BASE_URL_ENV) or "").strip()
    if not resolved:
        raise ValueError(
            "Lemonade base URL is required. Pass base_url=... or set "
            f"{LEMONADE_BASE_URL_ENV} (e.g. http://localhost:8000/api/v1)."
        )
    return resolved


def apply_api_key(api_key: Optional[str] = None) -> None:
    """Inject API key into LEMONADE_API_KEY so Gaia/LemonadeClient can use it.

    AgentConfig does not expose api_key; Gaia reads LEMONADE_API_KEY from the env.
    Empty or whitespace-only values are ignored.
    """
    if api_key is None:
        return
    stripped = api_key.strip()
    if stripped:
        os.environ[LEMONADE_API_KEY_ENV] = stripped


class StoryTellerAgent:
    """Agent that streams children's stories without thinking blocks."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        system_prompt: Optional[str] = None,
        prompt_params_path: Optional[str | Path] = None,
        topic_creator: Optional[bool] = False,
        imagination: Optional[float] = DEFAULT_IMAGINATION,
    ) -> None:
        resolved_base_url = resolve_base_url(base_url)
        apply_api_key(api_key)

        if system_prompt is not None:
            resolved_prompt = system_prompt
        elif prompt_params_path is not None:
            resolved_prompt = PromptBuilder.from_file(prompt_params_path).build()
        else:
            default_params = CONFIG_DIR / "prompt_params.json"
            if default_params.is_file():
                resolved_prompt = PromptBuilder.from_file(default_params).build()
            else:
                resolved_prompt = PromptBuilder().build()

        config = AgentConfig(
            base_url=resolved_base_url,
            system_prompt=resolved_prompt,
            model=model,
            show_stats=False,
            max_tokens=max_tokens,
            temperature=imagination,
        )
        self._chat = AgentSDK(config)
        if topic_creator:
            self.topic_creator = TopicCreator()
        else:
            self.topic_creator = None

    def create_topic(self) -> str:
        """Create a topic for the story."""
        if self.topic_creator is not None:
            return self.topic_creator.create_topic()
        return DEFAULT_TOPIC

    def tell_stream(self, topic: Optional[str] = None) -> Iterator[str]:
        """Stream visible story text: yield each chunk immediately, without buffering."""
        if topic is None:
            topic = self.create_topic()
        thinking = False
        for chunk in self._chat.send_stream(topic):
            if chunk.is_complete:
                continue
            text = chunk.text
            if text == "<think>":
                thinking = True
                continue
            if text == "</think>":
                thinking = False
                continue
            if not thinking:
                yield text
