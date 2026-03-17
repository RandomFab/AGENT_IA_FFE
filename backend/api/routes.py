from fastapi import APIRouter

from backend.services.lichess_service import evaluate_opening
from backend.services.stockfish_service import evaluate_position
from backend.schemas.lichess_schema import LichessEvaluationResponse, LichessInput
from backend.schemas.stockfish_schema import StockfishEvaluationResponse, StockfishInput
from backend.schemas.agent_schema import AgentResponse
from backend.graph.state import AgentState
from backend.graph.agent import app


router = APIRouter(prefix="/api/v1")


@router.post(
    "/moves", response_model=LichessEvaluationResponse, tags=["Lichess"]
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
    "/evaluate", response_model=StockfishEvaluationResponse, tags=["Stockfish"]
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


@router.post("/agent", response_model=AgentResponse, tags=["Agent"])
def call_chess_agent(agent_input: StockfishInput):
    """Lance l'agent intelligent d'analyse d'échecs.

    Orchestre l'analyse complète via Lichess (base théorique) et Stockfish (calcul engine).
    L'agent essaie d'abord de trouver la position dans la base théorique Lichess,
    puis utilise Stockfish pour approfondir l'analyse si nécessaire.

    Args:
        agent_input: Position en format FEN et profondeur d'analyse

    Returns:
        AgentResponse: Réponse formatée avec évaluations Lichess et/ou Stockfish et réponse finale
    """
    initial_state = AgentState(fen=agent_input.fen, depth=agent_input.depth)

    result = app.invoke(initial_state)

    # Formattage de la réponse
    return AgentResponse(
        fen=agent_input.fen,
        depth=agent_input.depth,
        final_answer=result.get("final_answer", "Erreur lors de l'analyse"),
        lichess_evaluation=result.get("lichess_evaluation"),
        stockfish_evaluation=result.get("stockfish_evaluation"),
    )
