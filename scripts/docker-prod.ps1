#!/usr/bin/env pwsh
# ==============================================================================
# DevTrack - Production Environment Launcher (PowerShell)
# ==============================================================================

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 DevTrack - Modo PRODUCCIÓN" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker está instalado
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Docker no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar que Docker está corriendo
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Docker no está corriendo" -ForegroundColor Red
    exit 1
}

# Verificar que existe .env.docker
if (-not (Test-Path ".env.docker")) {
    Write-Host "❌ Error: .env.docker no encontrado" -ForegroundColor Red
    Write-Host "📝 Copia .env.docker.example y configura los valores de producción" -ForegroundColor Yellow
    exit 1
}

# Advertencia de producción
Write-Host "⚠️  ATENCIÓN: Estás iniciando en modo PRODUCCIÓN" -ForegroundColor Yellow
Write-Host "📋 Asegúrate de haber configurado:" -ForegroundColor Yellow
Write-Host "   - DJANGO_SECRET_KEY seguro" -ForegroundColor Yellow
Write-Host "   - DJANGO_DEBUG=False" -ForegroundColor Yellow
Write-Host "   - Contraseñas de base de datos seguras" -ForegroundColor Yellow
Write-Host "   - ALLOWED_HOSTS configurado correctamente" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "¿Continuar? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔨 Construyendo imágenes de producción..." -ForegroundColor Cyan
Write-Host ""

# Levantar en modo detached (background)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ DevTrack iniciado en modo producción" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Ver logs: docker-compose logs -f" -ForegroundColor Cyan
    Write-Host "🛑 Detener: docker-compose down" -ForegroundColor Cyan
    Write-Host "📈 Ver estado: docker-compose ps" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Error al iniciar DevTrack" -ForegroundColor Red
}

Write-Host ""
