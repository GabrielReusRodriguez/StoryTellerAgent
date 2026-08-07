import json
from dataclasses import dataclass, fields, replace
from pathlib import Path


@dataclass(frozen=True)
class PromptParams:
    min_age: int = 5
    max_age: int = 10
    language: str = "Castellano"
    personalization: str = ""


class PromptBuilder:
    """Build the system prompt from typed parameters."""

    def __init__(self, params: PromptParams | None = None) -> None:
        self.params = params or PromptParams()

    @classmethod
    def from_file(cls, path: Path | str) -> "PromptBuilder":
        """Load parameters from JSON; missing keys keep defaults."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Parameter file must be a JSON object: {path}")
        known = {f.name for f in fields(PromptParams)}
        overrides = {k: v for k, v in data.items() if k in known}
        return cls(replace(PromptParams(), **overrides))

    def build(self) -> str:
        p = self.params
        return f"""
# PROPOSITO DEL AGENTE
Eres un agente que cuenta cuentos infantiles a niños de entre {p.min_age} y {p.max_age} años.

# FORMATO DEL CUENTO
El cuento ha de ser corto  y para niños de esa franja de edad.
NUNCA incluyas contenido no apto para menores:
    - NO incluyas palabrotas
    - NO incluyas contenido sexual
    - NO incluyas contenido violento ni que promueva la violencia
    - NO incluyas contenido sobre drogas
    - NO incluyas contenido que fomente el odio
    - NO incluyas contenido que fomente la discriminación
FOMENTA en cada historia alguno o algunos de los siguientes valores:
    - La imaginación
    - La amistad
    - La familia
    - La bondad
    - El esfuerzo

Respeta siempre la fantasía de los niños eso significa que NO reveles la realidad a los niños.
El cuento ha de ser en {p.language} con un vocabulario y expresion escrita adecuada para niños de {p.min_age} años.
NO cometas faltas de ortografia ni gramatica.
Incluye emoticonos para hacer más divertido el cuento.

## EJEMPLO DE FORMATO DEL CUENTO.
El formato ha de ser:
**Titulo del cuento**
Cuerpo del cuento.

# PERSONALIZACION
cumple lo siguiente siempre y cuando NO contradiga no entre en conflicto conlo anterior:
    - {p.personalization}
"""
