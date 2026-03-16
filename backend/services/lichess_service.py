# --- Interactions avec API Lichess ---

import os
import requests
from dotenv import load_dotenv
from config.logger import logger

load_dotenv()



def evaluate_opening(fen: str = os.getenv("FEN_EXAMPLE")) -> dict:
    """Évalue une ouverture via l'API Lichess Cloud Eval.
    
    Récupère le meilleur coup et l'évaluation d'une position d'échecs depuis
    la base de données Lichess des positions connues et étudiées.

    Args:
        fen (str): Position au format FEN (Forsyth–Edwards Notation).

    Returns:
        dict: Dictionnaire contenant:
            - "fen": Position FEN renvoyée
            - "knodes": Nombre de nœuds évalués  
            - "depth": Profondeur d'analyse
            - "pvs": Liste des variations principales avec {
                "moves": coups suggérés,
                "cp": avantage en centipawns
              }
            Ou dictionnaire d'erreur en cas d'échec.
    """
    url = f"{os.getenv('LICHESS_API_URL')}/api/cloud-eval"
    params = {"fen": fen}
    headers = {"Authorization": f"Bearer {os.getenv("LICHESS_API_KEY")}"}
    
    logger.info(f"Évaluation Lichess demandée")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            logger.debug(f"Réponse Lichess reçue avec succès")
            return response.json()

        elif response.status_code == 404:
            logger.warning(f"Évaluation non trouvée pour la position - FEN: {fen[:30]}...")
            return {
                "error": "Evaluation non trouvée dans la base des ouvertures connues et étudiées",
                "status": 404,
            }

        elif response.status_code == 429:
            logger.warning(f"Limite d'appels API Lichess atteinte")
            return {"error": "Limite d'appels API Lichess dépassée", "status": 429}
        
        else:
            logger.error(f"Erreur Lichess - Status: {response.status_code}")
            return {"error": f"API error", "status": response.status_code}

    except requests.exceptions.Timeout:
        logger.error("Timeout Lichess après 10 secondes")
        return {"error": "Response time hitted the 10 seconds limits imposed.", "status": 504}

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de connexion Lichess: {str(e)}")
        return {"error": f"Erreur de connexion : {str(e)}", "status": 500}


if __name__ == "__main__":
    response = evaluate_opening()
    print(response)
