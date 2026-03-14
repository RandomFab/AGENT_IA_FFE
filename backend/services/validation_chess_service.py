import chess
from typing import Dict, Optional


def validate_position(fen: str) -> Dict[str, any]:
    """Valide si une position FEN est correcte."""
    try:
        board = chess.Board(fen)
        return {"status": True, "message": "Position valide"}
    except ValueError:
        return {"status": False, "message": "FEN invalide"}


def validate_move(fen: str, move: str) -> Dict:
    """
    Valide si un mouvement est légal.
    move: format UCI (ex: "e2e4" ou "e7e8q" pour promotion)
    """
    try:
        board = chess.Board(fen)
        chess_move = chess.Move.from_uci(move)
        
        if chess_move in board.legal_moves:
            new_fen = _process_move(board, chess_move)
            return {"status": True, "new_fen": new_fen}
        else:
            return {"status": False, "message": "Mouvement illégal"}
    
    except ValueError:
        return {"status": False, "message": "FEN ou mouvement au mauvais format"}
    

def _process_move(board: chess.Board, move: chess.Move) -> str:
    """Traite un mouvement et retourne la nouvelle FEN."""
    board.push(move)
    return board.fen()