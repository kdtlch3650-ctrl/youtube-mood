from app.config import YOUTUBE_API_KEY
from app.schemas import RecommendationItem


def has_youtube_api_key() -> bool:
    return bool(YOUTUBE_API_KEY)


def get_mock_recommended_track() -> RecommendationItem:
    return RecommendationItem(
        id="track-1",
        title="Soft Night Drive",
        channel_title="Mood Archive",
        url="https://www.youtube.com/",
        thumbnail_url="",
        reason="지친 기분을 가라앉히되 너무 무겁지 않은 분위기를 기준으로 고른 곡입니다.",
    )


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
