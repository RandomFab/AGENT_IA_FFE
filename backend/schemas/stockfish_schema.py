from pydantic import BaseModel
from typing import Optional

class StockfishInput(BaseModel):
    """Schéma de validation pour une requête d'évaluation Stockfish."""
    fen: str
    depth: int

class StockfishEvaluationResponse(BaseModel):
    """Schéma de validation pour une réponse d'évaluation Stockfish."""
    success: bool
    evaluation: float
    mate: int
    bestmove: str
    continuation: str