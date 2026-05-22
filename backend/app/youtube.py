import requests

from app.config import YOUTUBE_API_KEY
from app.schemas import RecommendationItem

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def has_youtube_api_key() -> bool:
    return bool(YOUTUBE_API_KEY)


def search_youtube(query: str, result_type: str, max_results: int) -> list[dict]:
    # API 키가 없으면 외부 요청을 보내지 않고 fallback 데이터를 사용한다.
    if not has_youtube_api_key():
        return []

    try:
        response = requests.get(
            YOUTUBE_SEARCH_URL,
            params={
                "part": "snippet",
                "q": query,
                "type": result_type,
                "maxResults": max_results,
                "key": YOUTUBE_API_KEY,
            },
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        # 키 오류, 할당량 초과, 네트워크 문제로 추천 흐름 전체가 깨지지 않게 한다.
        return []

    data = response.json()
    return data.get("items", [])


def convert_youtube_item(item: dict, result_type: str, reason: str) -> RecommendationItem:
    snippet = item.get("snippet", {})
    item_id = item.get("id", {})
    # YouTube 검색 응답은 video와 playlist의 id 필드 이름이 다르다.
    youtube_id = item_id.get("videoId") if result_type == "video" else item_id.get("playlistId")
    url_path = "watch?v=" if result_type == "video" else "playlist?list="
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = thumbnails.get("medium") or thumbnails.get("default") or {}

    return RecommendationItem(
        id=youtube_id or "",
        title=snippet.get("title", "제목 없음"),
        channel_title=snippet.get("channelTitle", "채널 정보 없음"),
        url=f"https://www.youtube.com/{url_path}{youtube_id}" if youtube_id else "https://www.youtube.com/",
        thumbnail_url=thumbnail.get("url", ""),
        reason=reason,
    )


def get_recommended_tracks(search_keywords: list[str]) -> list[RecommendationItem]:
    keyword = search_keywords[0] if search_keywords else "calm warm music"
    items = search_youtube(f"{keyword} music", "video", 5)

    # 검색 결과가 없으면 화면 확인이 가능하도록 임시 추천 곡 목록을 반환한다.
    if not items:
        return get_mock_recommended_tracks()

    return [
        convert_youtube_item(
            item,
            "video",
            "분석된 분위기와 가까운 음악 검색 결과입니다.",
        )
        for item in items
    ]


def get_recommended_playlists(search_keywords: list[str]) -> list[RecommendationItem]:
    keyword = search_keywords[0] if search_keywords else "calm warm music"
    items = search_youtube(f"{keyword} playlist", "playlist", 3)

    # 검색 결과가 없으면 화면 확인이 가능하도록 임시 플레이리스트를 반환한다.
    if not items:
        return get_mock_recommended_playlists()

    return [
        convert_youtube_item(
            item,
            "playlist",
            "분석된 분위기를 이어서 듣기 좋은 플레이리스트 검색 결과입니다.",
        )
        for item in items
    ]


def get_mock_recommended_tracks() -> list[RecommendationItem]:
    return [
        RecommendationItem(
            id="track-1",
            title="Soft Night Drive",
            channel_title="Mood Archive",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="지친 기분을 가라앉히되 너무 무겁지 않은 분위기를 기준으로 고른 곡입니다.",
        ),
        RecommendationItem(
            id="track-2",
            title="Warm Static",
            channel_title="Night Room",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="차분하지만 너무 가라앉지 않는 분위기를 이어가기 좋은 곡입니다.",
        ),
        RecommendationItem(
            id="track-3",
            title="Blue Hour Walk",
            channel_title="Soft Studio",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="늦은 시간에 부담 없이 들을 수 있는 부드러운 곡입니다.",
        ),
        RecommendationItem(
            id="track-4",
            title="Low Light Focus",
            channel_title="Calm Project",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="집중과 휴식 사이의 분위기를 유지하기 좋은 곡입니다.",
        ),
    ]


def get_mock_recommended_playlists() -> list[RecommendationItem]:
    return [
        RecommendationItem(
            id="playlist-1",
            title="Calm but not sad playlist",
            channel_title="Daily Sound",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="차분하지만 우울하게 가라앉지 않는 음악을 이어서 듣기 좋습니다.",
        ),
        RecommendationItem(
            id="playlist-2",
            title="Warm focus music",
            channel_title="Studio Room",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="집중이 필요하면서도 편안한 분위기를 유지하고 싶을 때 어울립니다.",
        ),
        RecommendationItem(
            id="playlist-3",
            title="Late night comfort songs",
            channel_title="Playlist Garden",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="밤에 듣기 좋은 부드러운 곡 중심으로 이어지는 플레이리스트입니다.",
        ),
    ]
