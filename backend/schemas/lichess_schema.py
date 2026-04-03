from pydantic import BaseModel, Field,field_validator,model_validator
from typing import List, Optional
import os
from services.validation_chess_service import validate_position,validate_move


class LichessInput(BaseModel):
    """Schéma de validation pour une requête d'évaluation Lichess."""
    fen: str = Field(
        ...,
        example= os.getenv('FEN_EXAMPLE'),
        description="Position au format FEN"
    )

    @field_validator('fen')
    @classmethod
    def validate_fen(cls, v):
        validation = validate_position(v)
        if not validation['status']:
            raise ValueError(validation["message"])
        return v

class Opening(BaseModel):
    """Opening information with ECO code and name."""
    eco: str = Field(..., description="ECO opening code")
    name: str = Field(..., description="Opening name")


class Move(BaseModel):
    """Single move with statistics and opening information."""
    uci: str = Field(..., description="Move in UCI notation (e.g., 'e2e4')")
    san: str = Field(..., description="Move in SAN notation (e.g., 'e4')")
    averageRating: int = Field(..., description="Average rating of players making this move")
    white: int = Field(..., description="Number of white wins")
    draws: int = Field(..., description="Number of draws")
    black: int = Field(..., description="Number of black wins")
    game: Optional[str] = Field(None, description="Example game ID")
    opening: Optional[Opening] = Field(None, description="Opening info if available")


class Player(BaseModel):
    """Player information in a game."""
    name: str = Field(..., description="Player username")
    rating: int = Field(..., description="Player rating")


class Game(BaseModel):
    """Game record from recent or top games."""
    uci: str = Field(..., description="First move in UCI notation")
    id: str = Field(..., description="Lichess game ID")
    winner: Optional[str] = Field(None, description="'white', 'black', or None for draw")
    speed: str = Field(..., description="Game speed (bullet, blitz, rapid, etc.)")
    mode: str = Field(..., description="Game mode (rated, casual)")
    black: Player = Field(..., description="Black player info")
    white: Player = Field(..., description="White player info")
    year: int = Field(..., description="Year the game was played")
    month: str = Field(..., description="Month in YYYY-MM format")


class LichessOpeningWithGamesResponse(BaseModel):
    """Complete response from Lichess opening endpoint with games or error."""
    white: Optional[int] = Field(None, description="Total white wins at this position")
    draws: Optional[int] = Field(None, description="Total draws at this position")
    black: Optional[int] = Field(None, description="Total black wins at this position")
    moves: Optional[List[Move]] = Field(None, description="List of possible next moves with stats")
    recentGames: Optional[List[Game]] = Field(None, description="Recent games played from this position")
    topGames: Optional[List[Game]] = Field(None, description="Top player games from this position")
    opening: Optional[Opening] = Field(None, description="Opening info at this position")
    error: Optional[str] = Field(None, description="Error message if position not found")
    status: Optional[int] = Field(None, description="HTTP status code (200 for success, 404 for not found)")