#!/usr/bin/env pwsh
# ==============================================================================
# DevTrack - Test Runner (PowerShell)
# ==============================================================================

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🧪 DevTrack - Ejecutando Tests" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que los contenedores están corriendo
$backendRunning = docker ps --filter "name=devtrack-backend" --format "{{.Names}}"
if (-not $backendRunning) {
    Write-Host "❌ Error: Contenedor backend no está corriendo" -ForegroundColor Red
    Write-Host "🔄 Inicia DevTrack primero con: .\scripts\docker-dev.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "🐍 Ejecutando tests de Backend..." -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
docker-compose exec backend python manage.py test
$backendExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "⚛️  Ejecutando tests de Frontend..." -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
docker-compose exec frontend npm test -- --run
$frontendExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan

if ($backendExitCode -eq 0 -and $frontendExitCode -eq 0) {
    Write-Host "✅ Todos los tests pasaron" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Algunos tests fallaron" -ForegroundColor Red
    if ($backendExitCode -ne 0) {
        Write-Host "   - Backend: FALLÓ" -ForegroundColor Red
    }
    if ($frontendExitCode -ne 0) {
        Write-Host "   - Frontend: FALLÓ" -ForegroundColor Red
    }
    exit 1
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
