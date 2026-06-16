# OpenSearch 인덱스 초안

이 문서는 검색 기록 객체를 OpenSearch에 저장하기 위한 필드 구조와 매핑 기준을 정리한 초안이다.

## 목적

- 검색 기록을 OpenSearch에 저장하기
- 이전 검색을 다시 찾기
- 감정, 분위기, 장르로 필터링하기
- 나중에 인기 검색어나 자주 나온 감정을 집계하기

## 인덱스 이름 초안

```text
search-records
```

## 저장할 필드

| 필드 | 용도 | 타입 초안 |
| --- | --- | --- |
| `id` | 기록 고유 ID | `keyword` |
| `created_at` | 생성 시각 | `date` |
| `input_text` | 사용자가 입력한 문장 | `text` |
| `search_scope` | 전체/한국어 중심 여부 | `keyword` |
| `emotions` | AI가 뽑은 감정 목록 | `keyword` |
| `mood_tags` | 분위기 태그 | `keyword` |
| `genre` | 추출된 장르 | `keyword` |
| `search_keywords` | YouTube 검색어 목록 | `text` |
| `recommended_tracks` | 추천 곡 목록 | `nested` |
| `recommended_playlists` | 추천 플레이리스트 목록 | `nested` |

## nested로 둘 필드

추천 결과는 객체 배열이므로 `nested`로 두는 것이 자연스럽다.

### `recommended_tracks`

- `id`
- `title`
- `channel_title`
- `url`
- `thumbnail_url`

### `recommended_playlists`

- `id`
- `title`
- `channel_title`
- `url`
- `thumbnail_url`

## 매핑 기준

### `keyword`

- 정확히 같은 값끼리 비교할 때 사용
- 필터, 집계, 정렬 기준에 적합

### `text`

- 입력 문장이나 검색어처럼 부분 검색이 필요한 필드에 사용

### `date`

- 생성 시각 저장용

### `nested`

- 추천 결과처럼 여러 속성을 가진 배열에 사용
- 특정 곡의 `title`과 `url`을 같이 찾을 수 있게 해줌

## 예상 문서 예시

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
  "recommended_tracks": [
    {
      "id": "track-1",
      "title": "Soft Night Drive",
      "channel_title": "Mood Archive",
      "url": "https://www.youtube.com/",
      "thumbnail_url": ""
    }
  ],
  "recommended_playlists": [
    {
      "id": "playlist-1",
      "title": "Calm but not sad playlist",
      "channel_title": "Daily Sound",
      "url": "https://www.youtube.com/",
      "thumbnail_url": ""
    }
  ]
}
```

## 다음 단계

1. 현재 `SearchRecord`를 이 문서 구조에 맞게 유지한다
2. OpenSearch 클라이언트를 붙이면 이 문서를 그대로 인덱싱한다
3. 기록 조회 API는 유지하고 저장소만 교체한다

