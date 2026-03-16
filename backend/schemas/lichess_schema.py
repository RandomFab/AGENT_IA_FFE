from pydantic import BaseModel, Field,field_validator
from typing import List, Optional
import os
from backend.services.validation_chess_service import validate_position


class LichessInput(BaseModel):
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

class PrincipalVariation(BaseModel):
    """Schéma pour une variation principale d'une position."""
    moves: str
    cp: int

class LichessEvaluationResponse(BaseModel):
    """Schéma de validation pour une réponse d'évaluation Lichess."""
    fen: str
    knodes: int
    depth: int
    pvs: List[PrincipalVariation]