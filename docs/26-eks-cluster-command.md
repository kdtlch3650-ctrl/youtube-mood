# EKS 클러스터 생성 명령 초안

이 문서는 EKS 클러스터를 만들기 위한 최소 명령을 정리한 초안이다.

AWS 공식 문서와 `eksctl` 문서에서는 간단한 클러스터 생성 예시를 제공한다.  
기본 흐름은 다음과 같다.

## 전제

- AWS CLI가 설정되어 있어야 한다
- `kubectl`과 `eksctl`이 설치되어 있어야 한다
- 사용할 리전과 클러스터 이름을 정해야 한다

## 권장 값

- 리전: `ap-northeast-2`
- 클러스터 이름: `youtube-mood`

## 기본 생성 명령

```powershell
eksctl create cluster --name youtube-mood --region ap-northeast-2
```

## 생성 후 확인

```powershell
kubectl get nodes -o wide
kubectl get pods -A -o wide
```

## 삭제 명령

```powershell
eksctl delete cluster --name youtube-mood --region ap-northeast-2
```

## 주의할 점

- 이 명령은 EKS 비용이 발생할 수 있다
- 생성에는 몇 분이 걸릴 수 있다
- 로컬 `kind`에서 먼저 확인한 뒤 사용하는 것이 안전하다
- ECR 이미지 주소를 반영한 뒤에 배포해야 한다

## 다음 단계

- ECR 이미지 주소를 EKS 매니페스트에 반영
- Ingress Controller 추가 여부 결정
- 실제 배포용 `kubectl apply` 순서 정리
