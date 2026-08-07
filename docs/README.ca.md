# StoryTellerAgent

**Idioma:** [English](../README.md) | [Castellano](README.es.md) | Català | [Galego](README.gl.md)

Agent de contes infantils basat en Gaia (`amd-gaia`), creat per fer-se servir amb **AMD Lemonade AI** com a backend LLM local. Genera històries curtes en streaming, amb temes aleatoris i un system prompt configurable per JSON.

## Requisits

- Python ≥ 3.12
- [uv](https://github.com/astral-sh/uv)
- [AMD Lemonade AI](https://lemonade-server.ai/) (o una API compatible estil OpenAI)
- Vegeu [Variables d'entorn](#variables-dentorn) més avall

## Instal·lació

```bash
cd StoryTellerAgent
uv sync --group dev
```

Això crea l'entorn virtual, instal·la `amd-gaia` (≥ 0.21.2) i les dependències de desenvolupament (`pytest`).

## Variables d'entorn

L'agent llegeix la configuració de l'**entorn del procés** (i flags opcionals del CLI). **No** carrega un fitxer `.env`.

| Variable | Obligatòria | Descripció |
|----------|-------------|------------|
| `LEMONADE_BASE_URL` | **Sí** | URL base de l'API de Lemonade, p. ex. `http://localhost:8000/api/v1` |
| `LEMONADE_API_KEY` | No | API key si el servidor Lemonade requereix autenticació (`Authorization: Bearer …`) |

## Ús

```bash
# Activar l'entorn (opcional)
source .venv/bin/activate

# Obligatori: URL de Lemonade
export LEMONADE_BASE_URL=http://localhost:8000/api/v1
# Opcional: només si el servidor Lemonade exigeix auth
export LEMONADE_API_KEY=la-teva-api-key

# CLI
storyteller-agent

# O passar URL / key a la línia d'ordres
storyteller-agent --base-url http://localhost:8000/api/v1 --api-key la-teva-api-key

# Com a mòdul
python -m story_teller_agent
```

Tots dos creen un `StoryTellerAgent` amb generador de temes (`TopicCreator`) i escriuen el conte per stdout en streaming. Els blocs `<think>…</think>` del model es filtren.

Flags del CLI:

| Flag | Descripció |
|------|------------|
| `--base-url` | Equivalent a `LEMONADE_BASE_URL` (té prioritat sobre l'env en aquesta execució) |
| `--api-key` | Equivalent a `LEMONADE_API_KEY` (només afecta aquest procés) |

### Ús programàtic

```python
from story_teller_agent import StoryTellerAgent

# Usa LEMONADE_BASE_URL / LEMONADE_API_KEY de l'entorn,
# o passa base_url=... / api_key=...
agent = StoryTellerAgent(topic_creator=True)
for chunk in agent.tell_stream():
    print(chunk, end="", flush=True)
```

Paràmetres útils del constructor:

| Paràmetre | Descripció |
|-----------|------------|
| `base_url` | URL de l'API de Lemonade (**obligatòria** si no hi ha `LEMONADE_BASE_URL`) |
| `api_key` | API key de Lemonade (**opcional**; injecta `LEMONADE_API_KEY` per a Gaia en aquest procés) |
| `model` | Nom del model (per defecte `Gemma-4-12B-it-GGUF`) |
| `system_prompt` | Prompt complet (omet el JSON de config) |
| `prompt_params_path` | Ruta a un JSON de paràmetres del prompt |
| `topic_creator` | Si és `True`, genera temes aleatoris |
| `imagination` | Temperatura del model (per defecte `1.0`) |
| `max_tokens` | Límit de tokens (per defecte `4096`) |

Si no s'indica `system_prompt` ni `prompt_params_path`, l'agent carrega `config/prompt_params.json` amb `PromptBuilder.from_file(...).build()`.

## Configuració

La carpeta `config/` es resol automàticament en desenvolupament (arrel del repo) o empaquetada (`story_teller_agent/config`), mitjançant `helpers/paths.py`.

### `prompt_params.json`

Defineix el system prompt via `PromptBuilder`:

| Camp | Descripció |
|------|------------|
| `min_age` / `max_age` | Franja d'edat del públic |
| `language` | Idioma del conte |
| `personalization` | Instruccions extra inserides a la secció de personalització del prompt |

Exemple:

```json
{
  "min_age": 5,
  "max_age": 10,
  "language": "Castellano",
  "personalization": "Incluye animales del bosque"
}
```

### Llistes de temes

`TopicCreator` combina a l'atzar una línia de cada fitxer:

| Fitxer | Rol |
|--------|-----|
| `subjects.txt` | Subjecte del conte |
| `actions.txt` | Acció |
| `objects.txt` | Objecte |
| `object_properties.txt` | Propietat de l'objecte |
| `subject_objectives.txt` | Objectiu del subjecte |

## Estructura

```text
config/                         # Paràmetres i llistes de temes
examples/                       # Exemples de contes
docs/                           # Documentació (ES, CA, GL)
src/story_teller_agent/
  cli.py                        # Entry point CLI (--base-url, --api-key)
  __main__.py                   # python -m story_teller_agent
  story_teller.py               # Agent (Gaia SDK)
  helpers/
    prompt_builder.py           # System prompt des de JSON
    topic_creator.py            # Temes aleatoris
    paths.py                    # Resolució de config/
tests/                          # pytest
gaia-agent.yaml                 # Metadades de l'agent Gaia
LICENSE                         # GPL-3.0
```

## Tests

```bash
uv sync --group dev
.venv/bin/pytest -q
```

## Gaia

El paquet es declara com a agent Gaia a `gaia-agent.yaml`:

- **Mòdul:** `story_teller_agent.story_teller`
- **Classe:** `StoryTellerAgent`
- **Gaia mínima:** `0.21.2`

Si Gaia instancia `StoryTellerAgent()` sense arguments, defineix `LEMONADE_BASE_URL` (i `LEMONADE_API_KEY` si cal) a l'entorn abans de llançar Gaia. `AgentConfig` no exposa `api_key`; el client Lemonade de Gaia llegeix `LEMONADE_API_KEY` de l'entorn.

## Llicència

[GPL-3.0](../LICENSE)
