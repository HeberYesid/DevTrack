#!/usr/bin/env pwsh
# ==============================================================================
# DevTrack - Shell Access (PowerShell)
# ==============================================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('backend', 'frontend', 'db')]
    [string]$Service
)

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🐚 DevTrack - Acceso a Shell" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$containerMap = @{
    'backend' = 'devtrack-backend'
    'frontend' = 'devtrack-frontend'
    'db' = 'devtrack-mysql'
}

$shellMap = @{
    'backend' = '/bin/bash'
    'frontend' = '/bin/sh'
    'db' = '/bin/bash'
}

$container = $containerMap[$Service]
$shell = $shellMap[$Service]

# Verificar que el contenedor existe
$exists = docker ps --filter "name=$container" --format "{{.Names}}"
if (-not $exists) {
    Write-Host "❌ Error: Contenedor $container no está corriendo" -ForegroundColor Red
    Write-Host "🔄 Inicia DevTrack primero" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔗 Conectando a $Service ($container)..." -ForegroundColor Cyan
Write-Host "   (Escribe 'exit' para salir)" -ForegroundColor Gray
Write-Host ""

docker exec -it $container $shell

Write-Host ""
Write-Host "👋 Desconectado de $Service" -ForegroundColor Yellow
Write-Host ""
