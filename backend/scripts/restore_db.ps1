param(
    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl
)

# Asegurarnos de estar en el directorio correcto
if (!(Test-Path "manage.py")) {
    Write-Error "Este script debe ejecutarse desde la carpeta 'backend' donde está manage.py"
    exit 1
}

if (!(Test-Path "backup_full.json")) {
    Write-Error "No se encuentra el archivo 'backup_full.json'. Asegúrate de haber realizado el backup primero."
    exit 1
}

Write-Host "Configurando entorno para restauración..." -ForegroundColor Cyan
$env:DATABASE_URL = $DatabaseUrl
$env:PYTHONUTF8 = "1"

Write-Host "1. Aplicando migraciones para crear estructura de base de datos..." -ForegroundColor Cyan
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error al aplicar migraciones. Verifica tu URL de conexión."
    exit 1
}

Write-Host "2. Importando datos desde backup_full.json..." -ForegroundColor Cyan
# Usamos loaddata para cargar los datos
python manage.py loaddata backup_full.json

if ($LASTEXITCODE -eq 0) {
    Write-Host "¡Restauración completada exitosamente!" -ForegroundColor Green
} else {
    Write-Host "Hubo errores durante la importación." -ForegroundColor Red
}
