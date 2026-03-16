from pydantic import BaseModel, Field
from typing import List, Optional
import os


class LichessInput(BaseModel):
    """Schéma de validation pour une requête d'évaluation Lichess."""
    fen: str = Field(
        ...,
        example= os.getenv('FEN_EXAMPLE'),
        description="Position au format FEN"
    )

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