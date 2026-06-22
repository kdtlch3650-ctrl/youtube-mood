from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from itertools import count

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.predict import predict_analysis
from app.schemas import AnalyzeRequest, AnalyzeResponse, PlaylistTrackItem, SearchRecord
from app.search_record_factory import build_search_record
from app.search_record_store import list_search_records, save_search_record
from app.youtube import get_playlist_tracks, get_recommended_playlists, get_recommended_tracks

app = FastAPI(title="YouTube Mood Recommendation API")

_record_sequence = count(1)

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


def _build_analyze_response(request: AnalyzeRequest) -> AnalyzeResponse:
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
        emotion_text=analysis.emotion_text,
        request_text=analysis.request_text,
        negative_text=analysis.negative_text,
        emotions=analysis.emotions,
        mood_tags=analysis.mood_tags,
        genre=analysis.genre,
        search_keywords=analysis.search_keywords,
        has_avoidance=analysis.has_avoidance,
        has_negation=analysis.has_negation,
        request_keywords=analysis.request_keywords,
        blocked_mood_tags=analysis.blocked_mood_tags,
        recommended_tracks=recommended_tracks,
        recommended_playlists=recommended_playlists,
    )


def _create_record(response: AnalyzeResponse, search_scope: str) -> SearchRecord:
    record_id = f"record-{next(_record_sequence)}"
    created_at = datetime.now(timezone.utc).isoformat()
    return build_search_record(record_id, created_at, response, search_scope)


@app.post("/api/analyze")
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    response = _build_analyze_response(request)
    save_search_record(_create_record(response, request.search_scope))
    return response


@app.get("/api/search-records")
def get_search_records() -> list[SearchRecord]:
    return list_search_records()


@app.get("/api/playlists/{playlist_id}/tracks")
def playlist_tracks(playlist_id: str, title: str = "") -> list[PlaylistTrackItem]:
    return get_playlist_tracks(playlist_id, title)
