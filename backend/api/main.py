from fastapi import FastAPI
from backend.services.lichess_service import evaluate_opening
from backend.schemas.lichess_schema import LichessEvaluationResponse, LichessInput

api = FastAPI()

@api.get('api/v1/')
def root():
    return  {"message":"Hello FFE"}

@api.get('/api/v1/health')
def health():
    return {"message":"Api is healthy"}

@api.post('/api/v1/moves',response_model=LichessEvaluationResponse)
def get_moves(fen_input:LichessInput):

    response = evaluate_opening(fen=fen_input.fen)

    return response