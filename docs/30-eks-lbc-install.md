# EKS Load Balancer Controller 설치 초안

이 문서는 EKS에서 `Ingress`를 실제로 동작시키기 위해 AWS Load Balancer Controller를 설치하는 초안이다.

AWS 공식 문서 기준으로, EKS에서는 보통 IRSA를 사용해 컨트롤러에 IAM 권한을 부여하고 Helm으로 설치한다.

## 설치 전 확인

- EKS 클러스터가 먼저 생성되어 있어야 한다
- `kubectl`, `eksctl`, `helm`, `aws` CLI가 설치되어 있어야 한다
- AWS 자격 증명이 설정되어 있어야 한다

## 권장 흐름

1. OIDC 제공자를 연결한다
2. 컨트롤러용 IAM 정책을 만든다
3. `aws-load-balancer-controller` 서비스 계정을 만든다
4. Helm으로 컨트롤러를 설치한다
5. `IngressClass`와 `Ingress`를 적용한다

## 예시 명령

```powershell
eksctl utils associate-iam-oidc-provider --region ap-northeast-2 --cluster youtube-mood --approve
```

```powershell
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v3.4.0/docs/install/iam_policy.json
aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam-policy.json
```

```powershell
eksctl create iamserviceaccount `
  --cluster=youtube-mood `
  --namespace=kube-system `
  --name=aws-load-balancer-controller `
  --attach-policy-arn=arn:aws:iam::<AWS_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy `
  --override-existing-serviceaccounts `
  --region ap-northeast-2 `
  --approve
```

```powershell
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=youtube-mood --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller
```

## 이후 적용 순서

```powershell
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

## 확인 기준

- `kubectl get pods -n kube-system`에서 컨트롤러가 실행 중이어야 한다
- `kubectl get ingress -n youtube-mood`에서 외부 주소가 생성되어야 한다
- `/api`와 `/` 요청이 각각 올바른 서비스로 연결되어야 한다

## 주의할 점

- Helm 설치만으로는 외부 주소가 즉시 생기지 않을 수 있다
- IAM 권한이 부족하면 ALB 생성이 실패한다
- 이 문서는 실제 계정에 맞춰 ARN과 클러스터 이름을 바꿔야 한다
