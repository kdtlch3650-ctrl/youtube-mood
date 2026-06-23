# ECR 준비 초안

이 문서는 Kubernetes로 올리기 전에 Docker 이미지를 AWS ECR로 보내기 위한 준비 초안이다.

목표는 다음과 같다.

- 백엔드와 프론트 이미지를 각각 ECR에 올린다
- 로컬 `kind`에서 쓰던 이미지를 AWS 배포용으로 다시 태그한다
- 나중에 EKS가 이미지를 가져갈 수 있게 한다

## 왜 필요한가

Kubernetes는 로컬 Docker 이미지보다, 원격 레지스트리의 이미지를 쓰는 편이 일반적이다.
ECR은 AWS에서 제공하는 Docker 이미지 저장소다.

## 준비할 것

- AWS 계정
- AWS CLI
- Docker
- ECR 저장소 2개
  - `youtube-mood-backend`
  - `youtube-mood-frontend`

## 권장 순서

1. ECR 리포지토리 생성
2. Docker 로그인
3. 이미지 태그 변경
4. 이미지 푸시
5. EKS 매니페스트에서 이미지 주소 교체

## 예시 명령

```powershell
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com

docker tag youtube-mood-backend:latest <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/youtube-mood-backend:latest
docker tag youtube-mood-frontend:latest <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/youtube-mood-frontend:latest

docker push <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/youtube-mood-backend:latest
docker push <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/youtube-mood-frontend:latest
```

## 주의할 점

- `<account-id>`는 AWS 계정 번호로 바꿔야 한다
- 리전은 프로젝트에서 쓰는 리전과 같게 유지한다
- 이미지는 ECR에 올린 뒤에 EKS에서 참조한다

## 다음 단계

- ECR 저장소 생성
- EKS 배포용 이미지 주소를 매니페스트에 반영
- EKS 클러스터 생성
