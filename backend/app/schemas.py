from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    search_scope: Literal["all", "korean"] = "all"


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
    emotion_text: str = ""
    request_text: str = ""
    negative_text: str = ""
    emotions: list[str]
    mood_tags: list[str]
    genre: str | None = None
    search_keywords: list[str]
    has_avoidance: bool = False
    has_negation: bool = False
    request_keywords: list[str] = Field(default_factory=list)
    blocked_mood_tags: list[str] = Field(default_factory=list)
    recommended_tracks: list[RecommendationItem]
    recommended_playlists: list[RecommendationItem]


class SearchRecordItem(BaseModel):
    id: str
    title: str
    channel_title: str
    url: str
    thumbnail_url: str


class SearchRecord(BaseModel):
    id: str
    created_at: str
    input_text: str
    emotion_text: str = ""
    request_text: str = ""
    negative_text: str = ""
    search_scope: Literal["all", "korean"]
    emotions: list[str]
    mood_tags: list[str]
    genre: str | None = None
    search_keywords: list[str]
    has_avoidance: bool = False
    has_negation: bool = False
    request_keywords: list[str] = Field(default_factory=list)
    blocked_mood_tags: list[str] = Field(default_factory=list)
    recommended_tracks: list[SearchRecordItem]
    recommended_playlists: list[SearchRecordItem]
