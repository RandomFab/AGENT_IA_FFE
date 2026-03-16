from typing import Optional, TypedDict

class AgentState(TypedDict):
    fen: str
    is_valid_fen: bool
    lichess_moves: Optional[dict] # Réponse de Lichess
    stockfish_eval: Optional[dict] # Réponse de stockfish
    final_answer: str