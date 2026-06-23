# EKS Load Balancer Controller 설치 스크립트 초안

이 문서는 AWS Load Balancer Controller 설치를 PowerShell 스크립트로 묶은 초안이다.

## 목적

- 수동 명령을 매번 치지 않기 위해서
- 계정 ID와 클러스터 이름만 바꿔서 재사용하기 위해서
- 설치 순서를 실수 없이 반복하기 위해서

## 사용 파일

- `scripts/install-lbc.ps1`
- `docs/30-eks-lbc-install.md`

## 실행 예시

```powershell
.\scripts\install-lbc.ps1 -AccountId 123456789012 -ClusterName youtube-mood -Region ap-northeast-2
```

## 스크립트가 하는 일

1. 필수 명령어가 있는지 확인한다
2. OIDC 제공자를 연결한다
3. IAM 정책 파일을 내려받는다
4. IAM 정책을 만든다
5. `aws-load-balancer-controller` ServiceAccount를 만든다
6. Helm으로 컨트롤러를 설치한다
7. 설치 상태를 확인한다

## 주의할 점

- `AccountId`가 실제 AWS 계정 번호여야 한다
- EKS 클러스터가 먼저 존재해야 한다
- AWS 권한이 부족하면 IAM 정책 생성 단계에서 실패할 수 있다

## 다음 단계

- 실제 AWS 계정으로 한 번 실행해 보기
- `kubectl get ingress` 결과 확인
- 외부 주소가 붙는지 확인
