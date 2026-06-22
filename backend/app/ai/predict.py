from app.ai.bedrock_client import load_request_hints
from app.ai.model import load_model
from app.ai.genre_mapping import extract_genre
from app.ai.mood_mapping import (
    adjust_mood_tags_by_text,
    build_mood_tags,
    build_search_keywords,
    merge_requested_mood_tags,
    resolve_mood_tags,
)
from app.ai.preprocess import preprocess_text
from app.ai.schema import AnalysisResult


def predict_analysis(text: str) -> AnalysisResult:
    cleaned_text = preprocess_text(text)

    request_hints = load_request_hints(cleaned_text)
    emotion_text = request_hints.emotion_text or cleaned_text
    request_text = request_hints.request_text

    model = load_model()

    predicted = model.predict(emotion_text)
    emotions = predicted.get("emotions", [])
    mood_tags = predicted.get("mood_tags") or build_mood_tags(emotions)
    mood_tags = adjust_mood_tags_by_text(mood_tags, emotion_text)
    mood_tags = merge_requested_mood_tags(
        mood_tags,
        request_hints.preferred_mood_tags,
        request_hints.avoid_mood_tags,
    )
    mood_tags = resolve_mood_tags(
        mood_tags,
        request_hints.preferred_mood_tags,
        request_hints.avoid_mood_tags,
        request_hints.blocked_mood_tags,
    )
    genre = extract_genre(emotion_text) or request_hints.genre_hint

    search_keywords = build_search_keywords(
        emotions,
        mood_tags,
        genre,
        [*request_hints.request_keywords, *request_hints.extra_keywords],
    )

    return AnalysisResult(
        input_text=cleaned_text,
        emotion_text=emotion_text,
        request_text=request_text,
        negative_text=request_hints.negative_text,
        emotions=emotions,
        mood_tags=mood_tags,
        genre=genre,
        search_keywords=search_keywords,
        has_avoidance=request_hints.has_avoidance,
        has_negation=request_hints.has_negation,
        request_keywords=request_hints.request_keywords,
        blocked_mood_tags=request_hints.blocked_mood_tags,
    )
