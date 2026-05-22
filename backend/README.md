# Backend

FastAPI 기반 백엔드 API를 둘 폴더입니다.

현재 단계에서는 프론트엔드와 AI 분석 흐름을 연결할 API 구조만 준비합니다.

## 예정 역할

- 사용자 입력 문장 받기
- AI 분석 로직 호출
- 분석 결과를 검색 조건으로 변환
- YouTube API 요청 처리
- 프론트엔드에 추천 결과 전달

## 현재 파일 역할

- `app/main.py`: FastAPI 앱과 API 경로를 관리합니다.
- `app/config.py`: `.env` 파일에서 환경 변수를 읽습니다.
- `app/schemas.py`: 요청과 응답 데이터 구조를 정의합니다.
- `app/youtube.py`: YouTube 추천 데이터를 가져오는 역할을 담당합니다. API 호출이 실패하면 임시 데이터를 반환합니다.

## 실행 예시

Python 설치 후 아래 흐름으로 실행할 예정입니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## VS Code에서 실행

루트 폴더를 VS Code로 연 뒤 `Run and Debug`에서 `Backend: FastAPI`를 선택하면 백엔드 서버를 실행할 수 있습니다.

실행 전에 `8000`번 포트를 사용하는 기존 Python 서버가 있다면 종료해야 합니다.

## 환경 변수 설정

YouTube API 키는 코드에 직접 작성하지 않습니다.

백엔드 폴더에서 `.env.example` 파일을 참고해 `.env` 파일을 만들고 값을 채웁니다.

```env
YOUTUBE_API_KEY=발급받은_YouTube_API_키
```

`.env` 파일은 Git에 올리지 않습니다.

현재 백엔드는 `app/config.py`에서 `YOUTUBE_API_KEY` 값을 읽습니다. 값이 없거나 YouTube API 요청이 실패하면 임시 추천 데이터를 반환합니다.

## 현재 API

### `GET /health`

백엔드 서버가 실행 중인지 확인하는 API입니다.

응답 예시:

```json
{
  "status": "ok"
}
```

### `POST /api/analyze`

사용자가 입력한 문장을 받아 임시 감정 분석 결과를 반환하는 API입니다.

현재 감정 분석 결과는 임시 데이터입니다. 추천 음악과 플레이리스트는 YouTube API 검색 결과를 사용하고, 요청이 실패하면 임시 추천 데이터를 반환합니다.

요청 예시:

```json
{
  "text": "오늘은 지쳤는데 너무 우울한 노래는 듣고 싶지 않아"
}
```

응답 예시:

```json
{
  "input_text": "오늘은 지쳤는데 너무 우울한 노래는 듣고 싶지 않아",
  "emotions": ["tired", "calm"],
  "mood_tags": ["calm", "warm", "not too sad"],
  "search_keywords": [
    "calm warm music playlist",
    "soft relaxing music",
    "not too sad comfort music"
  ],
  "recommended_tracks": [
    {
      "id": "track-1",
      "title": "Soft Night Drive",
      "channel_title": "Mood Archive",
      "url": "https://www.youtube.com/",
      "thumbnail_url": "",
      "reason": "지친 기분을 가라앉히되 너무 무겁지 않은 분위기를 기준으로 고른 곡입니다."
    }
  ],
  "recommended_playlists": [
    {
      "id": "playlist-1",
      "title": "Calm but not sad playlist",
      "channel_title": "Daily Sound",
      "url": "https://www.youtube.com/",
      "thumbnail_url": "",
      "reason": "차분하지만 우울하게 가라앉지 않는 음악을 이어서 듣기 좋습니다."
    }
  ]
}
```
