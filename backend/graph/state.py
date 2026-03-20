from typing import Optional, TypedDict

class AgentState(TypedDict):
    fen: str
    depth: int
    is_valid_fen: bool
    milvus_context: Optional[str] # Retrieval du cours wikipediaselon la position suite de coups
    lichess_evaluation: Optional[str] # Réponse de Lichess
    stockfish_evaluation: Optional[dict] # Réponse de stockfish
    final_answer: str