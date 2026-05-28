# API 설계 초안

## 1. 문서 목적

이 문서는 AI 분석 결과와 YouTube 추천 결과를 어떻게 주고받을지 정리한다.

이 프로젝트의 API는 다음 두 역할을 맡는다.

- 사용자의 자연어 입력을 AI 분석기에 전달한다.
- AI 결과를 바탕으로 YouTube 추천 데이터를 반환한다.

## 2. 전체 흐름

1. 사용자가 문장을 입력한다.
2. 프론트엔드가 `POST /api/analyze`를 호출한다.
3. 백엔드가 AI 모델에 문장을 전달한다.
4. AI가 감정과 분위기를 추론한다.
5. 백엔드가 검색 키워드를 정리한다.
6. YouTube 추천 결과를 생성한다.
7. 프론트엔드가 결과를 화면에 표시한다.

## 3. 현재 API 상태

현재는 백엔드에서 목업 응답을 반환한다.

즉,

- API 경로는 이미 존재한다.
- 응답 구조도 정해져 있다.
- 다만 실제 AI 모델 호출만 아직 연결되지 않았다.

## 4. 요청과 응답

### `POST /api/analyze`

#### 요청

```json
{
  "text": "지쳤지만 너무 무거운 음악은 싫고, 조금 차분한 분위기가 좋다",
  "search_scope": "all"
}
```

#### 응답

```json
{
  "input_text": "지쳤지만 너무 무거운 음악은 싫고, 조금 차분한 분위기가 좋다",
  "emotions": ["tired", "calm"],
  "mood_tags": ["soft", "quiet"],
  "search_keywords": [
    "calm soft music",
    "tired quiet playlist",
    "soft relaxing music"
  ],
  "recommended_tracks": [
    {
      "id": "track-1",
      "title": "Soft Night Drive",
      "channel_title": "Mood Archive",
      "url": "https://www.youtube.com/",
      "thumbnail_url": "",
      "reason": "차분하고 부드러운 분위기에 맞는 곡"
    }
  ],
  "recommended_playlists": [
    {
      "id": "playlist-1",
      "title": "Calm but not sad playlist",
      "channel_title": "Daily Sound",
      "url": "https://www.youtube.com/",
      "thumbnail_url": "",
      "reason": "너무 무겁지 않은 차분한 플레이리스트"
    }
  ]
}
```

## 5. 응답 필드 설명

### `input_text`

- 사용자가 입력한 원문

### `emotions`

- AI가 판단한 감정 태그
- 복합 감정이면 여러 개가 들어갈 수 있다

### `mood_tags`

- 음악 분위기 태그
- 추천 화면의 Keywords 영역에 표시할 값

### `search_scope`

- YouTube 검색 범위를 조정하는 요청 옵션
- `all`: 전체 검색
- `korean`: 한국어 중심 검색
- 감정 분석 결과를 바꾸는 값이 아니라 YouTube 검색 옵션만 조정한다

### `search_keywords`

- YouTube 검색에 사용할 키워드
- 감정 태그와 분위기 태그를 조합해서 생성한다

### `recommended_tracks`

- 개별 곡 추천 목록
- 프론트의 `Popular` 카드와 하단 플레이바가 이 값을 사용한다

### `recommended_playlists`

- 플레이리스트 추천 목록
- 각 항목은 내부 곡 목록을 포함할 수 있다

## 6. 데이터 구조

### 추천 항목

추천 곡과 추천 플레이리스트는 같은 구조를 기본으로 사용한다.

```json
{
  "id": "string",
  "title": "string",
  "channel_title": "string",
  "url": "string",
  "thumbnail_url": "string",
  "reason": "string"
}
```

### 플레이리스트 곡 항목

플레이리스트는 내부 곡 리스트를 따로 가진다.

```json
{
  "title": "string",
  "thumbnail_url": "string",
  "url": "string",
  "video_id": "string"
}
```

## 7. 백엔드 처리 원칙

### 감정과 분위기 분리

- 감정은 사용자 상태를 설명한다.
- 분위기는 음악 선택을 설명한다.

### 검색어 생성

- AI가 직접 검색어를 만들 수 있다.
- 하지만 1차 버전은 백엔드가 감정과 분위기를 조합해 만드는 편이 안정적이다.

### 추천 결과 생성

- 감정과 분위기 태그를 기반으로 YouTube 검색 키워드를 만든다.
- 그 키워드로 곡과 플레이리스트를 찾는다.
- 결과를 정리해서 한 번에 돌려준다.

## 8. 현재 구현과 앞으로의 연결

현재 백엔드는 목업 분석 함수를 사용한다.

앞으로는 아래 순서로 바뀐다.

1. 사용자의 입력 문장을 받는다.
2. AI 모델에 전달한다.
3. AI 결과를 정리한다.
4. YouTube 추천 결과를 만든다.
5. 프론트에 전달한다.

## 9. 확인해야 할 점

- 응답에 감정과 분위기를 어디까지 보여줄지
- 추천 곡과 플레이리스트를 각각 몇 개까지 보여줄지
- 플레이리스트 내부 곡 목록을 몇 개까지 포함할지
- AI가 검색어를 만들지, 백엔드가 만들지
