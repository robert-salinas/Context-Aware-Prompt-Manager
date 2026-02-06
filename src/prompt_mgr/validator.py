from typing import List, Optional
from pydantic import BaseModel, Field

class PromptModel(BaseModel):
    name: str = Field(..., description="The name of the prompt")
    description: str = Field(..., description="A short description of what the prompt does")
    template: str = Field(..., description="The Jinja2 template for the prompt")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    version: str = Field(default="0.1.0", description="Semantic version of the prompt")

def validate_prompt(data: dict) -> PromptModel:
    """Validates prompt data against the PromptModel."""
    return PromptModel(**data)
