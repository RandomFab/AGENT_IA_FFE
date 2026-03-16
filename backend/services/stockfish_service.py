import requests
import os
from config.logger import logger

def evaluate_position(fen: str = os.getenv("FEN_EXAMPLE"), depth: int = 5) -> dict:
    """Évalue une position d'échecs via l'API Stockfish en ligne.
    
    Args:
        fen (str): Position au format FEN (Forsyth–Edwards Notation).
        depth (int): Profondeur d'analyse en demi-coups. Défaut: 5.
    
    Returns:
        dict: Réponse JSON contenant l'évaluation ou un message d'erreur.
    """
    params = {'fen': fen, 'depth': depth}
    logger.info(f"Évaluation Stockfish demandée - Profondeur: {depth}")
    
    try:
        response = requests.post(
            os.getenv("STOCKFISH_API_URL"),
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            logger.debug(f"Réponse Stockfish reçue avec succès")
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Position non trouvée - FEN: {fen[:30]}...")
            return {
                "error": "Request failed",
                "status": 404,
            }
        else:
            logger.error(f"Erreur Stockfish - Status: {response.status_code}")
            return {
                "error": f"API error",
                "status": response.status_code,
            }
    except requests.exceptions.Timeout:
        logger.error("Timeout Stockfish après 10 secondes")
        return {"error": "Response time hitted the 10 seconds limits imposed."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de connexion Stockfish: {str(e)}")
        return {"error": f"Connection error: {str(e)}", "status": 500} 


if __name__ == "__main__":
    print(os.getenv("FEN_EXAMPLE"))
    response = evaluate_position()
    print(response)