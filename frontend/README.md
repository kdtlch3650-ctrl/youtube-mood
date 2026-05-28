# Frontend

React와 TypeScript로 구현한 YouTube Mood Recommendation 클라이언트다.

## 역할

- 자연어 감정 입력 화면 제공
- 추천 결과 화면 표시
- 추천 곡과 플레이리스트 탭 전환
- 선택한 곡을 YouTube 플레이어와 연동
- 검색 옵션 선택
- 분위기/장르 키워드 표시

## 실행

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

브라우저 접속:

```text
http://127.0.0.1:5173
```

## 빌드 확인

```powershell
npm run build
```

## 백엔드 연결

프론트는 아래 백엔드 API를 호출한다.

```text
POST http://127.0.0.1:8000/api/analyze
GET  http://127.0.0.1:8000/api/playlists/{playlist_id}/tracks
```

프론트를 사용하려면 백엔드 서버가 `127.0.0.1:8000`에서 실행 중이어야 한다.
