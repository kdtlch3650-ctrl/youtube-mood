# EKS 배포 초안

이 문서는 ECR에 이미지를 올린 뒤, Kubernetes를 AWS EKS로 옮기기 위한 초안이다.

## 목표

- 로컬 `kind`에서 확인한 구성을 AWS EKS로 옮긴다
- 백엔드와 프론트를 ECR 이미지로 배포한다
- 나중에 도메인과 로드밸런서를 붙일 수 있게 한다

## 준비할 것

- AWS 계정
- AWS CLI
- `kubectl`
- `eksctl` 또는 AWS 콘솔
- ECR 이미지
  - `youtube-mood-backend`
  - `youtube-mood-frontend`

## 권장 순서

1. ECR 이미지 준비
2. EKS 클러스터 생성
3. 노드 그룹 생성
4. IAM 권한 확인
5. EKS 전용 매니페스트의 이미지 주소를 ECR로 반영
6. IngressClass와 Ingress를 EKS용으로 적용
7. 상태 확인

관련 실행 문서:

- [EKS 클러스터 생성](26-eks-cluster-command.md)
- [EKS 적용 흐름](27-eks-apply-flow.md)
- [EKS Ingress 준비](28-eks-ingress-plan.md)
- [EKS Ingress Controller](29-eks-ingress-controller-draft.md)
- [EKS Load Balancer Controller 설치](30-eks-lbc-install.md)
- [EKS LBC 설치 스크립트](31-eks-lbc-install-script.md)
- [EKS 실행 순서](32-eks-runbook.md)
- [EKS 최종 점검](33-eks-final-checklist.md)

## 초안 설정값

- 리전: `ap-northeast-2`
- 클러스터 이름: `youtube-mood`
- 네임스페이스: `youtube-mood`

## 배포 전 확인

- 백엔드와 프론트 이미지가 ECR에 올라가 있는가
- `configMap`과 `Secret`이 EKS에도 적용 가능한가
- Ingress를 쓸 경우 컨트롤러를 붙였는가

## 예시 흐름

```powershell
aws eks update-kubeconfig --region ap-northeast-2 --name youtube-mood

kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\configmap.yaml
kubectl apply -f k8s\secret.yaml
kubectl apply -f k8s\eks\backend\deployment.yaml
kubectl apply -f k8s\backend\service.yaml
kubectl apply -f k8s\eks\frontend\deployment.yaml
kubectl apply -f k8s\frontend\service.yaml
kubectl apply -f k8s\eks\ingress-class.yaml
kubectl apply -f k8s\eks\ingress.yaml
```

## 주의할 점

- EKS는 비용이 든다
- 처음부터 크게 만들지 않는다
- 로컬 `kind`에서 정상 확인한 뒤 옮긴다
- 로컬 매니페스트와 EKS 매니페스트는 분리해서 관리한다
- 이미지 주소를 `docker.io/library/...`가 아니라 ECR 주소로 반영해야 한다
- Ingress는 AWS Load Balancer Controller용 설정이 필요하다

## 다음 단계

- EKS 클러스터 생성 명령 정리
- ECR 이미지 주소 반영
- Ingress Controller 준비
