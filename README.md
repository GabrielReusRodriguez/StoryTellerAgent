# StoryTellerAgent

**Language:** English | [Castellano](docs/README.es.md) | [Català](docs/README.ca.md) | [Galego](docs/README.gl.md)

Children’s story agent built on Gaia (`amd-gaia`), designed to run with **AMD Lemonade AI** as the local LLM backend. It generates short stories in streaming, with random topics and a JSON-configurable system prompt.

## Requirements

- Python ≥ 3.12
- [uv](https://github.com/astral-sh/uv)
- [AMD Lemonade AI](https://lemonade-server.ai/) (or a compatible OpenAI-style API)
- See [Environment variables](#environment-variables) below

## Installation

```bash
cd StoryTellerAgent
uv sync --group dev
```

This creates the virtual environment, installs `amd-gaia` (≥ 0.21.2), and development dependencies (`pytest`).

## Environment variables

The agent reads configuration from the **process environment** (and optional CLI flags). It does **not** load a `.env` file.

| Variable | Required | Description |
|----------|----------|-------------|
| `LEMONADE_BASE_URL` | **Yes** | Lemonade API base URL, e.g. `http://localhost:8000/api/v1` |
| `LEMONADE_API_KEY` | No | API key when the Lemonade server requires authentication (`Authorization: Bearer …`) |

## Usage

```bash
# Activate the environment (optional)
source .venv/bin/activate

# Required: Lemonade URL
export LEMONADE_BASE_URL=http://localhost:8000/api/v1
# Optional: only if your Lemonade server requires auth
export LEMONADE_API_KEY=your-api-key

# CLI
storyteller-agent

# Or pass URL / key on the command line
storyteller-agent --base-url http://localhost:8000/api/v1 --api-key your-api-key

# As a module
python -m story_teller_agent
```

Both create a `StoryTellerAgent` with the topic generator (`TopicCreator`) and print the story to stdout in streaming. Model `<think>…</think>` blocks are filtered out.

CLI flags:

| Flag | Description |
|------|-------------|
| `--base-url` | Same as `LEMONADE_BASE_URL` (overrides env for this run) |
| `--api-key` | Same as `LEMONADE_API_KEY` (sets the env for this process only) |

### Programmatic usage

```python
from story_teller_agent import StoryTellerAgent

# Uses LEMONADE_BASE_URL / LEMONADE_API_KEY from the environment,
# or pass base_url=... / api_key=...
agent = StoryTellerAgent(topic_creator=True)
for chunk in agent.tell_stream():
    print(chunk, end="", flush=True)
```

Useful constructor parameters:

| Parameter | Description |
|-----------|-------------|
| `base_url` | Lemonade API URL (**required** unless `LEMONADE_BASE_URL` is set) |
| `api_key` | Lemonade API key (**optional**; injects `LEMONADE_API_KEY` for Gaia for this process) |
| `model` | Model name (default `Gemma-4-12B-it-GGUF`) |
| `system_prompt` | Full prompt (skips the config JSON) |
| `prompt_params_path` | Path to a prompt-parameter JSON file |
| `topic_creator` | If `True`, generates random topics |
| `imagination` | Model temperature (default `1.0`) |
| `max_tokens` | Token limit (default `4096`) |

If neither `system_prompt` nor `prompt_params_path` is set, the agent loads `config/prompt_params.json` via `PromptBuilder.from_file(...).build()`.

## Configuration

The `config/` folder is resolved automatically in development (repo root) or when packaged (`story_teller_agent/config`), via `helpers/paths.py`.

### `prompt_params.json`

Defines the system prompt through `PromptBuilder`:

| Field | Description |
|-------|-------------|
| `min_age` / `max_age` | Audience age range |
| `language` | Story language |
| `personalization` | Extra instructions inserted into the personalization section of the prompt |

Example:

```json
{
  "min_age": 5,
  "max_age": 10,
  "language": "Castellano",
  "personalization": "Incluye animales del bosque"
}
```

### Topic lists

`TopicCreator` randomly combines one line from each file:

| File | Role |
|------|------|
| `subjects.txt` | Story subject |
| `actions.txt` | Action |
| `objects.txt` | Object |
| `object_properties.txt` | Object property |
| `subject_objectives.txt` | Subject goal |

## Structure

```text
config/                         # Parameters and topic lists
examples/                       # Sample stories
docs/                           # Documentation (ES, CA, GL)
src/story_teller_agent/
  cli.py                        # CLI entry point (--base-url, --api-key)
  __main__.py                   # python -m story_teller_agent
  story_teller.py               # Agent (Gaia SDK)
  helpers/
    prompt_builder.py           # System prompt from JSON
    topic_creator.py            # Random topics
    paths.py                    # config/ resolution
tests/                          # pytest
gaia-agent.yaml                 # Gaia agent metadata
LICENSE                         # GPL-3.0
```

## Tests

```bash
uv sync --group dev
.venv/bin/pytest -q
```

## Gaia

The package is declared as a Gaia agent in `gaia-agent.yaml`:

- **Module:** `story_teller_agent.story_teller`
- **Class:** `StoryTellerAgent`
- **Minimum Gaia:** `0.21.2`

When Gaia constructs `StoryTellerAgent()` without arguments, set `LEMONADE_BASE_URL` (and `LEMONADE_API_KEY` if needed) in the environment before launching Gaia. `AgentConfig` does not expose an `api_key` field; Gaia’s Lemonade client reads `LEMONADE_API_KEY` from the environment.

## Examples

Sample stories generated by the agent (see [`examples/`](examples/)). The texts below are **English translations**; the [originals](examples/) were written in **Castilian Spanish (Castellano)**.

### [Little Dragon Maths and the Magical Mistake](examples/EL_Pequeño_Dragon_matematicas_y_el_error_magico.md)

Once upon a time there was a very special little dragon named Maths. Although he was a dragon who could shoot sparkling flames, he was so tiny that he fit perfectly inside a teacup! His most important mission in the Kingdom of Numbers was to make sure every sum and subtraction was in the right place, so nothing in the magical world fell into disorder.

One day, something very strange happened: there was a huge mistake on Calculation Mountain! The numbers had jumped from one place to another as if they were playing hide-and-seek. The number 3 was where the 8 should have been, and the apples at the market were being counted twice by mistake. It was a complete mess.

Maths knew he had to act fast. He put on his little explorer’s backpack and flew off with great courage. At first, moving the big digits was hard work because they were heavy, but he did not give up for a second. “With effort and patience, anything can be fixed!” he would say as he flew here and there.

He carefully put each digit back in place, using his little wings to balance the numbers and his kind heart to help everyone in the kingdom. After working all afternoon, everything was where it belonged again! The sums were perfect once more, and children could count their toys without getting confused.

Little dragon Maths went home very tired but very happy. He had shown that no matter how small you are, if you try hard and help others, you can achieve wonderful things.

### [The Gift of Snow and Heart](examples/El%20Regalo%20de%20nieve%20y%20corazon.md)

Once upon a time there was a very special mum who lived in a castle made of colourful flowers. She had a heart full of love and always wanted to see her family smile with the greatest joy. One day, she saw that her little son was a bit sad because he wished for a giant friend to play with in the garden on winter nights.

Mum decided to use her secret magic to help him. She went to the coolest corner of her magical courtyard and planted a shining seed that gleamed like a diamond under the moon. For several days she watered the plant with dew and whispered sweet words to it, giving it strength and affection.

Suddenly, something wonderful happened! From the earth sprang a tall, large figure made entirely of sparkling snowflakes and magical frost. It was an “Ice Dad”, soft and fluffy like a cold cloud. Although he felt cold to the touch on the outside, his smile was the warmest in the world!

This new friend brought little ice dolls that danced on their own and gave away snowflakes that tasted of strawberry when they fell into the child’s mouth. The little boy jumped with happiness, hugging his new companion made of crystal and snow. Mum had managed to create someone special using only her imagination and a great deal of love to fill the house with joy.

From that day on, “Ice Dad” watched over the child’s dreams every night, reminding everyone that when there is kindness in the heart, even the cold can turn into a sweet and wonderful hug.

## License

[GPL-3.0](LICENSE)
