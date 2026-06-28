# EKS 트러블슈팅

이 문서는 EKS 배포 중 자주 만날 수 있는 문제와 확인 순서를 정리한 초안이다.

## 1. AWS Load Balancer Controller가 설치되지 않는 문제

### 문제

`scripts/install-lbc.ps1` 실행 중 `helm install` 또는 `eksctl create iamserviceaccount` 단계에서 실패할 수 있다.

### 확인할 것

- AWS CLI 로그인 상태가 맞는가
- EKS 클러스터 이름이 실제 존재하는가
- `eksctl`, `helm`, `kubectl`이 설치되어 있는가
- IAM 정책을 만들 권한이 있는가

### 해결 방향

- `docs/30-eks-lbc-install.md`의 순서대로 다시 확인한다
- `docs/31-eks-lbc-install-script.md`의 계정 ID와 클러스터 이름을 다시 넣는다
- OIDC 연결이 끝났는지 확인한다

## 2. Ingress가 외부 주소를 받지 못하는 문제

### 문제

`kubectl get ingress -n youtube-mood`에서 ADDRESS가 비어 있을 수 있다.

### 확인할 것

- AWS Load Balancer Controller Pod가 Running 상태인가
- `IngressClass`가 `alb`로 적용되어 있는가
- `k8s/eks/ingress.yaml`이 EKS용으로 적용되었는가
- `k8s/eks/ingress-class.yaml`가 먼저 적용되었는가

### 해결 방향

- `docs/32-eks-runbook.md` 순서대로 다시 실행한다
- 컨트롤러 설치 후에 Ingress를 적용한다
- `kubectl get pods -n kube-system`으로 컨트롤러 상태를 확인한다

## 3. 백엔드가 헬스체크에 실패하는 문제

### 문제

백엔드 파드가 Running이지만 ALB 대상 그룹이 Unhealthy가 될 수 있다.

### 확인할 것

- 백엔드 경로가 `/health`인지 확인한다
- 백엔드 Service에 맞는 포트가 잡혀 있는지 확인한다
- `k8s/backend/service.yaml`의 헬스체크 주석이 맞는지 확인한다

### 해결 방향

- `k8s/backend/deployment.yaml`과 `backend/app/main.py`의 `/health` 경로를 맞춘다
- `kubectl describe ingress -n youtube-mood`와 `kubectl describe pod -n youtube-mood`로 확인한다

## 4. 프론트가 이미지 주소를 못 찾는 문제

### 문제

프론트 Pod가 ImagePullBackOff 상태가 될 수 있다.

### 확인할 것

- ECR에 프론트 이미지가 올라가 있는가
- `k8s/eks/frontend/deployment.yaml`의 이미지 주소가 실제 계정 ID로 바뀌었는가
- EKS 노드가 ECR에 접근할 권한이 있는가

### 해결 방향

- `scripts/push-ecr.ps1`를 다시 실행한다
- `scripts/apply-eks.ps1`에서 계정 ID를 다시 넣는다
- ECR 태그와 실제 이미지명이 맞는지 확인한다

## 5. 로컬 kind와 EKS 파일이 섞이는 문제

### 문제

로컬에서는 되는데 EKS에서만 안 되는 경우가 있다.

### 원인

로컬용 매니페스트와 EKS용 매니페스트가 분리되어 있기 때문이다.

### 해결 방향

- 로컬은 `k8s/backend/deployment.yaml`, `k8s/frontend/deployment.yaml`을 본다
- EKS는 `k8s/eks/backend/deployment.yaml`, `k8s/eks/frontend/deployment.yaml`을 본다
- 실행 전 어떤 파일을 적용하는지 다시 확인한다

## 6. 비용이 걱정되는 문제

### 문제

EKS와 ALB는 무료가 아니다.

### 확인할 것

- 클러스터를 실제로 계속 켜둘 필요가 있는가
- 테스트가 끝났으면 리소스를 정리했는가

### 해결 방향

- 테스트가 끝나면 클러스터와 관련 리소스를 정리한다
- 로컬 확인은 `kind`로 먼저 하고, AWS는 마지막에 붙인다

## 관련 문서

- [EKS 배포 초안](25-eks-draft.md)
- [EKS 실행 순서](32-eks-runbook.md)
- [EKS 최종 점검](33-eks-final-checklist.md)
- [EKS Ingress 준비](28-eks-ingress-plan.md)
- [EKS Load Balancer Controller 설치](30-eks-lbc-install.md)
