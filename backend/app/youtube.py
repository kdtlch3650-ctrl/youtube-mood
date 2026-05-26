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
    items = search_youtube(f"{keyword} music", "video", 10)

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
    items = search_youtube(f"{keyword} playlist", "playlist", 10)

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
        RecommendationItem(
            id="track-5",
            title="Slow Morning Air",
            channel_title="Quiet Floor",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="느리게 기분을 정리하고 싶을 때 어울리는 곡입니다.",
        ),
        RecommendationItem(
            id="track-6",
            title="Muted City Lights",
            channel_title="After Hours",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="도시적인 밤 분위기와 차분함을 함께 느끼기 좋은 곡입니다.",
        ),
        RecommendationItem(
            id="track-7",
            title="Gentle Reset",
            channel_title="Mood Lab",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="무거운 감정을 조금 덜어내는 데 어울리는 곡입니다.",
        ),
        RecommendationItem(
            id="track-8",
            title="Soft Pulse",
            channel_title="Blue Window",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="잔잔하지만 너무 처지지 않는 리듬을 가진 곡입니다.",
        ),
        RecommendationItem(
            id="track-9",
            title="Clouded Mind",
            channel_title="Room Tone",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="복잡한 생각을 정리하며 듣기 좋은 분위기의 곡입니다.",
        ),
        RecommendationItem(
            id="track-10",
            title="Warm Exit",
            channel_title="Late Studio",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="하루를 부드럽게 마무리하기 좋은 곡입니다.",
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
        RecommendationItem(
            id="playlist-4",
            title="Soft focus rotation",
            channel_title="Calm Desk",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="차분하게 집중을 이어가기 좋은 플레이리스트입니다.",
        ),
        RecommendationItem(
            id="playlist-5",
            title="Not too sad night mix",
            channel_title="Night Archive",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="너무 무겁지 않은 밤 분위기의 플레이리스트입니다.",
        ),
        RecommendationItem(
            id="playlist-6",
            title="Gentle mood reset",
            channel_title="Mood Room",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="감정을 천천히 정리하기 좋은 곡들로 구성된 플레이리스트입니다.",
        ),
        RecommendationItem(
            id="playlist-7",
            title="Warm indie background",
            channel_title="Indie Shelf",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="따뜻한 배경음악처럼 듣기 좋은 플레이리스트입니다.",
        ),
        RecommendationItem(
            id="playlist-8",
            title="Low energy comfort",
            channel_title="Soft Channel",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="에너지가 낮은 날 부담 없이 듣기 좋은 플레이리스트입니다.",
        ),
        RecommendationItem(
            id="playlist-9",
            title="Late walk playlist",
            channel_title="Street Light",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="밤 산책 같은 분위기에 어울리는 플레이리스트입니다.",
        ),
        RecommendationItem(
            id="playlist-10",
            title="Calm electronic selection",
            channel_title="Electronic Mood",
            url="https://www.youtube.com/",
            thumbnail_url="",
            reason="잔잔한 전자음악 중심으로 이어지는 플레이리스트입니다.",
        ),
    ]
