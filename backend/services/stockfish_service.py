import requests
import os
import json

from config.config import FEN_EXAMPLE

def evaluate_position(fen:str = FEN_EXAMPLE, depth:int = 5):

    params = {'fen':fen, 'depth':depth}
    
    try:

        response = requests.post("https://stockfish.online/api/s/v2.php", params=params, timeout=10)

        if response.status_code == 200 :
            return response.json()
        elif response.status_code == 404:
            return {
            "error": "Request failed",
            "status": 404,
    }
    except requests.exceptions.Timeout :
        return {"error": "Response time hitted the 10 seconds limits imposed."} 


if __name__ == "__main__":
    print(FEN_EXAMPLE)
    response = evaluate_position()
    print(response)