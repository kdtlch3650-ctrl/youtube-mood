from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    input_text: str
    emotion_text: str = ""
    request_text: str = ""
    emotions: list[str] = Field(default_factory=list)
    mood_tags: list[str] = Field(default_factory=list)
    genre: str | None = None
    search_keywords: list[str] = Field(default_factory=list)
    has_avoidance: bool = False
    has_negation: bool = False
    request_keywords: list[str] = Field(default_factory=list)
