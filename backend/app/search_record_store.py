from app.schemas import SearchRecord

_search_records: list[SearchRecord] = []
_MAX_RECORDS = 100


def save_search_record(record: SearchRecord) -> SearchRecord:
    # 현재는 메모리에 저장하고, 나중에 OpenSearch 저장으로 교체한다.
    _search_records.append(record)
    del _search_records[:-_MAX_RECORDS]
    return record


def list_search_records() -> list[SearchRecord]:
    return list(reversed(_search_records))
