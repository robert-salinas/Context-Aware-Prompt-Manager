from typing import List
from pydantic import BaseModel, Field


class PromptModel(BaseModel):
    """
    Modelo de datos para un prompt.
    Utiliza Pydantic para validación de tipos y campos requeridos.
    """

    name: str = Field(
        ..., min_length=1, max_length=120, description="Nombre descriptivo"
    )
    description: str = Field(..., max_length=500, description="Descripción breve")
    template: str = Field(
        ..., min_length=1, max_length=100_000, description="Plantilla Jinja2"
    )
    tags: List[str] = Field(
        default_factory=list, description="Etiquetas para categorización"
    )
    version: str = Field(default="0.1.0", description="Versión semántica del prompt")


def validate_prompt(data: dict) -> PromptModel:
    """
    Valida los datos de un prompt contra el modelo definido.

    Args:
        data: Diccionario con los datos del prompt.

    Returns:
        Instancia de PromptModel validada.

    Raises:
        ValidationError: Si los datos no cumplen con el esquema.
    """
    return PromptModel(**data)
