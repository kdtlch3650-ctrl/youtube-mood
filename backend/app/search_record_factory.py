from app.schemas import AnalyzeResponse, SearchRecord, SearchRecordItem


def _to_record_item(item: object) -> SearchRecordItem:
    return SearchRecordItem(
        id=getattr(item, "id"),
        title=getattr(item, "title"),
        channel_title=getattr(item, "channel_title"),
        url=getattr(item, "url"),
        thumbnail_url=getattr(item, "thumbnail_url"),
    )


def build_search_record(
    record_id: str,
    created_at: str,
    response: AnalyzeResponse,
    search_scope: str,
) -> SearchRecord:
    # OpenSearch 문서로 바로 옮길 수 있도록 기록 객체를 먼저 만든다.
    return SearchRecord(
        id=record_id,
        created_at=created_at,
        input_text=response.input_text,
        search_scope=search_scope,  # type: ignore[arg-type]
        emotions=response.emotions,
        mood_tags=response.mood_tags,
        genre=response.genre,
        search_keywords=response.search_keywords,
        recommended_tracks=[_to_record_item(item) for item in response.recommended_tracks],
        recommended_playlists=[_to_record_item(item) for item in response.recommended_playlists],
    )
