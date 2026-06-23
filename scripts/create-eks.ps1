param(
  [string]$ClusterName = 'youtube-mood',
  [string]$Region = 'ap-northeast-2'
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command eksctl -ErrorAction SilentlyContinue)) {
  throw 'eksctl 명령을 찾을 수 없습니다. eksctl을 설치한 뒤 다시 실행하세요.'
}

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  throw 'kubectl 명령을 찾을 수 없습니다. kubectl을 설치한 뒤 다시 실행하세요.'
}

eksctl create cluster --name $ClusterName --region $Region

kubectl get nodes -o wide
kubectl get pods -A -o wide
