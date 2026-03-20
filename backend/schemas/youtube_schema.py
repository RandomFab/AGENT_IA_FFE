from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class YoutubeVideo(BaseModel):
    title: str
    description: str
    thumbnail_url: str
    published_at: datetime = Field(alias="publishedAt")
    video_url: str

class YoutubeVideosOutput(BaseModel):
    videos: list[YoutubeVideo]