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
