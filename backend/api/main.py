from fastapi import FastAPI
from backend.services.lichess_service import get_opening_evaluation

api = FastAPI()

@api.get('api/v1/')
def root():
    return  {"message":"Hello FFE"}

@api.get('/api/v1/health')
def health():
    return {"message":"Api is healthy"}

@api.get('/api/v1/moves')
def get_moves(fen:str):

    response = get_opening_evaluation(fen=fen)

    return response