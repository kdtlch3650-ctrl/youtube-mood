# EKS 적용 흐름 초안

이 문서는 ECR에 이미지를 올린 뒤, EKS에 실제로 반영하는 흐름을 정리한 초안이다.

## 목표

- ECR에 올라간 이미지를 EKS 매니페스트에 연결한다
- 로컬용 파일과 EKS용 파일을 분리해서 관리한다
- 계정 ID는 스크립트 인자로 받아서 교체한다

## 사용 파일

- `k8s/eks/backend/deployment.yaml`
- `k8s/eks/frontend/deployment.yaml`
- `scripts/push-ecr.ps1`
- `scripts/apply-eks.ps1`

## 기본 흐름

1. Docker 이미지를 ECR에 푸시한다
2. `scripts/apply-eks.ps1`를 실행한다
3. 스크립트가 `<account-id>`를 실제 계정 ID로 바꾼다
4. `kubectl apply`로 EKS에 반영한다
5. `kubectl get pods`로 상태를 확인한다

## 예시

```powershell
.\scripts\push-ecr.ps1 -AccountId 123456789012
.\scripts\apply-eks.ps1 -AccountId 123456789012
```

## 주의할 점

- EKS 배포 전에 ECR 이미지 푸시가 먼저 끝나야 한다
- 로컬 `kind`용 매니페스트는 건드리지 않는다
- `AccountId`를 비워 두면 실제 이미지 주소가 완성되지 않는다

## 다음 단계

- 실제 AWS 계정 ID를 넣어서 테스트
- EKS Ingress Controller 준비
- 도메인 연결 여부 결정
