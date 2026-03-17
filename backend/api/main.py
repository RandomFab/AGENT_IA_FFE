from fastapi import FastAPI
from pydantic import BaseModel
from backend.services.lichess_service import evaluate_opening
from backend.services.stockfish_service import evaluate_position
from backend.schemas.lichess_schema import LichessEvaluationResponse, LichessInput
from backend.schemas.stockfish_schema import StockfishEvaluationResponse, StockfishInput
from backend.schemas.agent_schema import AgentResponse
from backend.graph.state import AgentState
from backend.graph.agent import app


# --- Configuration FastAPI ---
tags_metadata = [
    {
        "name": "Health",
        "description": "Vérification de l'état du service",
    },
    {
        "name": "Lichess",
        "description": "Accès à la base théorique Lichess",
    },
    {
        "name": "Stockfish",
        "description": "Analyse d'échecs avec Stockfish",
    },
    {
        "name": "Agent",
        "description": "Agent intelligent d'analyse d'échecs (Lichess + Stockfish)",
    },
]

api = FastAPI(
    title="FFE Chess Analysis API",
    description="API d'analyse d'échecs avec accès à la base théorique et moteur d'analyse",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


@api.get("api/v1/", tags=["Health"])
def root():
    """Endpoint racine de l'API."""
    return {"message": "Hello FFE"}


@api.get("/api/v1/health", tags=["Health"])
def health():
    """Vérifie l'état de santé de l'API."""
    return {"message": "Api is healthy"}


@api.post("/api/v1/moves", response_model=LichessEvaluationResponse, tags=["Lichess"])
def get_lichess_moves(lichess_input: LichessInput):
    """Récupère les meilleurs coups d'une position via Lichess.

    Args:
        lichess_input: Position en format FEN

    Returns:
        LichessEvaluationResponse: Évaluation et variations principales
    """
    response = evaluate_opening(fen=lichess_input.fen)
    return response


@api.post("/api/v1/evaluate", response_model=StockfishEvaluationResponse, tags=["Stockfish"])
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


@api.post("/api/v1/agent", response_model=AgentResponse, tags=["Agent"])
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