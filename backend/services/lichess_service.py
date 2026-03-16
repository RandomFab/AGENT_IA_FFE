# --- Interactions avec API Lichess ---

import os
import requests
from dotenv import load_dotenv

load_dotenv()

from config.config import FEN_EXAMPLE


def evaluate_opening(fen: str = os.getenv('FEN_EXAMPLE')) -> dict:
    """Fait un appel à l'API Lichess dans le but de récupérer le meilleur coup à jouer suivant une position envoyée

    Args:
        fen (str, optional): Suite de caractères au format fen (Forsyth–Edwards Notation). Defaults to FEN_EXAMPLE.

    Returns:
        dict: Retourne un dictionnaire renseignant :
        {
            "fen": La position fen renvoyé,
            "knodes": Nombre de positions calculées pour obtenir ce résultat,
            "depth": Profondeur de jeux,
            "pvs": Principales variation de jeu
            [
                    {
                    "moves": suite de coup explorer,
                    "cp": Avantage de la position conseillé en centipawns
                    }
            ] 
        }
    """
    url = f"{os.getenv('LICHESS_API_URL')}/api/cloud-eval"
    params = {"fen": fen}
    headers = {"Authorization": f"Bearer {os.getenv("LICHESS_API_KEY")}"}

    try:

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 404:
            return {
                "error": "Evaluation non trouvée dans la base des ouvertures connues et étudiées",
                "status": 404,
            }

        elif response.status_code == 429:
            return {"error": "Limite d'appels API Lichess dépassée", "status": 429}

    except requests.exceptions.Timeout:
        return {"error": "Response time hitted the 10 seconds limits imposed."}

    except requests.exceptions.RequestException as e:
        # Attrape toutes les autres erreurs réseau (DNS, connexion coupée, etc.)
        return {"error": f"Erreur de connexion : {str(e)}", "status": 500}


if __name__ == "__main__":
    response = evaluate_opening()
    print(response)
