# OpenSearch 기록 객체 초안

이 문서는 나중에 OpenSearch로 바로 넣기 위한 검색 기록 객체 구조를 정리한 문서다.

## 목적

- 추천 결과를 한 번의 검색 단위로 묶기
- 나중에 OpenSearch에 그대로 인덱싱하기
- 이전 검색 기록을 다시 보기 쉽게 만들기

## 현재 방식

- `/api/analyze` 요청이 들어오면
- 분석과 추천이 끝난 뒤
- 검색 기록 객체를 서버 메모리에 바로 생성한다

이 객체는 나중에 OpenSearch 문서로 그대로 바꿀 수 있게 설계한다.

## 기록 객체 필드

- `id`
- `created_at`
- `input_text`
- `search_scope`
- `emotions`
- `mood_tags`
- `genre`
- `search_keywords`
- `recommended_tracks`
- `recommended_playlists`

## 저장되는 정보

예시:

```json
{
  "id": "record-1",
  "created_at": "2026-06-16T12:00:00Z",
  "input_text": "오늘은 너무 지쳤지만 너무 무거운 음악은 싫어",
  "search_scope": "all",
  "emotions": ["tired", "calm"],
  "mood_tags": ["soft", "warm", "light"],
  "genre": "dance",
  "search_keywords": ["soft warm dance music"],
  "recommended_tracks": [],
  "recommended_playlists": []
}
```

## 현재 API

- `POST /api/analyze`
- `GET /api/search-records`

## 나중에 OpenSearch로 옮길 때

- 저장 위치만 OpenSearch로 바꾼다
- JSON 구조는 그대로 둔다
- API 모양도 크게 바꾸지 않는다

