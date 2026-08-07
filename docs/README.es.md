# StoryTellerAgent

**Idioma:** [English](../README.md) | Castellano | [Català](README.ca.md) | [Galego](README.gl.md)

Agente de cuentos infantiles basado en Gaia (`amd-gaia`), creado para usarse con **AMD Lemonade AI** como backend LLM local. Genera historias cortas en streaming, con temas aleatorios y un system prompt configurable por JSON.

## Requisitos

- Python ≥ 3.12
- [uv](https://github.com/astral-sh/uv)
- [AMD Lemonade AI](https://lemonade-server.ai/) (o una API compatible estilo OpenAI)
- Ver [Variables de entorno](#variables-de-entorno) más abajo

## Instalación

```bash
cd StoryTellerAgent
uv sync --group dev
```

Esto crea el entorno virtual, instala `amd-gaia` (≥ 0.21.2) y las dependencias de desarrollo (`pytest`).

## Variables de entorno

El agente lee la configuración del **entorno del proceso** (y flags opcionales del CLI). **No** carga un fichero `.env`.

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `LEMONADE_BASE_URL` | **Sí** | URL base de la API de Lemonade, p. ej. `http://localhost:8000/api/v1` |
| `LEMONADE_API_KEY` | No | API key si el servidor Lemonade requiere autenticación (`Authorization: Bearer …`) |

## Uso

```bash
# Activar el entorno (opcional)
source .venv/bin/activate

# Obligatorio: URL de Lemonade
export LEMONADE_BASE_URL=http://localhost:8000/api/v1
# Opcional: solo si el servidor Lemonade exige auth
export LEMONADE_API_KEY=tu-api-key

# CLI
storyteller-agent

# O pasar URL / key en la línea de comandos
storyteller-agent --base-url http://localhost:8000/api/v1 --api-key tu-api-key

# Como módulo
python -m story_teller_agent
```

Ambos crean un `StoryTellerAgent` con generador de temas (`TopicCreator`) y escriben el cuento por stdout en streaming. Los bloques `<think>…</think>` del modelo se filtran.

Flags del CLI:

| Flag | Descripción |
|------|-------------|
| `--base-url` | Equivale a `LEMONADE_BASE_URL` (tiene prioridad sobre la env en esta ejecución) |
| `--api-key` | Equivale a `LEMONADE_API_KEY` (solo afecta a este proceso) |

### Uso programático

```python
from story_teller_agent import StoryTellerAgent

# Usa LEMONADE_BASE_URL / LEMONADE_API_KEY del entorno,
# o pasa base_url=... / api_key=...
agent = StoryTellerAgent(topic_creator=True)
for chunk in agent.tell_stream():
    print(chunk, end="", flush=True)
```

Parámetros útiles del constructor:

| Parámetro | Descripción |
|-----------|-------------|
| `base_url` | URL de la API de Lemonade (**obligatoria** si no está `LEMONADE_BASE_URL`) |
| `api_key` | API key de Lemonade (**opcional**; inyecta `LEMONADE_API_KEY` para Gaia en este proceso) |
| `model` | Nombre del modelo (por defecto `Gemma-4-12B-it-GGUF`) |
| `system_prompt` | Prompt completo (omite el JSON de config) |
| `prompt_params_path` | Ruta a un JSON de parámetros del prompt |
| `topic_creator` | Si es `True`, genera temas aleatorios |
| `imagination` | Temperatura del modelo (por defecto `1.0`) |
| `max_tokens` | Límite de tokens (por defecto `4096`) |

Si no se indica `system_prompt` ni `prompt_params_path`, el agente carga `config/prompt_params.json` con `PromptBuilder.from_file(...).build()`.

## Configuración

La carpeta `config/` se resuelve automáticamente en desarrollo (raíz del repo) o empaquetada (`story_teller_agent/config`), mediante `helpers/paths.py`.

### `prompt_params.json`

Define el system prompt vía `PromptBuilder`:

| Campo | Descripción |
|-------|-------------|
| `min_age` / `max_age` | Franja de edad del público |
| `language` | Idioma del cuento |
| `personalization` | Instrucciones extra insertadas en la sección de personalización del prompt |

Ejemplo:

```json
{
  "min_age": 5,
  "max_age": 10,
  "language": "Castellano",
  "personalization": "Incluye animales del bosque"
}
```

### Listas de temas

`TopicCreator` combina al azar una línea de cada fichero:

| Fichero | Rol |
|---------|-----|
| `subjects.txt` | Sujeto del cuento |
| `actions.txt` | Acción |
| `objects.txt` | Objeto |
| `object_properties.txt` | Propiedad del objeto |
| `subject_objectives.txt` | Objetivo del sujeto |

## Estructura

```text
config/                         # Parámetros y listas de temas
examples/                       # Ejemplos de cuentos
docs/                           # Documentación (ES, CA, GL)
src/story_teller_agent/
  cli.py                        # Entry point CLI (--base-url, --api-key)
  __main__.py                   # python -m story_teller_agent
  story_teller.py               # Agente (Gaia SDK)
  helpers/
    prompt_builder.py           # System prompt desde JSON
    topic_creator.py            # Temas aleatorios
    paths.py                    # Resolución de config/
tests/                          # pytest
gaia-agent.yaml                 # Metadatos del agente Gaia
LICENSE                         # GPL-3.0
```

## Tests

```bash
uv sync --group dev
.venv/bin/pytest -q
```

## Gaia

El paquete se declara como agente Gaia en `gaia-agent.yaml`:

- **Módulo:** `story_teller_agent.story_teller`
- **Clase:** `StoryTellerAgent`
- **Gaia mínima:** `0.21.2`

Si Gaia instancia `StoryTellerAgent()` sin argumentos, define `LEMONADE_BASE_URL` (y `LEMONADE_API_KEY` si hace falta) en el entorno antes de lanzar Gaia. `AgentConfig` no expone `api_key`; el cliente Lemonade de Gaia lee `LEMONADE_API_KEY` del entorno.

## Ejemplos

Cuentos de muestra generados por el agente (ver [`examples/`](../examples/)). Los textos siguientes son los **originales** en **castellano** (no traducidos).

### [El Pequeño Dragón Matemáticas y el Error Mágico](../examples/EL_Pequeño_Dragon_matematicas_y_el_error_magico.md)

Había una vez un dragoncito muy especial llamado Matemáticas. Aunque era un dragón que podía lanzar chispas brillantes, ¡era tan pequeñito que cabía perfectamente dentro de una taza de té! Su misión más importante en el Reino de los Números era cuidar que todas las sumas y restas estuvieran bien puestas para que nada se desordenara en el mundo mágico.

Un día, algo muy extraño ocurrió: ¡hubo un gran error en la montaña de los cálculos! Los números habían saltado de un lado a otro como si estuvieran jugando a las escondidas. El número 3 estaba donde debía estar el 8, y las manzanas del mercado estaban contando doble por equivocación. Todo era un lío total.

Matemáticas supo que tenía que actuar rápido. Se puso su pequeña mochila de explorador y salió volando con mucha valentía. Al principio, le costaba mucho trabajo mover las cifras grandes porque eran pesadas, pero él no se rindió ni un segundo. "¡Con esfuerzo y paciencia, todo se puede arreglar!", decía mientras volaba de aquí para allá.

Acomodó cada cifra con mucho cuidado, usando sus alitas para equilibrar los números y su corazón lleno de bondad para ayudar a todos los habitantes del reino. Después de trabajar durante toda la tarde, ¡todo volvió a estar en su sitio! Las cuentas eran perfectas otra vez y los niños ya podían contar sus juguetes sin confundirse.

El pequeño dragón Matemáticas regresó a su casa muy cansado pero muy feliz. Había demostrado que no importa lo pequeño que seas, si te esfuerzas y ayudas a los demás, puedes lograr cosas maravillosas.

### [El Regalo de Nieve y Corazón](../examples/El%20Regalo%20de%20nieve%20y%20corazon.md)

Había una vez una mamá muy especial que vivía en un castillo hecho de flores de colores. Ella tenía un corazón lleno de amor y siempre quería ver sonreír a su familia con la mayor alegría posible. Un día, vio que su pequeño hijo estaba un poco triste porque deseaba tener un amigo gigante para jugar en el jardín durante las noches de invierno.

La mamá decidió usar su magia secreta para ayudarlo. Fue al rincón más fresco de su patio mágico y plantó una semilla brillante que relucía como un diamante bajo la luna. Durante varios días, regó la planta con agua de rocío y le susurró palabras dulces al oído, dándole mucha fuerza y cariño.

¡De pronto, ocurrió algo maravilloso! De la tierra brotó una figura alta y grande hecha totalmente de copos de nieve brillantes y escarcha mágica. Era un "Papá de Hielo" muy suave y esponjoso como una nube fría. Aunque era frío al tocarlo por fuera, ¡su sonrisa era lo más cálida del mundo!

Este nuevo amigo traía pequeños muñecos de hielo que bailaban solos y regalaba copos de nieve que sabían a fresa cuando caían en la boca del niño. El pequeño saltó de felicidad, abrazando a su nuevo compañero hecho de cristal y nieve. La mamá había logrado crear a alguien especial usando solo su imaginación y mucho amor para llenar la casa de alegría.

Desde ese día, el "Papá de Hielo" cuidaba los sueños del niño cada noche, recordándoles a todos que cuando hay bondad en el corazón, hasta el frío puede convertirse en un abrazo dulce y maravilloso.

## Licencia

[GPL-3.0](../LICENSE)
