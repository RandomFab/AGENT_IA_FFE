from pydantic import BaseModel,Field, field_validator
from typing import Optional
import os
from backend.services.validation_chess_service import validate_position

class StockfishInput(BaseModel):
    """Schéma de validation pour une requête d'évaluation Stockfish."""
    fen: str = Field(
        ...,
        example = os.getenv('FEN_EXAMPLE'),
        description = "Position au format FEN"
    )
    depth: int = Field(
        ge=0,
        le=15,
        example=5,
        default=5,
        description="Profondeur d'analyse (0-15)"
    )

    @field_validator('fen')
    @classmethod
    def validate_fen(cls, v):
        validation = validate_position(v)
        if not validation['status']:
            raise ValueError(validation["message"])
        return v

class StockfishEvaluationResponse(BaseModel):
    """Schéma de validation pour une réponse d'évaluation Stockfish."""
    success: Optional[bool] = None
    evaluation: Optional[float] = None
    mate: Optional[int] = None
    bestmove: Optional[str] = None
    continuation: Optional[str] = None