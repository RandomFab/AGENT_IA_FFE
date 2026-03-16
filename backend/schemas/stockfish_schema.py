from pydantic import BaseModel

class StockfishInput(BaseModel):
    fen: str
    depth:int

class StockfishEvaluationResponse(BaseModel):
    success: bool
    evaluation: float
    mate: int
    bestmove: str
    continuation: str