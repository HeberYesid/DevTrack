param(
    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl
)

# Asegurarnos de estar en el directorio correcto
if (!(Test-Path "manage.py")) {
    Write-Error "Este script debe ejecutarse desde la carpeta 'backend' donde está manage.py"
    exit 1
}

Write-Host "Configurando entorno para backup..." -ForegroundColor Cyan
$env:DATABASE_URL = $DatabaseUrl
$env:PYTHONUTF8 = "1"

Write-Host "Iniciando exportación de datos (esto puede tardar unos segundos)..." -ForegroundColor Cyan
# Excluímos contenttypes y auth.permission para evitar conflictos al importar
# Excluímos admin.logentry para reducir tamaño si no es crítico
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude admin.logentry --indent 2 --output backup_full.json

if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item "backup_full.json").Length / 1KB
    Write-Host "¡Backup completado exitosamente!" -ForegroundColor Green
    Write-Host "Archivo: $(Get-Location)\backup_full.json" -ForegroundColor Green
    Write-Host "Tamaño: $([math]::Round($size, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "Hubo un error al realizar el backup. Verifica tu URL de conexión." -ForegroundColor Red
}
