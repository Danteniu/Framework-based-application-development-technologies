param(
  [int]$RetentionDays = 14
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
  throw "Не найден Python venv: $Python"
}

Set-Location $ProjectRoot
& $Python manage.py backup_db --retention-days $RetentionDays


