from typing import List, Optional
from pydantic import BaseModel, Field


class PromptModel(BaseModel):
    """
    Modelo de datos para un prompt.
    Utiliza Pydantic para validación de tipos y campos requeridos.
    """

    name: str = Field(..., description="Nombre descriptivo del prompt")
    description: str = Field(..., description="Descripción breve de la funcionalidad")
    template: str = Field(..., description="Template de Jinja2 para el prompt")
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
