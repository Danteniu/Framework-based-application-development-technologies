param(
  [string]$HostUrl = "http://127.0.0.1:8000",
  [int]$Users = 50,
  [int]$SpawnRate = 10,
  [string]$RunTime = "1m",
  [string]$CsvPrefix = "artifacts\\loadtest"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Locust = Join-Path $ProjectRoot ".venv\Scripts\locust.exe"

Set-Location $ProjectRoot
New-Item -ItemType Directory -Force -Path "artifacts" | Out-Null

Write-Host "== Locust headless ==" -ForegroundColor Cyan
Write-Host "Host=$HostUrl Users=$Users SpawnRate=$SpawnRate Time=$RunTime Csv=$CsvPrefix" -ForegroundColor Cyan

& $Locust -f locustfile.py --headless -u $Users -r $SpawnRate -t $RunTime --host $HostUrl --csv $CsvPrefix --csv-full-history


