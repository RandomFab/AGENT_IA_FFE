from fastapi import FastAPI
from backend.services.lichess_service import get_opening_evaluation
from backend.schemas.lichess_schema import LichessEvaluationResponse, FenInput

api = FastAPI()

@api.get('api/v1/')
def root():
    return  {"message":"Hello FFE"}

@api.get('/api/v1/health')
def health():
    return {"message":"Api is healthy"}

@api.post('/api/v1/moves',response_model=LichessEvaluationResponse)
def get_moves(fen_input:FenInput):

    response = get_opening_evaluation(fen=fen_input.fen)

    return response