# kind 테스트 메모

로컬 Kubernetes에서 확인할 때는 다음 순서로 본다.

1. namespace 적용
2. configmap, secret 적용
3. backend deployment, service 적용
4. frontend deployment, service 적용
5. ingress 적용

## 기본 명령 순서

### 한 번에 실행

```powershell
.\k8s\local\setup-kind.ps1
```

- 이 스크립트는 `k8s/secret.yaml`이 없으면 `backend/.env`를 읽어서 먼저 만든다

### 직접 실행

```powershell
kind create cluster --name youtube-mood

docker build -t youtube-mood-backend:latest .\backend
docker build -t youtube-mood-frontend:latest .\frontend

kind load docker-image youtube-mood-backend:latest --name youtube-mood
kind load docker-image youtube-mood-frontend:latest --name youtube-mood

kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\configmap.yaml
kubectl apply -f k8s\secret.yaml
kubectl apply -f k8s\backend\deployment.yaml
kubectl apply -f k8s\backend\service.yaml
kubectl apply -f k8s\frontend\deployment.yaml
kubectl apply -f k8s\frontend\service.yaml
kubectl apply -f k8s\ingress\ingress.yaml
```

## 확인 명령

```powershell
kubectl get pods -n youtube-mood
kubectl get svc -n youtube-mood
kubectl get ingress -n youtube-mood
kubectl describe pod -n youtube-mood
kubectl logs -n youtube-mood deploy/youtube-mood-backend
```

## 브라우저 확인

`kind`에서 외부 브라우저로 바로 보려면 프론트 서비스에 포트포워딩을 건다.

```powershell
.\k8s\local\forward-frontend.ps1
```

- 브라우저 주소: `http://127.0.0.1:8080`
- 프론트 Nginx가 `/api/` 요청을 백엔드 서비스로 넘긴다

## 이미지 준비 메모

- `backend`와 `frontend` 이미지는 먼저 로컬에서 빌드해야 한다
- `kind`는 로컬 이미지가 클러스터에서 보이도록 `kind load docker-image`를 쓸 수 있다
- 이 단계에서는 `EKS`보다 로컬 확인이 먼저다
- 이미지 이름은 매니페스트의 `image:` 값과 같게 맞추는 편이 헷갈리지 않는다
- 예: `youtube-mood-backend:latest`, `youtube-mood-frontend:latest`
- 스크립트는 위 명령을 순서대로 실행한 버전이다

## 정리 명령

```powershell
kubectl delete -f k8s\ingress\ingress.yaml
kubectl delete -f k8s\frontend\service.yaml
kubectl delete -f k8s\frontend\deployment.yaml
kubectl delete -f k8s\backend\service.yaml
kubectl delete -f k8s\backend\deployment.yaml
kubectl delete -f k8s\secret.yaml
kubectl delete -f k8s\configmap.yaml
kubectl delete -f k8s\namespace.yaml
kind delete cluster --name youtube-mood
```

## Secret 준비 메모

- `k8s/secret.example.yaml`은 예시용이다
- 실제 `k8s/secret.yaml`은 로컬에서 직접 만들어 적용한다
- `k8s/local/create-secret.ps1`를 쓰면 `backend/.env`에서 Secret YAML을 생성할 수 있다
- 예:

```powershell
.\k8s\local\create-secret.ps1
```

## 확인 포인트

- backend 서비스가 `/health`에 응답하는지 확인
- frontend가 `/api`로 백엔드에 접근하는지 확인
- 브라우저에서 같은 주소로 화면과 API가 함께 동작하는지 확인
