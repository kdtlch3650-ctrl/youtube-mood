# OpenSearch 연결 초안

이 문서는 검색 기록 객체를 OpenSearch에 연결하기 위한 구조 초안이다.

## 목표

- 현재 메모리 저장 방식을 나중에 OpenSearch로 바꾸기
- API 구조는 최대한 유지하기
- 저장 코드는 한 곳에서만 바꾸기

## 지금 구조

- `build_search_record(...)`
  - 분석 결과를 검색 기록 객체로 만든다
- `save_search_record(...)`
  - 검색 기록 객체를 저장한다
- `list_search_records()`
  - 저장된 기록을 조회한다

이 구조 덕분에 저장소만 바꾸면 된다.

## OpenSearch로 바뀔 부분

### 저장

현재:

- 메모리 리스트에 저장

나중:

- OpenSearch 인덱스에 문서로 저장

### 조회

현재:

- 메모리 리스트를 역순으로 반환

나중:

- OpenSearch에서 최신순 검색
- 필요하면 감정/장르/태그로 필터링

## 파일 역할 초안

### `backend/app/search_record_factory.py`

- 분석 결과를 기록 객체로 만드는 역할
- OpenSearch 문서 형태와 가장 가까운 데이터 생성

### `backend/app/search_record_store.py`

- 저장소 역할
- 지금은 메모리
- 나중에는 OpenSearch로 교체

### `backend/app/main.py`

- API 요청을 받아서
- 기록 객체를 만들고
- 저장소에 넘기는 역할

## 나중에 필요한 설정값

OpenSearch를 실제로 붙일 때는 보통 아래 값이 필요하다.

- `OPENSEARCH_ENDPOINT`
- `OPENSEARCH_INDEX_NAME`
- `OPENSEARCH_USERNAME` 또는 IAM 인증 설정
- `OPENSEARCH_PASSWORD`

## 연결 흐름 초안

```text
사용자 입력
→ AI 분석
→ 추천 결과 생성
→ SearchRecord 객체 생성
→ SearchRecord 저장
→ OpenSearch 문서 인덱싱
```

## 주의할 점

- 아직은 저장 구조만 분리한 상태다
- OpenSearch 클라이언트는 별도 승인 후 추가하는 편이 안전하다
- 저장소를 바꿔도 API 응답 형식은 유지한다

## 다음 단계

1. OpenSearch 클라이언트 추가 여부 결정
2. 환경변수 초안 정리
3. 저장소 구현을 OpenSearch용으로 교체

