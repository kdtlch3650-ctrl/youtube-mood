from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class RecommendationItem(BaseModel):
    id: str
    title: str
    channel_title: str
    url: str
    thumbnail_url: str
    reason: str


class AnalyzeResponse(BaseModel):
    input_text: str
    emotions: list[str]
    mood_tags: list[str]
    search_keywords: list[str]
    recommended_tracks: list[RecommendationItem]
    recommended_playlists: list[RecommendationItem]
