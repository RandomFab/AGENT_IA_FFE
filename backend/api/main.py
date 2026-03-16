from fastapi import FastAPI
from backend.services.lichess_service import evaluate_opening
from backend.services.stockfish_service import evaluate_position
from backend.schemas.lichess_schema import LichessEvaluationResponse, LichessInput
from backend.schemas.stockfish_schema import StockfishEvaluationResponse, StockfishInput

api = FastAPI()

@api.get('api/v1/')
def root():
    """Endpoint racine de l'API."""
    return {"message": "Hello FFE"}

@api.get('/api/v1/health')
def health():
    """Vérifie l'état de santé de l'API."""
    return {"message": "Api is healthy"}

@api.post('/api/v1/moves', response_model=LichessEvaluationResponse)
def get_lichess_moves(lichess_input: LichessInput):
    """Récupère les meilleurs coups d'une position via Lichess.
    
    Args:
        lichess_input: Position en format FEN
    
    Returns:
        LichessEvaluationResponse: Évaluation et variations principales
    """
    response = evaluate_opening(fen=lichess_input.fen)
    return response

@api.post('/api/v1/evaluate', response_model=StockfishEvaluationResponse)
def get_stockfish_evaluation(stockfish_input: StockfishInput):
    """Évalue une position d'échecs via Stockfish.
    
    Args:
        stockfish_input: Position en format FEN et profondeur d'analyse
    
    Returns:
        StockfishEvaluationResponse: Évaluation et meilleur coup
    """
    response = evaluate_position(fen=stockfish_input.fen, depth=stockfish_input.depth)
    response['fen'] = stockfish_input.fen  # ← Ajouter le FEN
    return response