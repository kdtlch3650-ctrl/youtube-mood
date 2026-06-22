# Docker 정리

이 문서는 `youtube-mood-recommendation` 프로젝트를 Docker로 실행하는 방법을 정리한 안내서다.

목표는 다음 두 가지다.

- 프론트와 백엔드를 같은 방식으로 실행하기
- 나중에 AWS나 Kubernetes로 옮길 때 재사용하기 쉬운 구조 만들기

## 현재 구성

- `backend`: FastAPI
- `frontend`: React + Vite + Nginx
- `ml`: 학습된 모델 파일 저장소

## 관련 파일

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.yml`
- `backend/.env.example`
- `frontend/.env.example`

## 실행 방식

### 1. 환경 파일 준비

```powershell
copy backend\.env.example backend\.env
```

`backend/.env`에는 최소한 아래 값이 들어 있어야 한다.

```env
YOUTUBE_API_KEY=...
AWS_REGION=ap-northeast-2
BEDROCK_ENABLED=true
BEDROCK_MODEL_ID=...
AWS_BEARER_TOKEN_BEDROCK=...
```

### 2. 컨테이너 실행

```powershell
docker compose up --build
```

### 3. 접속 주소

- 프론트: `http://127.0.0.1:5173`
- 백엔드: `http://127.0.0.1:8000`

### 4. 종료

```powershell
docker compose down
```

## 정리한 점

- 백엔드는 `backend/.env`를 읽는다.
- 모델 파일은 루트의 `ml/models`를 읽는다.
- 프론트는 빌드 시점에 API 주소를 넣고, Nginx가 정적 파일을 제공한다.
- 백엔드 헬스 체크가 살아 있어야 프론트가 먼저 뜨지 않는다.

## 참고

- Docker 실행이 안 되면 Docker Desktop과 WSL 상태를 먼저 확인한다.
- YouTube API가 없으면 추천 데이터가 mock으로 내려온다.
- `.env` 파일은 Git에 올리지 않는다.
