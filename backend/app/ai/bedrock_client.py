from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

import requests

ALLOW_MOOD_TAGS = {"soft", "quiet", "warm", "late night", "heavy", "uplifting", "light", "minimal"}
ALLOW_SCOPE = {"all", "korean"}

REQUEST_PATTERNS = [
    "추천해줘",
    "추천해 줘",
    "찾아줘",
    "틀어줘",
    "들려줘",
    "들려 줘",
    "듣고 싶어",
    "듣고싶어",
    "듣고 싶다",
    "듣고싶다",
    "좋겠어",
    "좋겠다",
    "좋을거 같아",
    "좋을 것 같아",
    "좋을거 같음",
    "좋을 것 같음",
    "좋을 거 같아",
    "좋을 거 같음",
    "했으면 좋겠어",
    "했으면 좋겠다",
    "이면 좋겠어",
    "이면 좋겠다",
    "원해",
    "원한다",
    "원해요",
    "원합니다",
    "듣고 싶지 않아",
    "듣고싶지않아",
    "듣고 싶지않아",
    "듣고싶지 않아",
    "듣기 싫어",
    "듣기싫어",
    "원하지 않아",
    "원하지않아",
    "듣고 싶지 않다",
    "말고",
]

NEGATIVE_REQUEST_PATTERNS = [
    "듣고 싶지 않아",
    "듣고싶지않아",
    "듣고 싶지않아",
    "듣고싶지 않아",
    "듣기 싫어",
    "듣기싫어",
    "원하지 않아",
    "원하지않아",
    "싫어",
    "싫다",
    "않아",
    "않고",
    "말고",
]

REQUEST_MODIFIER_WORDS = {
    "신나는",
    "흥겨운",
    "활기찬",
    "밝은",
    "차분한",
    "조용한",
    "잔잔한",
    "편안한",
    "가벼운",
    "빠른",
    "느린",
    "강한",
    "무거운",
    "지루한",
    "댄스",
    "댄스음악",
}

DESIRE_REQUEST_PATTERNS = {
    "좋겠어",
    "좋겠다",
    "좋을거 같아",
    "좋을 것 같아",
    "좋을거 같음",
    "좋을 것 같음",
    "좋을 거 같아",
    "좋을 거 같음",
    "했으면 좋겠어",
    "했으면 좋겠다",
    "이면 좋겠어",
    "이면 좋겠다",
    "원해",
    "원한다",
    "원해요",
    "원합니다",
}


@dataclass
class RequestHints:
    emotion_text: str = ""
    request_text: str = ""
    negative_text: str = ""
    request_keywords: list[str] = field(default_factory=list)
    preferred_mood_tags: list[str] = field(default_factory=list)
    avoid_mood_tags: list[str] = field(default_factory=list)
    blocked_mood_tags: list[str] = field(default_factory=list)
    extra_keywords: list[str] = field(default_factory=list)
    genre_hint: str | None = None
    search_scope_hint: str | None = None
    has_avoidance: bool = False
    has_negation: bool = False


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def _merge_unique(*values: list[str]) -> list[str]:
    merged: list[str] = []
    for value_list in values:
        for value in value_list:
            if value not in merged:
                merged.append(value)
    return merged


def _normalize_tags(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []

    normalized: list[str] = []

    for value in values:
        if not isinstance(value, str):
            continue

        tag = value.strip().lower()
        if tag in ALLOW_MOOD_TAGS:
            normalized.append(tag)

    return _unique(normalized)


def _normalize_scope(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    scope = value.strip().lower()
    if scope in ALLOW_SCOPE:
        return scope

    return None


def _normalize_keywords(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []

    keywords: list[str] = []

    for value in values:
        if not isinstance(value, str):
            continue

        keyword = value.strip()
        if keyword:
            keywords.append(keyword)

    return _unique(keywords)


def _parse_json_payload(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _remove_request_phrase(text: str) -> str:
    cleaned = text
    for pattern in REQUEST_PATTERNS:
        cleaned = cleaned.replace(pattern, "")
    cleaned = re.sub(r"[?.!~]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _split_request_and_emotion_text(text: str) -> tuple[str, str]:
    request_index = len(text)
    matched_pattern = ""

    for pattern in REQUEST_PATTERNS:
        index = text.find(pattern)
        if index == -1:
            continue
        if index < request_index:
            request_index = index
            matched_pattern = pattern

    if not matched_pattern:
        return text, ""

    prefix = text[:request_index].strip(" .!?~")
    suffix = text[request_index:].strip(" .!?~")
    prefix_words = prefix.split()

    modifier_index = -1
    for index, word in enumerate(prefix_words):
        if word in REQUEST_MODIFIER_WORDS:
            modifier_index = index

    if modifier_index != -1:
        suffix = " ".join([*prefix_words[modifier_index:], suffix]).strip()
        prefix_words = prefix_words[:modifier_index]
    elif matched_pattern in DESIRE_REQUEST_PATTERNS and prefix_words:
        request_prefix = " ".join(prefix_words[-2:]).strip()
        if request_prefix:
            suffix = " ".join([request_prefix, suffix]).strip()
        prefix_words = prefix_words[:-2] if len(prefix_words) > 2 else []

    emotion_text = " ".join(prefix_words).strip()
    if not emotion_text:
        emotion_text = text

    return emotion_text, suffix


def _split_negative_and_request_text(text: str) -> tuple[str, str]:
    negative_index = len(text)
    matched_pattern = ""

    for pattern in NEGATIVE_REQUEST_PATTERNS:
        index = text.find(pattern)
        if index == -1:
            continue
        if index < negative_index:
            negative_index = index
            matched_pattern = pattern

    if not matched_pattern:
        return "", text.strip()

    negative_text = text[: negative_index + len(matched_pattern)].strip(" .!?~")
    request_text = text[negative_index + len(matched_pattern) :].strip(" .!?~")
    return negative_text, request_text


def _build_local_request_hints(text: str) -> RequestHints:
    normalized = text.lower()
    preferred_mood_tags: list[str] = []
    avoid_mood_tags: list[str] = []
    blocked_mood_tags: list[str] = []
    extra_keywords: list[str] = []
    request_keywords: list[str] = []
    search_scope_hint: str | None = None
    has_avoidance = False
    has_negation = False

    emotion_text, request_text = _split_request_and_emotion_text(text)
    negative_text, request_text = _split_negative_and_request_text(request_text)

    if request_text:
        cleaned_request = _remove_request_phrase(request_text)
        if cleaned_request:
            request_keywords.append(cleaned_request)

    if negative_text and any(keyword in negative_text.lower() for keyword in ["느린", "지루", "무겁", "어둡", "싫", "않", "말고", "not", "no"]):
        blocked_mood_tags.extend(["heavy", "late night"])
        has_avoidance = True

    if any(keyword in normalized for keyword in ["신나", "즐거", "밝아", "upbeat", "energetic"]):
        preferred_mood_tags.extend(["uplifting", "light"])
        blocked_mood_tags.extend(["heavy", "late night"])
        extra_keywords.extend(["upbeat music", "energetic playlist"])

    if any(keyword in normalized for keyword in ["차분", "잔잔", "조용", "calm", "quiet"]):
        preferred_mood_tags.extend(["soft", "quiet"])
        blocked_mood_tags.extend(["heavy"])
        extra_keywords.extend(["calm music", "quiet playlist"])

    if any(keyword in normalized for keyword in ["무겁", "어둡", "강한", "heavy", "dark"]):
        avoid_mood_tags.extend(["heavy", "late night"])
        blocked_mood_tags.extend(["heavy", "late night"])
        has_avoidance = True

    if any(keyword in normalized for keyword in ["지치", "피곤", "힘들", "우울", "슬프", "sad", "tired"]):
        preferred_mood_tags.extend(["soft", "warm"])
        extra_keywords.extend(["soft emotional music", "warm comfort music"])

    if any(keyword in normalized for keyword in ["싫", "말고", "별로", "않고", "안", "no", "not"]):
        has_negation = True

    if has_negation and any(keyword in normalized for keyword in ["우울", "슬프", "sad", "tired", "힘들", "지치"]):
        blocked_mood_tags.extend(["heavy", "late night"])
        preferred_mood_tags.extend(["uplifting", "light"])

    if any(keyword in normalized for keyword in ["한국", "국내", "korean"]):
        search_scope_hint = "korean"

    if any(keyword in normalized for keyword in ["전체", "글로벌", "global", "worldwide"]):
        search_scope_hint = "all"

    return RequestHints(
        emotion_text=emotion_text,
        request_text=request_text,
        negative_text=negative_text,
        preferred_mood_tags=_unique(preferred_mood_tags),
        avoid_mood_tags=_unique(avoid_mood_tags),
        blocked_mood_tags=_unique(blocked_mood_tags),
        extra_keywords=_unique(extra_keywords),
        request_keywords=_unique(request_keywords),
        search_scope_hint=search_scope_hint,
        has_avoidance=has_avoidance,
        has_negation=has_negation,
    )


def _merge_request_hints(primary: RequestHints, fallback: RequestHints) -> RequestHints:
    return RequestHints(
        emotion_text=primary.emotion_text or fallback.emotion_text,
        request_text=primary.request_text or fallback.request_text,
        negative_text=primary.negative_text or fallback.negative_text,
        request_keywords=_merge_unique(primary.request_keywords, fallback.request_keywords),
        preferred_mood_tags=_merge_unique(primary.preferred_mood_tags, fallback.preferred_mood_tags),
        avoid_mood_tags=_merge_unique(primary.avoid_mood_tags, fallback.avoid_mood_tags),
        blocked_mood_tags=_merge_unique(primary.blocked_mood_tags, fallback.blocked_mood_tags),
        extra_keywords=_merge_unique(primary.extra_keywords, fallback.extra_keywords),
        genre_hint=primary.genre_hint or fallback.genre_hint,
        search_scope_hint=primary.search_scope_hint or fallback.search_scope_hint,
        has_avoidance=primary.has_avoidance or fallback.has_avoidance,
        has_negation=primary.has_negation or fallback.has_negation,
    )


def _invoke_bedrock(text: str) -> RequestHints | None:
    if os.getenv("BEDROCK_ENABLED", "").lower() not in {"1", "true", "yes"}:
        return None

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-opus-4-7")
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "").strip()
    if not region or not api_key:
        return None

    system_prompt = (
        "You analyze a Korean music recommendation request. "
        "Split the input into emotion_text and request_text. "
        "emotion_text should describe the user's feeling only. "
        "request_text should describe the user's music request only. "
        "Split any negation or avoidance into negative_text. "
        "emotion_text should not include request or negative parts. "
        "Return only valid JSON with keys: emotion_text, request_text, negative_text, request_keywords, has_avoidance, has_negation, "
        "preferred_mood_tags, blocked_mood_tags, genre_hint, search_scope_hint. "
        "negative_text should include expressions the user wants to avoid. "
        "blocked_mood_tags should contain semantically similar tags that should be removed from recommendations. "
        "preferred_mood_tags should contain tags that better fit the request. "
        "request_keywords must be short search phrases extracted from request_text. "
        "genre_hint must be a short string or null. "
        "search_scope_hint must be all, korean, or null."
    )

    user_prompt = f"Text: {text}"

    endpoint = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/converse"
    payload = {
        "system": [{"text": system_prompt}],
        "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
        "inferenceConfig": {"maxTokens": 300, "temperature": 0},
    }

    try:
        response = requests.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    content = data.get("output", {}).get("message", {}).get("content", [])
    raw_text = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    payload = _parse_json_payload(raw_text)
    if payload is None:
        return None

    emotion_text = payload.get("emotion_text")
    request_text = payload.get("request_text")
    negative_text = payload.get("negative_text")

    return RequestHints(
        emotion_text=emotion_text.strip() if isinstance(emotion_text, str) and emotion_text.strip() else text,
        request_text=request_text.strip() if isinstance(request_text, str) and request_text.strip() else "",
        negative_text=negative_text.strip() if isinstance(negative_text, str) and negative_text.strip() else "",
        request_keywords=_normalize_keywords(payload.get("request_keywords")),
        preferred_mood_tags=_normalize_tags(payload.get("preferred_mood_tags")),
        avoid_mood_tags=_normalize_tags(payload.get("avoid_mood_tags")),
        blocked_mood_tags=_normalize_tags(payload.get("blocked_mood_tags")),
        extra_keywords=[],
        genre_hint=(
            payload.get("genre_hint").strip()
            if isinstance(payload.get("genre_hint"), str) and payload.get("genre_hint").strip()
            else None
        ),
        search_scope_hint=_normalize_scope(payload.get("search_scope_hint")),
        has_avoidance=bool(payload.get("has_avoidance")),
        has_negation=bool(payload.get("has_negation")),
    )


def load_request_hints(text: str) -> RequestHints:
    # Bedrock이 응답하면 그 결과를 쓰고, 로컬 규칙은 안전장치로 덧붙인다.
    bedrock_hints = _invoke_bedrock(text)
    local_hints = _build_local_request_hints(text)

    if bedrock_hints is not None:
        # 요청/부정 표현 분리는 로컬 규칙을 우선하고, Bedrock는 보강 정보만 얹는다.
        return _merge_request_hints(local_hints, bedrock_hints)

    return local_hints
