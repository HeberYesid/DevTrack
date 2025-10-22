#!/usr/bin/env pwsh
# ==============================================================================
# DevTrack - Cleanup Script (PowerShell)
# ==============================================================================

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🧹 DevTrack - Limpieza de Contenedores" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Esta operación detendrá todos los contenedores de DevTrack" -ForegroundColor Yellow
Write-Host ""

# Detener y eliminar contenedores
Write-Host "🛑 Deteniendo contenedores..." -ForegroundColor Cyan
docker-compose down

Write-Host ""
Write-Host "¿Deseas eliminar también los volúmenes (BASE DE DATOS)?"-ForegroundColor Red
Write-Host "⚠️  ADVERTENCIA: Esto eliminará toda la data de la base de datos" -ForegroundColor Red
$deleteVolumes = Read-Host "Eliminar volúmenes (y/N)"

if ($deleteVolumes -eq 'y' -or $deleteVolumes -eq 'Y') {
    Write-Host ""
    Write-Host "🗑️  Eliminando volúmenes..." -ForegroundColor Red
    docker-compose down -v
    Write-Host "✅ Volúmenes eliminados" -ForegroundColor Green
}

Write-Host ""
Write-Host "¿Deseas eliminar imágenes de DevTrack para forzar rebuild?" -ForegroundColor Yellow
$deleteImages = Read-Host "Eliminar imágenes (y/N)"

if ($deleteImages -eq 'y' -or $deleteImages -eq 'Y') {
    Write-Host ""
    Write-Host "🗑️  Eliminando imágenes..." -ForegroundColor Yellow
    docker-compose down --rmi local
    Write-Host "✅ Imágenes eliminadas" -ForegroundColor Green
}

Write-Host ""
Write-Host "🧹 Limpiando imágenes sin usar..." -ForegroundColor Cyan
docker image prune -f

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Limpieza completada" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
