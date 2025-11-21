# Script para preparar DevTrack para despliegue en Render.com
Write-Host "🚀 Preparando DevTrack para Render.com..." -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Ejecuta este script desde la raíz del proyecto DevTrack" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Directorio correcto" -ForegroundColor Green

# Verificar estado de Git
Write-Host ""
Write-Host "📋 Verificando estado de Git..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "📦 Archivos modificados/creados:" -ForegroundColor Yellow
Write-Host "  - backend/requirements.txt (agregado psycopg2-binary)" -ForegroundColor Gray
Write-Host "  - backend/build.sh (script de build para Render)" -ForegroundColor Gray
Write-Host "  - backend/config/settings.py (soporte PostgreSQL)" -ForegroundColor Gray
Write-Host "  - render.yaml (configuración de Render)" -ForegroundColor Gray
Write-Host "  - docs/RENDER_DEPLOY.md (guía detallada)" -ForegroundColor Gray
Write-Host "  - docs/FREE_HOSTING_OPTIONS.md (comparación)" -ForegroundColor Gray
Write-Host "  - README.md (sección de despliegue)" -ForegroundColor Gray

Write-Host ""
$confirm = Read-Host "¿Deseas hacer commit de estos cambios? (s/n)"

if ($confirm -eq "s" -or $confirm -eq "S") {
    Write-Host ""
    Write-Host "📝 Agregando archivos..." -ForegroundColor Cyan
    
    git add backend/requirements.txt
    git add backend/build.sh
    git add backend/config/settings.py
    git add render.yaml
    git add docs/RENDER_DEPLOY.md
    git add docs/FREE_HOSTING_OPTIONS.md
    git add README.md
    
    Write-Host "✅ Archivos agregados" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "💾 Haciendo commit..." -ForegroundColor Cyan
    git commit -m "feat: Preparado para despliegue en Render.com y otras plataformas gratuitas

- Agregado soporte para PostgreSQL (psycopg2-binary)
- Creado build.sh para Render
- Actualizado settings.py para soportar MySQL y PostgreSQL
- Agregado render.yaml con configuración de blueprint
- Documentación completa en docs/RENDER_DEPLOY.md
- Comparación de opciones gratuitas en docs/FREE_HOSTING_OPTIONS.md
- Actualizado README con sección de despliegue"
    
    Write-Host "✅ Commit realizado" -ForegroundColor Green
    
    Write-Host ""
    $push = Read-Host "¿Deseas hacer push a GitHub? (s/n)"
    
    if ($push -eq "s" -or $push -eq "S") {
        Write-Host ""
        Write-Host "🚀 Haciendo push..." -ForegroundColor Cyan
        git push origin main
        Write-Host "✅ Push completado" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "🎉 ¡Listo! Ahora puedes:" -ForegroundColor Green
        Write-Host "  1. Ir a https://render.com" -ForegroundColor Cyan
        Write-Host "  2. Sign up with GitHub" -ForegroundColor Cyan
        Write-Host "  3. Seguir la guía en docs/RENDER_DEPLOY.md" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📚 Documentación:" -ForegroundColor Yellow
        Write-Host "  - docs/RENDER_DEPLOY.md - Guía paso a paso" -ForegroundColor Gray
        Write-Host "  - docs/FREE_HOSTING_OPTIONS.md - Comparación de opciones" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "⏸️  Commit realizado, push pendiente" -ForegroundColor Yellow
        Write-Host "   Ejecuta: git push origin main" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "⏸️  Cambios listos, commit pendiente" -ForegroundColor Yellow
    Write-Host "   Ejecuta este script nuevamente cuando estés listo" -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 Tip: Lee docs/FREE_HOSTING_OPTIONS.md para comparar opciones" -ForegroundColor Cyan
