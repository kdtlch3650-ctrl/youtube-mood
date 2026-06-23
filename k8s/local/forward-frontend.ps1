param(
  [int]$LocalPort = 8080
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  throw 'kubectl 명령을 찾을 수 없습니다. kubectl을 설치한 뒤 다시 실행하세요.'
}

Start-Process -FilePath kubectl -ArgumentList @(
  'port-forward',
  '-n',
  'youtube-mood',
  'svc/youtube-mood-frontend',
  "$LocalPort`:80"
) -WindowStyle Hidden

Write-Host "프론트 포트포워딩 시작: http://127.0.0.1:$LocalPort"
