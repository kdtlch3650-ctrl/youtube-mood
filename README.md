# YouTube Mood Recommendation

사용자가 자연어로 현재 감정이나 상황을 입력하면, AI 분석 결과를 바탕으로 어울리는 YouTube 음악과 플레이리스트를 추천하는 웹 애플리케이션이다.

핵심 목표는 단순히 `sad music`처럼 감정 단어 하나로 검색하는 것이 아니라, 복합 감정, 분위기 태그, 장르, 검색 범위를 조합해 추천 검색어를 만드는 것이다.

## 주요 기능

- 자연어 감정 입력
- AI 기반 감정 그룹 예측
- 분위기 태그 생성
- 장르 키워드 추출
- 회피 표현 반영
- YouTube 개별 곡 추천
- YouTube 플레이리스트 추천
- 전체 / 한국어 중심 검색 옵션
- YouTube 하단 플레이어 제어
- 추천 로직 확인용 테스트 스크립트

## 기술 스택

### Frontend

- React
- TypeScript
- Vite
- CSS

### Backend

- Python
- FastAPI
- YouTube Data API

### AI / ML

- PyTorch
- Transformers
- `klue/roberta-small`
- KOTE 감정 데이터 기반 학습

## 프로젝트 구조

```text
youtube-mood-recommendation/
  backend/   FastAPI API 서버
  frontend/  React 클라이언트
  ml/        모델 학습 및 평가 작업 공간
  docs/      기획, 설계, AI, 테스트, 트러블슈팅 문서
```

## 실행 방법

### 1. 백엔드 실행

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

상태 확인:

```text
http://127.0.0.1:8000/health
```

### 2. 프론트엔드 실행

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

브라우저에서 접속:

```text
http://127.0.0.1:5173
```

## 환경 변수

YouTube API 키는 `backend/.env`에 설정한다.

```env
YOUTUBE_API_KEY=발급받은_YouTube_API_키
```

`.env` 파일은 Git에 포함하지 않는다.

API 키가 없거나 YouTube 요청이 실패하면 백엔드는 fallback 추천 데이터를 반환한다.

## AI 모델 동작 방식

백엔드는 로컬에 학습된 모델이 있는지 확인한 뒤 사용할 모델을 정한다.

우선순위:

```text
1. ml/models/grouped-mood-roberta-small/
2. ml/models/mood-roberta-small/
3. 규칙 기반 fallback 모델
```

학습된 모델 파일은 GitHub에 포함하지 않는다.

모델 파일은 대용량 산출물이므로 로컬 또는 별도 저장소에서 관리한다.
저장소에는 학습 코드, 평가 코드, 모델 연결 방식, fallback 구조, 테스트 케이스를 남긴다.

자세한 내용은 [모델 산출물 관리](docs/15-model-artifact-management.md)에 정리되어 있다.

## 추천 로직

추천 흐름:

```text
사용자 문장
→ AI 감정 그룹 예측
→ 분위기 태그 생성
→ 장르 키워드 추출
→ 회피 표현 보정
→ 검색 옵션 반영
→ YouTube 검색어 생성
→ 곡 / 플레이리스트 추천
```

예시:

```text
입력: 오늘은 특히 너무 지쳐 신나는 댄스음악 추천해줘
검색 옵션: 한국어 중심
장르: dance
검색어: 따뜻한 댄스 음악
```

## 테스트

단위 테스트 확인:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

추천 로직 확인:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\check_recommendation_cases.py
```

현재 테스트 케이스:

```text
TOTAL: 16
PASS: 16
CHECK: 0
```

프론트엔드 빌드 확인:

```powershell
cd frontend
npm run build
```

## 주요 문서

- [프로젝트 기획](docs/01-project-plan.md)
- [사용자 요구사항](docs/02-user-requirements.md)
- [사용자 흐름](docs/03-user-flow.md)
- [API 설계](docs/07-api-draft.md)
- [개발 로그](docs/11-dev-log.md)
- [AI 서비스 연결](docs/12-ai-service-integration.md)
- [트러블슈팅](docs/13-troubleshooting.md)
- [추천 테스트 케이스](docs/14-recommendation-test-cases.md)
- [모델 산출물 관리](docs/15-model-artifact-management.md)

## 현재 한계

- YouTube 검색 결과는 외부 API 상태와 검색 시점에 따라 달라질 수 있다.
- 한국어 중심 옵션은 한국어 결과를 우선하도록 돕지만, 한국 곡만 반환하도록 보장하지는 않는다.
- 모델 파일은 Git에 포함되지 않으므로, 학습 모델 기반 실행을 위해서는 로컬 모델 배치가 필요하다.
- fallback 모델은 서비스 실행을 위한 안전장치이며, 학습 모델보다 표현 이해 범위가 좁다.
