param(
  [Parameter(Mandatory = $true)]
  [string]$AccountId,
  [string]$Region = 'ap-northeast-2',
  [string]$ClusterName = 'youtube-mood'
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
  throw 'aws 명령을 찾을 수 없습니다. AWS CLI를 설치한 뒤 다시 실행하세요.'
}

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  throw 'kubectl 명령을 찾을 수 없습니다. kubectl을 설치한 뒤 다시 실행하세요.'
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$eksSourceRoot = Join-Path $repoRoot 'k8s\eks'
$tempRoot = Join-Path $env:TEMP 'youtube-mood-eks'

if (Test-Path $tempRoot) {
  Remove-Item -Recurse -Force $tempRoot
}

New-Item -ItemType Directory -Path $tempRoot | Out-Null

aws eks update-kubeconfig --region $Region --name $ClusterName

function Copy-EksTemplate {
  param(
    [string]$SourcePath,
    [string]$TargetPath
  )

  $content = Get-Content -Raw -Encoding utf8 $SourcePath
  $content = $content.Replace('<account-id>', $AccountId)
  Set-Content -Encoding utf8 -Path $TargetPath -Value $content
}

Copy-EksTemplate -SourcePath (Join-Path $eksSourceRoot 'backend\deployment.yaml') -TargetPath (Join-Path $tempRoot 'backend-deployment.yaml')
Copy-EksTemplate -SourcePath (Join-Path $eksSourceRoot 'frontend\deployment.yaml') -TargetPath (Join-Path $tempRoot 'frontend-deployment.yaml')

kubectl apply -f (Join-Path $repoRoot 'k8s\namespace.yaml')
kubectl apply -f (Join-Path $repoRoot 'k8s\configmap.yaml')
kubectl apply -f (Join-Path $repoRoot 'k8s\secret.yaml')
kubectl apply -f (Join-Path $tempRoot 'backend-deployment.yaml')
kubectl apply -f (Join-Path $repoRoot 'k8s\backend\service.yaml')
kubectl apply -f (Join-Path $tempRoot 'frontend-deployment.yaml')
kubectl apply -f (Join-Path $repoRoot 'k8s\frontend\service.yaml')
kubectl apply -f (Join-Path $repoRoot 'k8s\eks\ingress-class.yaml')
kubectl apply -f (Join-Path $repoRoot 'k8s\eks\ingress.yaml')

kubectl get pods -n youtube-mood -o wide
kubectl get svc -n youtube-mood
