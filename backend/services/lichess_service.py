import os
import requests


from dotenv import load_dotenv

load_dotenv()

FEN_EXAMPLE = "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"


def get_opening_evaluation(fen: str = FEN_EXAMPLE) -> dict:

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
    response = get_opening_evaluation()
    print(response)
