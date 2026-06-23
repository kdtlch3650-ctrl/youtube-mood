param(
  [string]$Namespace = 'youtube-mood'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$envFile = Join-Path $repoRoot 'backend\.env'
$secretFile = Join-Path $repoRoot 'k8s\secret.yaml'

Set-Location $repoRoot

if (-not (Test-Path $envFile)) {
  throw 'backend/.env 파일을 찾을 수 없습니다. 먼저 로컬 환경 파일을 준비하세요.'
}

$content = Get-Content -Encoding utf8 $envFile | Where-Object {
  $_ -and -not $_.StartsWith('#') -and $_.Contains('=')
}

$pairs = @{}
foreach ($line in $content) {
  $parts = $line.Split('=', 2)
  if ($parts.Count -ne 2) {
    continue
  }

  $key = $parts[0].Trim()
  $value = $parts[1].Trim()
  if ($key) {
    $pairs[$key] = $value
  }
}

$requiredKeys = @('YOUTUBE_API_KEY', 'AWS_BEARER_TOKEN_BEDROCK')
foreach ($requiredKey in $requiredKeys) {
  if (-not $pairs.ContainsKey($requiredKey)) {
    throw "$requiredKey 값이 backend/.env에 없습니다."
  }
}

function Convert-ToYamlSingleQuotedString {
  param([string]$Value)

  return "'" + ($Value -replace "'", "''") + "'"
}

$secretYaml = @"
apiVersion: v1
kind: Secret
metadata:
  name: youtube-mood-secret
  namespace: $Namespace
type: Opaque
stringData:
  YOUTUBE_API_KEY: $(Convert-ToYamlSingleQuotedString $pairs['YOUTUBE_API_KEY'])
  AWS_BEARER_TOKEN_BEDROCK: $(Convert-ToYamlSingleQuotedString $pairs['AWS_BEARER_TOKEN_BEDROCK'])
"@

Set-Content -Encoding utf8 -LiteralPath $secretFile -Value $secretYaml

Write-Host "생성 완료: $secretFile"
