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

## License

[GPL-3.0](LICENSE)
