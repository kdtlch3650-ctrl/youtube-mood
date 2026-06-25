param(
  [Parameter(Mandatory = $true)]
  [string]$AccountId,
  [Parameter(Mandatory = $true)]
  [string]$VpcId,
  [string]$Region = 'ap-northeast-2',
  [string]$ClusterName = 'youtube-mood',
  [string]$PolicyName = 'AWSLoadBalancerControllerIAMPolicy',
  [string]$ControllerVersion = 'v3.4.0'
)

$ErrorActionPreference = 'Stop'

foreach ($command in @('aws', 'eksctl', 'kubectl', 'helm')) {
  if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
    throw "$command is not installed or not found in PATH."
  }
}

$policyArn = "arn:aws:iam::$AccountId:policy/$PolicyName"
$tempRoot = Join-Path $env:TEMP 'youtube-mood-lbc'
$policyUrl = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/$ControllerVersion/docs/install/iam_policy.json"

if (Test-Path $tempRoot) {
  Remove-Item -Recurse -Force $tempRoot
}

New-Item -ItemType Directory -Path $tempRoot | Out-Null

Write-Host '1. Associate OIDC provider'
eksctl utils associate-iam-oidc-provider --region $Region --cluster $ClusterName --approve

Write-Host '2. Download IAM policy'
$policyFile = Join-Path $tempRoot 'iam-policy.json'
Invoke-WebRequest -Uri $policyUrl -OutFile $policyFile

Write-Host '3. Ensure IAM policy exists'
aws iam get-policy --policy-arn $policyArn *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host '   Policy not found. Creating a new one.'
  aws iam create-policy --policy-name $PolicyName --policy-document "file://$policyFile"
  if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create IAM policy.'
  }
} else {
  Write-Host '   Policy already exists.'
}

Write-Host '4. Create service account'
eksctl create iamserviceaccount `
  --cluster $ClusterName `
  --namespace kube-system `
  --name aws-load-balancer-controller `
  --attach-policy-arn $policyArn `
  --override-existing-serviceaccounts `
  --region $Region `
  --approve

Write-Host '5. Add Helm repository'
helm repo add eks https://aws.github.io/eks-charts
helm repo update

Write-Host '6. Install AWS Load Balancer Controller'
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller `
  -n kube-system `
  --set-string clusterName=$ClusterName `
  --set-string region=$Region `
  --set-string vpcId=$VpcId `
  --set serviceAccount.create=false `
  --set serviceAccount.name=aws-load-balancer-controller

Write-Host '7. Check installed pods'
kubectl get pods -n kube-system
