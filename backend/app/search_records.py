from datetime import datetime, timezone
from itertools import count

from app.schemas import AnalyzeResponse, SearchRecord, SearchRecordItem

_record_sequence = count(1)
_search_records: list[SearchRecord] = []
_MAX_RECORDS = 100


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_record_item(item: object) -> SearchRecordItem:
    return SearchRecordItem(
        id=getattr(item, "id"),
        title=getattr(item, "title"),
        channel_title=getattr(item, "channel_title"),
        url=getattr(item, "url"),
        thumbnail_url=getattr(item, "thumbnail_url"),
    )


def create_search_record(response: AnalyzeResponse, search_scope: str) -> SearchRecord:
    record = SearchRecord(
        id=f"record-{next(_record_sequence)}",
        created_at=_now_iso(),
        input_text=response.input_text,
        search_scope=search_scope,  # type: ignore[arg-type]
        emotions=response.emotions,
        mood_tags=response.mood_tags,
        genre=response.genre,
        search_keywords=response.search_keywords,
        recommended_tracks=[_to_record_item(item) for item in response.recommended_tracks],
        recommended_playlists=[_to_record_item(item) for item in response.recommended_playlists],
    )

    _search_records.append(record)
    del _search_records[:-_MAX_RECORDS]
    return record


def list_search_records() -> list[SearchRecord]:
    return list(reversed(_search_records))
