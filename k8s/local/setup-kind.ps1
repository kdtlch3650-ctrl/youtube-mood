param(
  [string]$ClusterName = 'youtube-mood'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$backendImage = 'youtube-mood-backend:latest'
$frontendImage = 'youtube-mood-frontend:latest'
$secretPath = Join-Path $repoRoot 'k8s\secret.yaml'

Set-Location $repoRoot

if (-not (Get-Command kind -ErrorAction SilentlyContinue)) {
  throw 'kind 명령을 찾을 수 없습니다. 설치 후 다시 실행하세요.'
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw 'docker 명령을 찾을 수 없습니다. Docker Desktop이 실행 중인지 확인하세요.'
}

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  throw 'kubectl 명령을 찾을 수 없습니다. kubectl을 설치한 뒤 다시 실행하세요.'
}

$existingClusters = @(kind get clusters 2>$null)
if ($existingClusters -notcontains $ClusterName) {
  kind create cluster --name $ClusterName
} else {
  Write-Host "kind 클러스터 '$ClusterName'이 이미 있어서 다시 만들지 않습니다."
}

docker build -t $backendImage .\backend
docker build -t $frontendImage .\frontend

kind load docker-image $backendImage --name $ClusterName
kind load docker-image $frontendImage --name $ClusterName

kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\configmap.yaml

if (Test-Path $secretPath) {
  kubectl apply -f $secretPath
} else {
  & (Join-Path $PSScriptRoot 'create-secret.ps1') -Namespace 'youtube-mood'
  kubectl apply -f $secretPath
}

kubectl apply -f .\k8s\backend\deployment.yaml
kubectl apply -f .\k8s\backend\service.yaml
kubectl apply -f .\k8s\frontend\deployment.yaml
kubectl apply -f .\k8s\frontend\service.yaml
kubectl apply -f .\k8s\ingress\ingress.yaml

kubectl get pods -n youtube-mood
kubectl get svc -n youtube-mood
kubectl get ingress -n youtube-mood
