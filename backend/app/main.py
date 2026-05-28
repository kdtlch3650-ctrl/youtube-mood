from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.predict import predict_analysis
from app.schemas import AnalyzeRequest, AnalyzeResponse, PlaylistTrackItem
from app.youtube import get_playlist_tracks, get_recommended_playlists, get_recommended_tracks

app = FastAPI(title="YouTube Mood Recommendation API")

# 프론트 개발 서버에서 API를 호출할 수 있게 CORS를 허용한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    # AI 결과를 먼저 만든 뒤, 서로 독립적인 YouTube 검색은 동시에 실행한다.
    analysis = predict_analysis(request.text)

    with ThreadPoolExecutor(max_workers=2) as executor:
        tracks_future = executor.submit(
            get_recommended_tracks,
            analysis.search_keywords,
            analysis.mood_tags,
            analysis.genre,
            request.search_scope,
        )
        playlists_future = executor.submit(
            get_recommended_playlists,
            analysis.search_keywords,
            analysis.mood_tags,
            analysis.genre,
            request.search_scope,
        )
        recommended_tracks = tracks_future.result()
        recommended_playlists = playlists_future.result()

    return AnalyzeResponse(
        input_text=analysis.input_text,
        emotions=analysis.emotions,
        mood_tags=analysis.mood_tags,
        genre=analysis.genre,
        search_keywords=analysis.search_keywords,
        recommended_tracks=recommended_tracks,
        recommended_playlists=recommended_playlists,
    )


@app.get("/api/playlists/{playlist_id}/tracks")
def playlist_tracks(playlist_id: str, title: str = "") -> list[PlaylistTrackItem]:
    # 선택한 플레이리스트의 곡 목록만 늦게 불러와 첫 결과 화면 전환 시간을 줄인다.
    return get_playlist_tracks(playlist_id, title)
