from typing import Protocol

from app.schemas import SearchRecord


class SearchRecordRepository(Protocol):
    def save(self, record: SearchRecord) -> SearchRecord:
        ...

    def list(self, user_id: str | None = None) -> list[SearchRecord]:
        ...


class InMemorySearchRecordRepository:
    def __init__(self, max_records: int = 100) -> None:
        self._records: list[SearchRecord] = []
        self._max_records = max_records

    def save(self, record: SearchRecord) -> SearchRecord:
        # 현재는 메모리에 저장하고, 나중에 OpenSearch 저장소로 교체한다.
        self._records.append(record)
        del self._records[:-self._max_records]
        return record

    def list(self, user_id: str | None = None) -> list[SearchRecord]:
        records = reversed(self._records)
        if user_id is None:
            return list(records)

        return [record for record in records if record.user_id == user_id]


_repository: SearchRecordRepository = InMemorySearchRecordRepository()


def save_search_record(record: SearchRecord) -> SearchRecord:
    return _repository.save(record)


def list_search_records(user_id: str | None = None) -> list[SearchRecord]:
    return _repository.list(user_id)
