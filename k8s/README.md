# Kubernetes 초안

이 폴더는 이 프로젝트를 나중에 Kubernetes로 옮길 때 사용할 배포 설정 초안이다.

지금 단계에서는 실제 클러스터 배포보다, 파일 역할과 배치 순서를 먼저 정리한다.

## 목표

- 프론트와 백엔드를 Kubernetes용 설정으로 분리한다
- 로컬 `kind` 또는 `minikube`에서 먼저 검증할 수 있게 만든다
- 나중에 EKS로 옮겨도 파일을 크게 바꾸지 않도록 한다

## 폴더 구조

```text
k8s/
  README.md
  namespace.yaml
  configmap.yaml
  secret.example.yaml

  backend/
    deployment.yaml
    service.yaml

  frontend/
    deployment.yaml
    service.yaml

  ingress/
    ingress.yaml

  local/
    kind-notes.md
```

## 파일 역할

### `namespace.yaml`

- 이 프로젝트 전용 작업 공간을 분리한다
- 처음에는 없어도 되지만, 있으면 자원 관리가 편하다

### `configmap.yaml`

- 일반 설정값을 넣는다
- 예: API 주소, 실행 모드, 기본 옵션

### `secret.example.yaml`

- 민감 정보 예시를 적어둔다
- 실제 값은 별도 파일이나 환경변수로 관리한다

### `backend/deployment.yaml`

- 백엔드 컨테이너를 몇 개 띄울지 정한다
- 이미지 이름, 포트, 환경변수를 여기에 적는다

### `backend/service.yaml`

- 백엔드 내부 접속 주소를 고정한다
- 프론트가 백엔드를 찾을 때 사용한다

### `frontend/deployment.yaml`

- 프론트 컨테이너를 어떻게 띄울지 정한다

### `frontend/service.yaml`

- 브라우저가 접근할 프론트 서비스 주소를 만든다

### `ingress/ingress.yaml`

- 외부 요청을 프론트와 백엔드로 나눈다
- 나중에 도메인을 붙일 때 핵심이 된다

### `local/kind-notes.md`

- 로컬 Kubernetes에서 확인할 때 필요한 메모를 적는다
- `kind` 또는 `minikube` 기준으로 쓴다

## 작업 순서

1. `namespace.yaml`, `configmap.yaml`, `secret.example.yaml` 준비
2. `backend`와 `frontend`의 `deployment`, `service` 작성
3. `ingress`로 `/`와 `/api` 연결
4. 로컬 Kubernetes에서 통신 확인
5. 마지막에 EKS 연결

## 프론트 주의점

- Kubernetes에서는 브라우저가 클러스터 내부 주소를 직접 못 본다
- 그래서 프론트는 가능하면 같은 도메인에서 `/api`로 백엔드에 붙는 방식이 좋다
- 현재 프론트는 빌드 시점 `VITE_API_BASE_URL`을 쓰므로, Kubernetes용 이미지는 `/api` 기준으로 빌드하는 흐름이 필요하다

## 주의할 점

- 실제 비밀 값은 Git에 넣지 않는다
- 처음부터 EKS에 붙이지 않는다
- Docker 실행이 안정된 뒤에 Kubernetes로 옮긴다

## 로컬 확인 순서

1. `kind` 클러스터 생성
2. 필요한 Docker 이미지 빌드
3. `kind load docker-image`로 이미지 주입
4. `kubectl apply`로 k8s 파일 적용
5. `kubectl get pods`, `kubectl get svc`, `kubectl get ingress`로 상태 확인

## 실제 적용 팁

- `secret.example.yaml`은 예시만 남긴다
- 실제 `secret.yaml`은 로컬에서 생성해서 적용한다
- `k8s/local/create-secret.ps1`는 `backend/.env`를 읽어서 `k8s/secret.yaml`을 만든다
- 로컬 테스트가 끝난 뒤에야 EKS로 옮긴다
- `k8s/local/setup-kind.ps1`는 위 과정을 한 번에 실행하고, secret이 없으면 먼저 만든다
- 브라우저 확인은 `k8s/local/forward-frontend.ps1`로 프론트 포트포워딩을 띄우면 된다
