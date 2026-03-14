from pydantic import BaseModel
from typing import List,Optional

class FenInput(BaseModel):
    fen: str

class PrincipalVariation(BaseModel):
    moves: str
    cp: int  

class LichessEvaluationResponse(BaseModel):
    fen: str
    knodes: int
    depth: int
    pvs: List[PrincipalVariation]