#!/usr/bin/env pwsh
# =============================================================
# LEVELLY — Full Local Setup & Start Script (Windows PowerShell)
# =============================================================
# Usage: .\start.ps1

param(
    [switch]$SeedOnly,
    [switch]$SkipSeed
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "  LEVELLY — Starting Application" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# ---- Check PostgreSQL ----
Write-Host "[1/6] Checking PostgreSQL connection..." -ForegroundColor Cyan

$pgInstalled = Get-Command psql -ErrorAction SilentlyContinue
if (-not $pgInstalled) {
    Write-Host "  PostgreSQL CLI not found in PATH." -ForegroundColor Yellow
    Write-Host "  Make sure PostgreSQL is running and update DATABASE_URL in .env" -ForegroundColor Yellow
}

# Ensure UTF-8 output encoding for Windows PowerShell
$env:PYTHONUTF8 = "1"
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Load .env if exists
$envFile = "levelly\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([A-Z_]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
        }
    }
    Write-Host "  .env loaded from levelly\.env" -ForegroundColor Gray
    # Ensure backend has .env as well
    if (-not (Test-Path "levelly\backend\.env")) {
        Copy-Item $envFile "levelly\backend\.env"
        Write-Host "  Copied .env to levelly\backend\.env" -ForegroundColor Gray
    }
} else {
    Write-Host "  WARNING: levelly\.env not found. Using defaults." -ForegroundColor Yellow
}

# ---- Backend Setup ----
Write-Host ""
Write-Host "[2/6] Setting up Backend..." -ForegroundColor Cyan

Set-Location "levelly\backend"

# Activate venv if exists, else create
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
& "venv\Scripts\pip" install -r requirements.txt --quiet

# ---- Run Migrations ----
Write-Host ""
Write-Host "[3/6] Running Database Migrations..." -ForegroundColor Cyan
try {
    & "venv\Scripts\alembic" upgrade head
    Write-Host "  Migrations applied successfully." -ForegroundColor Green
} catch {
    Write-Host "  Migration note: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "  Attempting to create tables directly..." -ForegroundColor Gray
    & "venv\Scripts\python" -c "from app.core.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine); print('Tables created OK')"
}

# ---- Seed Data ----
if (-not $SkipSeed) {
    Write-Host ""
    Write-Host "[4/6] Seeding Database..." -ForegroundColor Cyan
    try {
        & "venv\Scripts\python" -X utf8 app/seed.py
    } catch {
        Write-Host "  Seed note: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "  (This is OK if data already exists)" -ForegroundColor Gray
    }
}

if ($SeedOnly) {
    Write-Host ""
    Write-Host "Seed complete. Exiting (--seed-only mode)." -ForegroundColor Green
    Set-Location "..\.."
    exit 0
}

# ---- Start Backend ----
Write-Host ""
Write-Host "[5/6] Starting Backend API..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    $env:PYTHONUTF8 = "1"
    Set-Location $using:PWD
    & "venv\Scripts\uvicorn" app.main:app --host 0.0.0.0 --port 8000 --reload
}
Write-Host "  Backend starting at http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs at http://localhost:8000/docs" -ForegroundColor Gray

Start-Sleep -Seconds 3
Set-Location "..\.."

# ---- Start Frontend ----
Write-Host ""
Write-Host "[6/6] Starting Frontend..." -ForegroundColor Cyan
Set-Location "levelly\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend npm packages..." -ForegroundColor Gray
    npm install --silent
}
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
}
Write-Host "  Frontend starting at http://localhost:5173" -ForegroundColor Green

Set-Location "..\.."

# ---- Summary ----
Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "  LEVELLY is starting up!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:    http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Demo Login:" -ForegroundColor Yellow
Write-Host "    Email:    arjun@levelly.app" -ForegroundColor White
Write-Host "    Password: Levelly@123" -ForegroundColor White
Write-Host ""
Write-Host "  Admin Login:" -ForegroundColor Yellow
Write-Host "    Email:    admin@levelly.app" -ForegroundColor White
Write-Host "    Password: Admin@Levelly123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Gray

try {
    Wait-Job $backendJob, $frontendJob
} finally {
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
}
