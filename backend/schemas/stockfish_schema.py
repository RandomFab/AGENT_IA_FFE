from pydantic import BaseModel,Field
from typing import Optional
import os

class StockfishInput(BaseModel):
    """Schéma de validation pour une requête d'évaluation Stockfish."""
    fen: str = Field(
        ...,
        example = os.getenv('FEN_EXAMPLE'),
        description = "Position au format FEN"
    )
    depth: int = Field(
        example=5,
        default=5,
        description="Profondeur d'analyse"
    )

class StockfishEvaluationResponse(BaseModel):
    """Schéma de validation pour une réponse d'évaluation Stockfish."""
    success: Optional[bool] = None
    evaluation: Optional[float] = None
    mate: Optional[int] = None
    bestmove: Optional[str] = None
    continuation: Optional[str] = None