import os
from pydantic import BaseModel, Field, field_validator
from backend.services.validation_chess_service import validate_position
from typing import Union

class AgentInput(BaseModel):
    """Schéma de validation pour une requête d'évaluation Lichess."""
    fen: str = Field(
        ...,
        example= os.getenv('FEN_EXAMPLE'),
        description="Position au format FEN"
    )

    @field_validator('fen')
    @classmethod
    def validate_fen(cls, v):
        validation = validate_position(v)
        if not validation['status']:
            raise ValueError(validation["message"])
        return v
    depth: int = 10
    max_articles: int = 3
    max_video: int = 3


class AgentOutput(BaseModel):
    """Réponse de l'agent d'analyse échecs."""

    final_answer: str

