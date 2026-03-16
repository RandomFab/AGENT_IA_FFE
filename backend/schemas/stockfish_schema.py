from pydantic import BaseModel,Field, field_validator, model_validator
from typing import Optional
import os
from backend.services.validation_chess_service import validate_position, validate_move

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
    fen: Optional[str] = None
    success: Optional[bool] = None
    evaluation: Optional[float] = None
    mate: Optional[int] = None
    bestmove: Optional[str] = None
    continuation: Optional[str] = None

    @model_validator(mode='after')
    def validate_bestmove_from_api(self):
        """Valide que le bestmove retourné par l'API est légal."""
        if self.continuation and self.fen:
            next_move = self.continuation.split(" ")[0]
            validation = validate_move(self.fen, next_move)
            if not validation["status"]:
                raise ValueError(f"Mouvement illégal retourné par l'API: {next_move}")
        return self