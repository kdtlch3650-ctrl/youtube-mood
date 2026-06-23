# EKS 최종 점검 체크리스트

이 문서는 EKS 배포를 끝내기 전에 확인할 항목만 따로 정리한 체크리스트다.

## 1. 사전 준비

- [ ] AWS CLI 로그인 상태가 정상인가
- [ ] `kubectl`이 EKS 클러스터를 바라보고 있는가
- [ ] `eksctl`이 설치되어 있는가
- [ ] `helm`이 설치되어 있는가
- [ ] Docker 이미지가 ECR에 올라가 있는가
- [ ] AWS 계정 ID가 준비되어 있는가

## 2. 컨트롤러 확인

- [ ] AWS Load Balancer Controller가 설치되어 있는가
- [ ] `kube-system` 네임스페이스에 관련 파드가 Running 상태인가
- [ ] IRSA 또는 Pod Identity 설정이 완료되었는가

## 3. 배포 확인

- [ ] `namespace`, `configMap`, `secret`이 적용되었는가
- [ ] 백엔드 배포가 ECR 이미지를 참조하는가
- [ ] 프론트 배포가 ECR 이미지를 참조하는가
- [ ] `IngressClass`가 적용되었는가
- [ ] `Ingress`가 적용되었는가

## 4. 동작 확인

- [ ] `kubectl get pods -n youtube-mood`에서 파드가 Running 상태인가
- [ ] `kubectl get svc -n youtube-mood`에서 서비스가 생성되었는가
- [ ] `kubectl get ingress -n youtube-mood`에서 외부 주소가 보이는가
- [ ] `/api`가 백엔드로 연결되는가
- [ ] `/`가 프론트로 연결되는가

## 5. 문제 발생 시 확인할 것

- [ ] ECR 이미지 주소가 실제 계정 ID로 바뀌었는가
- [ ] 백엔드 헬스체크 경로가 `/health`인가
- [ ] 프론트 헬스체크 경로가 `/`인가
- [ ] AWS Load Balancer Controller 설치가 끝나기 전에 Ingress를 먼저 적용하지 않았는가
- [ ] AWS 권한이 부족하지 않은가

## 6. 마무리 기준

아래 항목이 모두 맞으면 EKS 배포 확인 단계가 끝난다.

- [ ] 컨트롤러 설치 완료
- [ ] EKS 파드 Running
- [ ] 외부 주소 생성
- [ ] 경로 분기 동작
- [ ] 이미지 주소 반영 완료
