from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.youtube import get_recommended_playlists, get_recommended_tracks

app = FastAPI(title="YouTube Mood Recommendation API")

# 프론트엔드 개발 서버에서 백엔드 API를 호출할 수 있도록 허용한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_mock_analysis(text: str) -> AnalyzeResponse:
    # 실제 AI 모델을 연결하기 전까지 고정된 분석 결과를 사용한다.
    # 이후 이 함수 내부를 모델 추론 결과로 교체할 예정이다.
    search_keywords = [
        "calm warm music playlist",
        "soft relaxing music",
        "not too sad comfort music",
    ]

    return AnalyzeResponse(
        input_text=text,
        emotions=["tired", "calm"],
        mood_tags=["calm", "warm", "not too sad"],
        search_keywords=search_keywords,
        recommended_tracks=get_recommended_tracks(search_keywords),
        recommended_playlists=get_recommended_playlists(search_keywords),
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    return create_mock_analysis(request.text)
