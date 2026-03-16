import chess
from typing import Dict, Optional
from config.logger import logger


def validate_position(fen: str) -> Dict[str, any]:
    """Valide si une position FEN est correcte."""
    logger.debug(f"Validation position - FEN reçu: {fen[:50]}...")
    try:
        board = chess.Board(fen)
        logger.info(f"✓ Position valide")
        return {"status": True, "message": "Position valide"}
    except ValueError as e:
        logger.error(f"✗ FEN invalide: {str(e)}")
        return {"status": False, "message": "FEN invalide"}


def validate_move(fen: str, move: str) -> Dict:
    """
    Valide si un mouvement est légal.
    move: format UCI (ex: "e2e4" ou "e7e8q" pour promotion)
    """
    logger.debug(f"Validation move - FEN: {fen[:50]}..., Move: {move}")
    try:
        board = chess.Board(fen)
        chess_move = chess.Move.from_uci(move)
        
        if chess_move in board.legal_moves:
            new_fen = _process_move(board, chess_move)
            logger.info(f"✓ Move légal: {move} → Nouvelle FEN: {new_fen[:50]}...")
            return {"status": True, "new_fen": new_fen}
        else:
            logger.warning(f"✗ Move illégal pour cette position: {move}")
            return {"status": False, "message": "Mouvement illégal"}
    
    except ValueError as e:
        logger.error(f"✗ Erreur format FEN ou move: {str(e)}")
        return {"status": False, "message": "FEN ou mouvement au mauvais format"}
    

def _process_move(board: chess.Board, move: chess.Move) -> str:
    """Traite un mouvement et retourne la nouvelle FEN."""
    board.push(move)
    return board.fen()