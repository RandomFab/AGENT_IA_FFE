from pydantic import BaseModel

class AgentResponse(BaseModel):
    """Réponse de l'agent d'analyse échecs."""
    fen: str
    depth: int
    final_answer: str
    lichess_evaluation: str | None = None
    stockfish_evaluation: str | None = None
