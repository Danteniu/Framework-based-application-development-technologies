$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Coverage = Join-Path $ProjectRoot ".venv\Scripts\coverage.exe"

Set-Location $ProjectRoot

& $Python -m pip install -r requirements.txt

Write-Host "== Django tests ==" -ForegroundColor Cyan
& $Python manage.py test

Write-Host "== Coverage ==" -ForegroundColor Cyan
& $Coverage run -m django test --settings=sistemakontrolya.settings
& $Coverage report -m
& $Coverage html
Write-Host "HTML coverage report: htmlcov\\index.html" -ForegroundColor Green


