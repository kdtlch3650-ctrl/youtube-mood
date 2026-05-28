from typing import Literal

import requests

from app.config import YOUTUBE_API_KEY
from app.schemas import PlaylistTrackItem, RecommendationItem

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
SearchScope = Literal["all", "korean"]

KOREAN_MOOD_SEARCH_PHRASES: dict[str, str] = {
    "soft": "부드러운",
    "quiet": "차분한",
    "warm": "따뜻한",
    "late night": "밤에 듣기 좋은",
    "heavy": "강렬한",
    "uplifting": "신나는",
    "light": "가볍게 듣는",
    "minimal": "집중할 때 듣는",
}

KOREAN_GENRE_NAMES: dict[str, str] = {
    "jazz": "재즈",
    "hiphop": "힙합",
    "lofi": "로파이",
    "rock": "록",
    "ballad": "발라드",
    "rnb": "알앤비",
    "pop": "팝",
    "classical": "클래식",
    "edm": "일렉트로닉",
    "acoustic": "어쿠스틱",
    "kpop": "케이팝",
    "citypop": "시티팝",
    "ambient": "앰비언트",
    "metal": "메탈",
    "reggae": "레게",
    "ost": "OST",
    "indie": "인디",
    "funk": "펑크",
    "soul": "소울",
    "blues": "블루스",
    "punk": "펑크 록",
    "house": "하우스",
    "techno": "테크노",
    "trap": "트랩",
    "dance": "댄스",
    "folk": "포크",
}


def has_youtube_api_key() -> bool:
    return bool(YOUTUBE_API_KEY)


def build_search_params(
    query: str,
    result_type: str,
    max_results: int,
    search_scope: SearchScope,
) -> dict[str, str | int]:
    params: dict[str, str | int] = {
        "part": "snippet",
        "q": query,
        "type": result_type,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }

    if search_scope == "korean":
        params["regionCode"] = "KR"
        params["relevanceLanguage"] = "ko"

    return params


def search_youtube(
    query: str,
    result_type: str,
    max_results: int,
    search_scope: SearchScope = "all",
) -> list[dict]:
    # API key가 없으면 외부 요청을 보내지 않고 fallback 데이터를 사용한다.
    if not has_youtube_api_key():
        return []

    try:
        response = requests.get(
            YOUTUBE_SEARCH_URL,
            params=build_search_params(query, result_type, max_results, search_scope),
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        # 네트워크 오류나 API 제한이 있으면 빈 결과를 돌려준다.
        return []

    data = response.json()
    return data.get("items", [])


def build_youtube_query(
    search_keywords: list[str],
    mood_tags: list[str],
    genre: str | None,
    search_scope: SearchScope,
    result_kind: Literal["music", "playlist"],
) -> str:
    if search_scope != "korean":
        keyword = search_keywords[0] if search_keywords else "calm warm music"
        if result_kind in keyword.lower():
            return keyword

        return f"{keyword} {result_kind}"

    korean_genre = KOREAN_GENRE_NAMES.get(genre or "", genre)
    mood_phrase = next(
        (
            KOREAN_MOOD_SEARCH_PHRASES[mood_tag]
            for mood_tag in mood_tags
            if mood_tag in KOREAN_MOOD_SEARCH_PHRASES
        ),
        "",
    )
    result_word = "플레이리스트" if result_kind == "playlist" else "음악"

    if korean_genre and mood_phrase:
        return f"{mood_phrase} {korean_genre} {result_word}"

    if korean_genre:
        return f"{korean_genre} {result_word}"

    if mood_phrase:
        return f"{mood_phrase} {result_word}"

    return "기분에 맞는 음악"


def search_playlist_tracks(playlist_id: str, max_results: int = 10) -> list[PlaylistTrackItem]:
    if not has_youtube_api_key() or not playlist_id:
        return []

    try:
        response = requests.get(
            YOUTUBE_PLAYLIST_ITEMS_URL,
            params={
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": max_results,
                "key": YOUTUBE_API_KEY,
            },
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    playlist_tracks: list[PlaylistTrackItem] = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        title = snippet.get("title")
        resource_id = snippet.get("resourceId", {})
        video_id = resource_id.get("videoId") or ""
        thumbnails = snippet.get("thumbnails", {})
        thumbnail = thumbnails.get("medium") or thumbnails.get("default") or {}

        if not title:
            continue

        playlist_tracks.append(
            PlaylistTrackItem(
                title=title,
                thumbnail_url=thumbnail.get("url", ""),
                url=f"https://www.youtube.com/watch?v={video_id}" if video_id else "https://www.youtube.com/",
                video_id=video_id,
            )
        )

    return playlist_tracks


def fallback_playlist_tracks(label: str) -> list[PlaylistTrackItem]:
    base_label = label or "playlist"
    return [
        PlaylistTrackItem(
            title=f"{base_label} track 1",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 2",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 3",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 4",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 5",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 6",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 7",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 8",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 9",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
        PlaylistTrackItem(
            title=f"{base_label} track 10",
            thumbnail_url="",
            url="https://www.youtube.com/",
            video_id="",
        ),
    ]


def convert_youtube_item(item: dict, result_type: str, reason: str) -> RecommendationItem:
    snippet = item.get("snippet", {})
    item_id = item.get("id", {})
    # search API response has different id field names for video and playlist results.
    youtube_id = item_id.get("videoId") if result_type == "video" else item_id.get("playlistId")
    url_path = "watch?v=" if result_type == "video" else "playlist?list="
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = thumbnails.get("medium") or thumbnails.get("default") or {}

    return RecommendationItem(
        id=youtube_id or "",
        title=snippet.get("title", "Untitled"),
        channel_title=snippet.get("channelTitle", "Unknown channel"),
        url=f"https://www.youtube.com/{url_path}{youtube_id}" if youtube_id else "https://www.youtube.com/",
        thumbnail_url=thumbnail.get("url", ""),
        reason=reason,
        playlist_tracks=[],
    )


def enrich_playlist_tracks(items: list[RecommendationItem]) -> list[RecommendationItem]:
    return [
        item.model_copy(
            update={
                "playlist_tracks": search_playlist_tracks(item.id) or fallback_playlist_tracks(item.title)
            }
        )
        for item in items
    ]


def get_playlist_tracks(playlist_id: str, title: str = "") -> list[PlaylistTrackItem]:
    # 결과 페이지 진입을 빠르게 하기 위해 플레이리스트 내부 곡은 선택된 항목만 따로 조회한다.
    return search_playlist_tracks(playlist_id) or fallback_playlist_tracks(title or playlist_id)


def get_recommended_tracks(
    search_keywords: list[str],
    mood_tags: list[str],
    genre: str | None,
    search_scope: SearchScope = "all",
) -> list[RecommendationItem]:
    query = build_youtube_query(search_keywords, mood_tags, genre, search_scope, "music")
    items = search_youtube(query, "video", 10, search_scope)

    if not items:
        return get_mock_recommended_tracks()

    return [
        convert_youtube_item(
            item,
            "video",
            "Matched to the current search.",
        )
        for item in items
    ]


def get_recommended_playlists(
    search_keywords: list[str],
    mood_tags: list[str],
    genre: str | None,
    search_scope: SearchScope = "all",
) -> list[RecommendationItem]:
    query = build_youtube_query(search_keywords, mood_tags, genre, search_scope, "playlist")
    items = search_youtube(query, "playlist", 10, search_scope)

    if not items:
        return get_mock_recommended_playlists()

    playlists = [
        convert_youtube_item(
            item,
            "playlist",
            "A playlist that matches the current mood.",
        )
        for item in items
    ]
    return playlists


def get_mock_recommended_tracks() -> list[RecommendationItem]:
    return [
        RecommendationItem(
            id="track-1",
            title="Soft Night Drive",
            channel_title="Mood Archive",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A calm track with a low-pressure atmosphere.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-2",
            title="Warm Static",
            channel_title="Night Room",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A mellow track that feels warm without becoming heavy.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-3",
            title="Blue Hour Walk",
            channel_title="Soft Studio",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A track that fits quiet evening walks.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-4",
            title="Low Light Focus",
            channel_title="Calm Project",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A steady track for focused but relaxed listening.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-5",
            title="Slow Morning Air",
            channel_title="Quiet Floor",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A track that feels light and unhurried.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-6",
            title="Muted City Lights",
            channel_title="After Hours",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A city-night atmosphere with a gentle tone.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-7",
            title="Gentle Reset",
            channel_title="Mood Lab",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A good fit for slowly resetting your mood.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-8",
            title="Soft Pulse",
            channel_title="Blue Window",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A soft rhythm that does not feel too heavy.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-9",
            title="Clouded Mind",
            channel_title="Room Tone",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A track for sorting out complex thoughts.",
            playlist_tracks=[],
        ),
        RecommendationItem(
            id="track-10",
            title="Warm Exit",
            channel_title="Late Studio",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A smooth way to close out the day.",
            playlist_tracks=[],
        ),
    ]


def get_mock_recommended_playlists() -> list[RecommendationItem]:
    playlists = [
        RecommendationItem(
            id="playlist-1",
            title="Calm but not sad playlist",
            channel_title="Daily Sound",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A playlist for staying light without becoming too gloomy.",
        ),
        RecommendationItem(
            id="playlist-2",
            title="Warm focus music",
            channel_title="Studio Room",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A playlist that helps you stay focused in a gentle way.",
        ),
        RecommendationItem(
            id="playlist-3",
            title="Late night comfort songs",
            channel_title="Playlist Garden",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A softer late-night playlist with a centered mood.",
        ),
        RecommendationItem(
            id="playlist-4",
            title="Soft focus rotation",
            channel_title="Calm Desk",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A playlist for quiet productivity.",
        ),
        RecommendationItem(
            id="playlist-5",
            title="Not too sad night mix",
            channel_title="Night Archive",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A night mix with a softer emotional tone.",
        ),
        RecommendationItem(
            id="playlist-6",
            title="Gentle mood reset",
            channel_title="Mood Room",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A playlist built for a slow mood reset.",
        ),
        RecommendationItem(
            id="playlist-7",
            title="Warm indie background",
            channel_title="Indie Shelf",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="Indie background music with a warm texture.",
        ),
        RecommendationItem(
            id="playlist-8",
            title="Low energy comfort",
            channel_title="Soft Channel",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="Comfort music for low-energy days.",
        ),
        RecommendationItem(
            id="playlist-9",
            title="Late walk playlist",
            channel_title="Street Light",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="A playlist that fits a quiet night walk.",
        ),
        RecommendationItem(
            id="playlist-10",
            title="Calm electronic selection",
            channel_title="Electronic Mood",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="Calm electronic music with a steady pulse.",
        ),
    ]

    # Mock playlist ids are not real YouTube playlist ids, so avoid external playlistItems calls.
    return [
        playlist.model_copy(update={"playlist_tracks": fallback_playlist_tracks(playlist.title)})
        for playlist in playlists
    ]
