#!/usr/bin/env pwsh
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "DevTrack - Modo DESARROLLO" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}

$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker no está corriendo" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".env.docker")) {
    Write-Host "Creando .env.docker desde .env.docker.example..." -ForegroundColor Yellow
    Copy-Item ".env.docker.example" ".env.docker"
}

Write-Host "Construyendo imágenes..." -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "DevTrack detenido" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
