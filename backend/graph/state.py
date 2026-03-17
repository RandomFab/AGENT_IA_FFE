from typing import Optional, TypedDict

class AgentState(TypedDict):
    fen: str
    depth: int
    is_valid_fen: bool
    lichess_evaluation: Optional[dict] # Réponse de Lichess
    stockfish_evaluation: Optional[dict] # Réponse de stockfish
    final_answer: str