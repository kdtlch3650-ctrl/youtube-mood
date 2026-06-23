# kind 테스트 메모

로컬 Kubernetes에서 확인할 때는 다음 순서로 본다.

1. namespace 적용
2. configmap, secret 적용
3. backend deployment, service 적용
4. frontend deployment, service 적용
5. ingress 적용

## 기본 명령 순서

```powershell
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

## 이미지 준비 메모

- `backend`와 `frontend` 이미지는 먼저 로컬에서 빌드해야 한다
- `kind`는 로컬 이미지가 클러스터에서 보이도록 `kind load docker-image`를 쓸 수 있다
- 이 단계에서는 `EKS`보다 로컬 확인이 먼저다

## 확인 포인트

- backend 서비스가 `/health`에 응답하는지 확인
- frontend가 `/api`로 백엔드에 접근하는지 확인
- 브라우저에서 같은 주소로 화면과 API가 함께 동작하는지 확인
