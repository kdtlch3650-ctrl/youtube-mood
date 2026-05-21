from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="YouTube Mood Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class AnalyzeResponse(BaseModel):
    input_text: str
    emotions: list[str]
    mood_tags: list[str]
    search_keywords: list[str]


def create_mock_analysis(text: str) -> AnalyzeResponse:
    return AnalyzeResponse(
        input_text=text,
        emotions=["tired", "calm"],
        mood_tags=["calm", "warm", "not too sad"],
        search_keywords=[
            "calm warm music playlist",
            "soft relaxing music",
            "not too sad comfort music",
        ],
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    return create_mock_analysis(request.text)
