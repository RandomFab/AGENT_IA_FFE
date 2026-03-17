from pydantic import BaseModel, Field,field_validator,model_validator
from typing import List, Optional
import os
from backend.services.validation_chess_service import validate_position,validate_move


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

    @model_validator(mode='after')
    def validate_moves_from_api(self):
        """Valide que tous les moves retournés par l'API sont légaux."""
        for pv in self.pvs:
            next_move = pv.moves.split(" ")[0]
            validation = validate_move(self.fen, next_move)
            if not validation['status']:
                raise ValueError(f"Move illégal retourné par l'API: {next_move}")
        return self