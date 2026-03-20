from pydantic import BaseModel
from typing import Union

class AgentResponse(BaseModel):
    """Réponse de l'agent d'analyse échecs."""
    fen: str
    depth: int
    final_answer: str
    lichess_evaluation: Union[dict, None] = None  # Opening name as string
    stockfish_evaluation: Union[dict, None] = None  # {move, cp} as dict
