# Backend

FastAPI 기반 백엔드 API를 둘 폴더입니다.

현재 단계에서는 프론트엔드와 AI 분석 흐름을 연결할 API 구조만 준비합니다.

## 예정 역할

- 사용자 입력 문장 받기
- AI 분석 로직 호출
- 분석 결과를 검색 조건으로 변환
- YouTube API 요청 처리
- 프론트엔드에 추천 결과 전달

## 실행 예시

Python 설치 후 아래 흐름으로 실행할 예정입니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

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

현재는 실제 AI 모델이 아니라 고정된 예시 데이터를 반환합니다. 나중에 AI 모델을 연결할 때 이 API의 내부 로직을 교체할 예정입니다.

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
  ]
}
```
