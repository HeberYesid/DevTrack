#!/usr/bin/env pwsh
# ==============================================================================
# DevTrack - View Logs (PowerShell)
# ==============================================================================

param(
    [string]$Service = "all",
    [switch]$Follow = $false
)

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "📋 DevTrack - Ver Logs" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$followFlag = if ($Follow) { "-f" } else { "" }

if ($Service -eq "all") {
    Write-Host "📊 Mostrando logs de todos los servicios..." -ForegroundColor Cyan
    if ($Follow) {
        Write-Host "   (Presiona Ctrl+C para salir)" -ForegroundColor Gray
    }
    Write-Host ""
    docker-compose logs $followFlag
} else {
    Write-Host "📊 Mostrando logs de: $Service" -ForegroundColor Cyan
    if ($Follow) {
        Write-Host "   (Presiona Ctrl+C para salir)" -ForegroundColor Gray
    }
    Write-Host ""
    docker-compose logs $followFlag $Service
}

Write-Host ""
