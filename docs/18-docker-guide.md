# Docker 정리 초안

이 문서는 `youtube-mood-recommendation` 프로젝트를 Docker 기반으로 정리하기 위한 기준을 적어둔 문서다.

## 목적

- 프론트엔드와 백엔드를 같은 방식으로 실행하기
- 나중에 쿠버네티스로 옮기기 쉬운 구조 만들기
- 로컬 실행과 배포 준비를 분리하기

## 현재 구성

- `frontend`: React + Vite
- `backend`: FastAPI
- `ml`: 모델 파일과 학습 관련 스크립트

## 추가한 파일

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.yml`
- `backend/.env.example`
- `frontend/.env.example`

## 실행 방식

### 백엔드

- Python 3.12 기반 이미지 사용
- `uvicorn`으로 FastAPI 실행
- `YOUTUBE_API_KEY`는 환경변수로 주입

### 프론트엔드

- Vite로 정적 빌드
- 빌드 결과물을 Nginx로 제공
- API 주소는 `VITE_API_BASE_URL`로 분리

## 로컬 실행 예시

```powershell
copy backend\.env.example backend\.env
```

프론트엔드는 빌드 인자로 API 주소를 주입하므로, Docker 실행용으로는 별도 `.env`가 없어도 된다.

```powershell
docker compose up --build
```

## 접속 주소

- 프론트엔드: `http://127.0.0.1:5173`
- 백엔드: `http://127.0.0.1:8000`

## 종료 방법

```powershell
docker compose down
```

## 주의할 점

- 모델 파일은 Git에 올리지 않는다
- Docker 이미지에 모델을 직접 넣지 않고, 필요하면 볼륨으로 연결한다
- 쿠버네티스는 나중 단계에서 추가한다
- 프론트엔드는 빌드 시점의 `VITE_API_BASE_URL`을 사용하므로, 주소를 바꾸면 다시 빌드해야 한다
