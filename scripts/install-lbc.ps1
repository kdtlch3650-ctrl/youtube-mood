param(
  [Parameter(Mandatory = $true)]
  [string]$AccountId,
  [string]$Region = 'ap-northeast-2',
  [string]$ClusterName = 'youtube-mood',
  [string]$PolicyName = 'AWSLoadBalancerControllerIAMPolicy',
  [string]$ControllerVersion = 'v3.4.0'
)

$ErrorActionPreference = 'Stop'

foreach ($command in @('aws', 'eksctl', 'kubectl', 'helm')) {
  if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
    throw "$command 명령을 찾을 수 없습니다. 설치한 뒤 다시 실행하세요."
  }
}

$policyArn = "arn:aws:iam::$AccountId:policy/$PolicyName"
$tempRoot = Join-Path $env:TEMP 'youtube-mood-lbc'
$policyUrl = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/$ControllerVersion/docs/install/iam_policy.json"

if (Test-Path $tempRoot) {
  Remove-Item -Recurse -Force $tempRoot
}

New-Item -ItemType Directory -Path $tempRoot | Out-Null

Write-Host '1. OIDC 제공자 연결'
eksctl utils associate-iam-oidc-provider --region $Region --cluster $ClusterName --approve

Write-Host '2. IAM 정책 파일 다운로드'
$policyFile = Join-Path $tempRoot 'iam-policy.json'
Invoke-WebRequest -Uri $policyUrl -OutFile $policyFile

Write-Host '3. IAM 정책 존재 확인'
aws iam get-policy --policy-arn $policyArn *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host '   정책이 없어서 새로 생성합니다'
  aws iam create-policy --policy-name $PolicyName --policy-document "file://$policyFile"
  if ($LASTEXITCODE -ne 0) {
    throw 'IAM 정책 생성에 실패했습니다.'
  }
} else {
  Write-Host '   이미 정책이 있습니다'
}

Write-Host '4. ServiceAccount 생성'
eksctl create iamserviceaccount `
  --cluster $ClusterName `
  --namespace kube-system `
  --name aws-load-balancer-controller `
  --attach-policy-arn $policyArn `
  --override-existing-serviceaccounts `
  --region $Region `
  --approve

Write-Host '5. Helm 저장소 추가'
helm repo add eks https://aws.github.io/eks-charts
helm repo update

Write-Host '6. AWS Load Balancer Controller 설치'
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller `
  -n kube-system `
  --set clusterName=$ClusterName `
  --set serviceAccount.create=false `
  --set serviceAccount.name=aws-load-balancer-controller

Write-Host '7. 설치 상태 확인'
kubectl get pods -n kube-system
