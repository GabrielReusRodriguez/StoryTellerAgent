# StoryTellerAgent

**Idioma:** [English](../README.md) | [Castellano](README.es.md) | [Català](README.ca.md) | Galego

Axente de contos infantís baseado en Gaia (`amd-gaia`), creado para usarse con **AMD Lemonade AI** como backend LLM local. Xera historias curtas en streaming, con temas aleatorios e un system prompt configurable por JSON.

## Requisitos

- Python ≥ 3.12
- [uv](https://github.com/astral-sh/uv)
- [AMD Lemonade AI](https://lemonade-server.ai/) (ou unha API compatible estilo OpenAI)
- Ver [Variables de contorno](#variables-de-contorno) máis abaixo

## Instalación

```bash
cd StoryTellerAgent
uv sync --group dev
```

Isto crea o contorno virtual, instala `amd-gaia` (≥ 0.21.2) e as dependencias de desenvolvemento (`pytest`).

## Variables de contorno

O axente le a configuración do **contorno do proceso** (e flags opcionais do CLI). **Non** carga un ficheiro `.env`.

| Variable | Obrigatoria | Descrición |
|----------|-------------|------------|
| `LEMONADE_BASE_URL` | **Si** | URL base da API de Lemonade, p. ex. `http://localhost:8000/api/v1` |
| `LEMONADE_API_KEY` | Non | API key se o servidor Lemonade require autenticación (`Authorization: Bearer …`) |

## Uso

```bash
# Activar o contorno (opcional)
source .venv/bin/activate

# Obrigatorio: URL de Lemonade
export LEMONADE_BASE_URL=http://localhost:8000/api/v1
# Opcional: só se o servidor Lemonade esixe auth
export LEMONADE_API_KEY=a-tua-api-key

# CLI
storyteller-agent

# Ou pasar URL / key na liña de comandos
storyteller-agent --base-url http://localhost:8000/api/v1 --api-key a-tua-api-key

# Como módulo
python -m story_teller_agent
```

Ambos crean un `StoryTellerAgent` con xerador de temas (`TopicCreator`) e escriben o conto por stdout en streaming. Os bloques `<think>…</think>` do modelo fíltranse.

Flags do CLI:

| Flag | Descrición |
|------|------------|
| `--base-url` | Equivale a `LEMONADE_BASE_URL` (ten prioridade sobre a env nesta execución) |
| `--api-key` | Equivale a `LEMONADE_API_KEY` (só afecta a este proceso) |

### Uso programático

```python
from story_teller_agent import StoryTellerAgent

# Usa LEMONADE_BASE_URL / LEMONADE_API_KEY do contorno,
# ou pasa base_url=... / api_key=...
agent = StoryTellerAgent(topic_creator=True)
for chunk in agent.tell_stream():
    print(chunk, end="", flush=True)
```

Parámetros útiles do construtor:

| Parámetro | Descrición |
|-----------|------------|
| `base_url` | URL da API de Lemonade (**obrigatoria** se non hai `LEMONADE_BASE_URL`) |
| `api_key` | API key de Lemonade (**opcional**; inxecta `LEMONADE_API_KEY` para Gaia neste proceso) |
| `model` | Nome do modelo (por defecto `Gemma-4-12B-it-GGUF`) |
| `system_prompt` | Prompt completo (omite o JSON de config) |
| `prompt_params_path` | Ruta a un JSON de parámetros do prompt |
| `topic_creator` | Se é `True`, xera temas aleatorios |
| `imagination` | Temperatura do modelo (por defecto `1.0`) |
| `max_tokens` | Límite de tokens (por defecto `4096`) |

Se non se indica `system_prompt` nin `prompt_params_path`, o axente carga `config/prompt_params.json` con `PromptBuilder.from_file(...).build()`.

## Configuración

A carpeta `config/` resólvese automaticamente en desenvolvemento (raíz do repo) ou empaquetada (`story_teller_agent/config`), mediante `helpers/paths.py`.

### `prompt_params.json`

Define o system prompt vía `PromptBuilder`:

| Campo | Descrición |
|-------|------------|
| `min_age` / `max_age` | Franxa de idade do público |
| `language` | Idioma do conto |
| `personalization` | Instrucións extra inseridas na sección de personalización do prompt |

Exemplo:

```json
{
  "min_age": 5,
  "max_age": 10,
  "language": "Castellano",
  "personalization": "Incluye animales del bosque"
}
```

### Listas de temas

`TopicCreator` combina ao chou unha liña de cada ficheiro:

| Ficheiro | Rol |
|----------|-----|
| `subjects.txt` | Suxeito do conto |
| `actions.txt` | Acción |
| `objects.txt` | Obxecto |
| `object_properties.txt` | Propiedade do obxecto |
| `subject_objectives.txt` | Obxectivo do suxeito |

## Estrutura

```text
config/                         # Parámetros e listas de temas
examples/                       # Exemplos de contos
docs/                           # Documentación (ES, CA, GL)
src/story_teller_agent/
  cli.py                        # Entry point CLI (--base-url, --api-key)
  __main__.py                   # python -m story_teller_agent
  story_teller.py               # Axente (Gaia SDK)
  helpers/
    prompt_builder.py           # System prompt desde JSON
    topic_creator.py            # Temas aleatorios
    paths.py                    # Resolución de config/
tests/                          # pytest
gaia-agent.yaml                 # Metadatos do axente Gaia
LICENSE                         # GPL-3.0
```

## Tests

```bash
uv sync --group dev
.venv/bin/pytest -q
```

## Gaia

O paquete declárase como axente Gaia en `gaia-agent.yaml`:

- **Módulo:** `story_teller_agent.story_teller`
- **Clase:** `StoryTellerAgent`
- **Gaia mínima:** `0.21.2`

Se Gaia instancia `StoryTellerAgent()` sen argumentos, define `LEMONADE_BASE_URL` (e `LEMONADE_API_KEY` se fai falta) no contorno antes de lanzar Gaia. `AgentConfig` non expón `api_key`; o cliente Lemonade de Gaia le `LEMONADE_API_KEY` do contorno.

## Exemplos

Contos de mostra xerados polo axente (véxase [`examples/`](../examples/)). Os textos seguintes son **traducións ao galego**; os [orixinais](../examples/) foron escritos en **castelán**.

### [O Pequeno Dragón Matemáticas e o Erro Máxico](../examples/EL_Pequeño_Dragon_matematicas_y_el_error_magico.md)

Había unha vez un dragónciño moi especial chamado Matemáticas. Aínda que era un dragón que podía lanzar chispas brillantes, ¡era tan pequerrechíño que cabía perfectamente dentro dunha cunca de té! A súa misión máis importante no Reino dos Números era coidar de que todas as sumas e restas estivesen ben postas para que nada se desordenase no mundo máxico.

Un día, ocorreu algo moi estraño: ¡houbo un gran erro na montaña dos cálculos! Os números saltaran dun lado a outro como se estivesen xogando ao escondite. O número 3 estaba onde debía estar o 8, e as mazás do mercado estaban contando dobre por equivocación. Todo era un lío total.

Matemáticas soubo que tiña que actuar rápido. Púxose a súa pequena mochila de explorador e saíu voando con moita valentía. Ao principio, custáballe moito traballo mover as cifras grandes porque eran pesadas, pero el non se rendeu nin un segundo. «¡Con esforzo e paciencia, todo se pode arranxar!», dicía mentres voaba de aquí para alá.

Acomodou cada cifra con moito coidado, usando as súas aliñas para equilibrar os números e o seu corazón cheo de bondade para axudar a todos os habitantes do reino. Despois de traballar durante toda a tarde, ¡todo volveu estar no seu sitio! As contas eran perfectas outra vez e os nenos xa podían contar os seus xoguetes sen confundirse.

O pequeno dragón Matemáticas regresou á súa casa moi canso pero moi feliz. Demostrara que non importa o pequeno que sexas: se te esforzas e axudas aos demais, podes lograr cousas marabillosas.

### [O Regalo de Neve e Corazón](../examples/El%20Regalo%20de%20nieve%20y%20corazon.md)

Había unha vez unha mamá moi especial que vivía nun castelo feito de flores de cores. Ela tiña un corazón cheo de amor e sempre quería ver sorrir á súa familia coa maior alegría posible. Un día, viu que o seu pequeno fillo estaba un pouco triste porque desexaba ter un amigo xigante para xogar no xardín durante as noites de inverno.

A mamá decidiu usar a súa maxia secreta para axudalo. Foi ao recuncho máis fresco do seu patio máxico e plantou unha semente brillante que relucía como un diamante baixo a lúa. Durante varios días, regou a planta con auga de orballo e murmurulle palabras doces ao oído, dándolle moita forza e cariño.

¡De pronto, ocorreu algo marabilloso! Da terra brotou unha figura alta e grande feita totalmente de flocos de neve brillantes e xeada máxica. Era un «Papá de Xeo» moi suave e esponxoso como unha nube fría. Aínda que era frío ao tocalo por fóra, ¡o seu sorriso era o máis cálido do mundo!

Este novo amigo traía pequenos bonecos de xeo que bailaban soíños e regalaba flocos de neve que sabían a amorodo cando caían na boca do neno. O pequeno saltou de felicidade, abrazando o seu novo compañeiro feito de cristal e neve. A mamá lograra crear a alguén especial usando só a súa imaxinación e moito amor para encher a casa de alegría.

Desde ese día, o «Papá de Xeo» coidaba os soños do neno cada noite, recordándolles a todos que cando hai bondade no corazón, ata o frío pode converterse nun abrazo doce e marabilloso.

## Licenza

[GPL-3.0](../LICENSE)
