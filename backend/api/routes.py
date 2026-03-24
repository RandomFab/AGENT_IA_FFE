from fastapi import APIRouter

from backend.services.lichess_service import evaluate_opening
from backend.services.stockfish_service import evaluate_position
from backend.services.rag_service import retrieve_articles
from backend.services.youtube_service import get_ytb_video

from backend.schemas.lichess_schema import LichessOpeningWithGamesResponse, LichessInput
from backend.schemas.stockfish_schema import StockfishEvaluationResponse, StockfishInput
from backend.schemas.agent_schema import AgentInput, AgentOutput
from backend.schemas.rag_schema import RAGSearchInput,RAGSearchResult
from backend.schemas.youtube_schema import YoutubeVideoOutput, YoutubeVideoInput

from backend.graph.state import AgentState
from backend.graph.agent import app


router = APIRouter(prefix="/api/v1")


@router.post(
    "/opening", response_model=LichessOpeningWithGamesResponse, tags=["move_evaluation"]
)
def get_lichess_moves(lichess_input: LichessInput):
    """Récupère les meilleurs coups d'une position via Lichess.

    Args:
        lichess_input: Position en format FEN

    Returns:
        LichessEvaluationResponse: Évaluation et variations principales
    """
    response = evaluate_opening(fen=lichess_input.fen)
    return response


@router.post(
    "/evaluate", response_model=StockfishEvaluationResponse, tags=["move_evaluation"]
)
def get_stockfish_evaluation(stockfish_input: StockfishInput):
    """Évalue une position d'échecs via Stockfish.

    Args:
        stockfish_input: Position en format FEN et profondeur d'analyse

    Returns:
        StockfishEvaluationResponse: Évaluation et meilleur coup
    """
    response = evaluate_position(fen=stockfish_input.fen, depth=stockfish_input.depth)
    response["fen"] = stockfish_input.fen  # ← Ajouter le FEN
    return response


@router.post("/retrieve_video", response_model=list[YoutubeVideoOutput], tags=["retrieve"])
def search_video(youtube_video_input: YoutubeVideoInput):
    """Recherche des videos relatif à l'ouverture via YouTube.

    Args:
        youtube_video_input: Texte à rechercher et nombre de résultats souhaités

    Returns:
        Liste de résultats avec similarité et métadonnées (title, miniature, description, date de publication, lien video)
    """
    results = get_ytb_video(opening=youtube_video_input.opening_name, max_results=youtube_video_input.max_results)
    return results


@router.post("/retrieve_articles", response_model=list[RAGSearchResult], tags=["retrieve"])
def search_rag(rag_input: RAGSearchInput):
    """Recherche des articles similaires via RAG (Retrieval Augmented Generation).

    Args:
        rag_input: Texte à rechercher et nombre de résultats souhaités

    Returns:
        Liste de résultats avec similarité et métadonnées (title, text, source)
    """
    results = retrieve_articles(request_text=rag_input.query, limit=rag_input.limit)
    return results

@router.post("/agent", response_model=AgentOutput, tags=["Agent"])
def call_chess_agent(agent_input: AgentInput):
    """Lance l'agent intelligent d'analyse d'échecs.

    Orchestre l'analyse complète via Lichess (base théorique) et Stockfish (calcul engine).
    L'agent essaie d'abord de trouver la position dans la base théorique Lichess,
    puis utilise Stockfish pour approfondir l'analyse si nécessaire.

    Args:
        agent_input: Position en format FEN et profondeur d'analyse

    Returns:
        AgentResponse: Réponse formatée avec évaluations Lichess et/ou Stockfish et réponse finale
    """
    initial_state = AgentState(fen=agent_input.fen)

    result = app.invoke(initial_state)

    # Formattage de la réponse
    return AgentOutput(final_answer=result.get("final_answer", "Erreur lors de l'analyse"),)

