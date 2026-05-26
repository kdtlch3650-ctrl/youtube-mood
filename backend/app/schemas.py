from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class PlaylistTrackItem(BaseModel):
    title: str
    thumbnail_url: str
    url: str
    video_id: str


class RecommendationItem(BaseModel):
    id: str
    title: str
    channel_title: str
    url: str
    thumbnail_url: str
    reason: str
    playlist_tracks: list[PlaylistTrackItem] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    input_text: str
    emotions: list[str]
    mood_tags: list[str]
    search_keywords: list[str]
    recommended_tracks: list[RecommendationItem]
    recommended_playlists: list[RecommendationItem]
