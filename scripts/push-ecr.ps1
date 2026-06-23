param(
  [Parameter(Mandatory = $true)]
  [string]$AccountId,
  [string]$Region = 'ap-northeast-2'
)

$ErrorActionPreference = 'Stop'

$backendImage = "$AccountId.dkr.ecr.$Region.amazonaws.com/youtube-mood-backend:latest"
$frontendImage = "$AccountId.dkr.ecr.$Region.amazonaws.com/youtube-mood-frontend:latest"

if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
  throw 'aws 명령을 찾을 수 없습니다. AWS CLI를 설치한 뒤 다시 실행하세요.'
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw 'docker 명령을 찾을 수 없습니다. Docker Desktop이 실행 중인지 확인하세요.'
}

$loginPassword = aws ecr get-login-password --region $Region
if (-not $loginPassword) {
  throw 'ECR 로그인 비밀번호를 가져오지 못했습니다. AWS 인증 상태를 확인하세요.'
}

$loginPassword | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"

docker tag youtube-mood-backend:latest $backendImage
docker tag youtube-mood-frontend:latest $frontendImage

docker push $backendImage
docker push $frontendImage
