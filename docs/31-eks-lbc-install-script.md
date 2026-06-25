# EKS Load Balancer Controller 설치 스크립트 안내

이 문서는 `scripts/install-lbc.ps1`의 실행 방법과 입력값을 정리한다.

## 목적

- OIDC provider 연결
- IAM policy 생성 또는 재사용
- `aws-load-balancer-controller` ServiceAccount 생성
- Helm으로 컨트롤러 설치
- VPC 자동 탐지가 안 될 때 `vpcId`를 명시

## 사용 파일

- `scripts/install-lbc.ps1`
- `docs/30-eks-lbc-install.md`

## 실행 예시

```powershell
.\scripts\install-lbc.ps1 -AccountId 123456789012 -VpcId vpc-06d30012eee7ab1ba -ClusterName youtube-mood -Region ap-northeast-2
```

## 새로 필요한 값

- `AccountId`: AWS 계정 번호
- `VpcId`: 클러스터가 사용하는 VPC ID

## 왜 `VpcId`가 필요한가

컨트롤러가 인스턴스 메타데이터에서 VPC ID를 자동으로 읽지 못하면 시작에 실패할 수 있다. 이때 Helm 설치값에 `vpcId`를 직접 넣는다.

## 확인 기준

- `kubectl get pods -n kube-system`에서 `aws-load-balancer-controller`가 `Running`이어야 한다.
- 더 이상 `failed to get VPC ID` 오류가 나오지 않아야 한다.
