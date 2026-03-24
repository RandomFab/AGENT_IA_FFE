from typing import Optional, TypedDict

class AgentState(TypedDict):
    fen: str
    depth: int
    is_valid_fen: bool
    articles_context: Optional[list[dict]] # Retrieval du cours wikipedia selon la position suite de coups
    videos_context : Optional[list[dict]]
    lichess_evaluation: Optional[str] # Réponse de Lichess
    stockfish_evaluation: Optional[dict] # Réponse de stockfish
    final_answer: str