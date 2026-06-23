# EKS 실행 순서 초안

이 문서는 지금까지 만든 ECR, EKS, Ingress 관련 초안을 실제 실행 순서로 묶은 초안이다.

## 목표

- 어떤 순서로 실행해야 하는지 한눈에 보이게 한다
- 각 단계에서 무엇이 성공 기준인지 적어둔다
- 나중에 AWS에서 실제로 따라 하기 쉽게 만든다

## 준비 단계

- Docker Desktop 실행
- AWS CLI 로그인 확인
- `kubectl`, `eksctl`, `helm` 설치 확인
- EKS 클러스터 생성 확인
- AWS 계정 ID 준비

## 실행 순서

### 1. ECR 이미지 푸시

```powershell
.\scripts\push-ecr.ps1 -AccountId 123456789012
```

확인 기준:
- 백엔드와 프론트 이미지가 ECR에 올라간다

### 2. AWS Load Balancer Controller 설치

```powershell
.\scripts\install-lbc.ps1 -AccountId 123456789012 -ClusterName youtube-mood -Region ap-northeast-2
```

확인 기준:
- `kube-system` 네임스페이스에 컨트롤러 파드가 실행된다

### 3. EKS 매니페스트 적용

```powershell
.\scripts\apply-eks.ps1 -AccountId 123456789012 -ClusterName youtube-mood -Region ap-northeast-2
```

확인 기준:
- `youtube-mood` 네임스페이스의 파드가 Running 상태가 된다
- Service와 Ingress가 생성된다

### 4. 외부 주소 확인

```powershell
kubectl get ingress -n youtube-mood
```

확인 기준:
- ALB 주소가 보인다
- `/api`와 `/` 경로가 각각 올바른 서비스로 연결된다

## 실패하면 먼저 볼 것

- Docker Desktop이 켜져 있는가
- AWS 로그인과 권한이 맞는가
- EKS 클러스터가 실제로 존재하는가
- ECR 이미지 푸시가 먼저 끝났는가
- Controller 설치가 끝났는가

## 주의할 점

- `AccountId`는 실제 AWS 계정 번호여야 한다
- 순서를 바꾸면 Ingress가 먼저 떠도 외부 주소가 안 붙을 수 있다
- 비용이 드는 단계는 EKS와 ALB 쪽이다

## 다음 단계

- 실제 AWS 값으로 한 번 실행해 보기
- 실패한 단계의 로그를 기록하기
- 최종 배포 체크리스트와 연결하기
