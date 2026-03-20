from backend.services.rag_service import retrieve_articles
from pydantic import BaseModel

class RAGSearchInput(BaseModel):
    """Schéma d'entrée pour recherche RAG."""
    query: str = "french defence"
    limit: int = 2


class RAGSearchResult(BaseModel):
    """Schéma de résultat RAG."""
    id: int
    distance: float
    title: str
    text: str
    source: str

