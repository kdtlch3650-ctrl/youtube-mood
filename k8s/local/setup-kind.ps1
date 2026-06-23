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
  $candidateKindPaths = @(
    Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages\Kubernetes.kind_Microsoft.Winget.Source_8wekyb3d8bbwe\kind.exe'
  )

  $kindPath = $candidateKindPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($kindPath) {
    $env:PATH = "$(Split-Path $kindPath);$env:PATH"
    Write-Host "kind 경로를 직접 찾았습니다: $kindPath"
  } else {
    throw 'kind 명령을 찾을 수 없습니다. 설치 후 새 PowerShell에서 다시 실행하세요.'
  }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw 'docker 명령을 찾을 수 없습니다. Docker Desktop이 실행 중인지 확인하세요.'
}

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  throw 'kubectl 명령을 찾을 수 없습니다. kubectl을 설치한 뒤 다시 실행하세요.'
}

try {
  docker info | Out-Null
} catch {
  throw 'Docker Engine에 연결할 수 없습니다. Docker Desktop이 완전히 켜진 뒤 다시 실행하세요.'
}

try {
  $existingClusters = @(kind get clusters 2>$null)
} catch {
  $existingClusters = @()
}

if ($existingClusters -contains $ClusterName) {
  Write-Host "kind 클러스터 '$ClusterName'이 이미 있어서 다시 만들지 않습니다."
} else {
  kind create cluster --name $ClusterName
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
