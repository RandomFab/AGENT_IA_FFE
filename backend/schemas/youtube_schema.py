import os
from pydantic import BaseModel, Field,field_validator
from services.validation_chess_service import validate_position
from datetime import datetime

class YoutubeVideoInput(BaseModel):
    opening_name: str = "french defence"
    max_results: int = 3


class YoutubeVideoOutput(BaseModel):
    title: str
    description: str
    thumbnail_url: str
    published_at: datetime = Field(alias="publishedAt")
    video_url: str