@echo off
REM =============================================================================
REM SCRIPT DE INSTALACIÓN AUTOMÁTICA - DevTrack
REM =============================================================================
REM Este script automatiza la instalación completa del proyecto DevTrack
REM para Windows. Ejecuta todos los pasos necesarios en orden.

echo.
echo =====================================
echo   INSTALACION AUTOMATICA - DevTrack
echo =====================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo Por favor instala Python 3.11+ desde https://python.org
    pause
    exit /b 1
)

echo [1/8] Python detectado correctamente
echo.

REM Crear entorno virtual si no existe
if not exist ".venv" (
    echo [2/8] Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
) else (
    echo [2/8] Entorno virtual ya existe
)

REM Activar entorno virtual
echo [3/8] Activando entorno virtual...
call .venv\Scripts\activate
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Actualizar pip
echo [4/8] Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo [5/8] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Error al instalar dependencias
    echo.
    echo SOLUCION ALTERNATIVA para problemas con mysqlclient:
    echo 1. Instala dependencias básicas:
    echo    pip install django django-cors-headers pillow python-decouple whitenoise
    echo.
    echo 2. Para MySQL (opcional):
    echo    - Descarga mysqlclient desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
    echo    - Instala con: pip install nombre_del_archivo.whl
    echo.
    pause
    exit /b 1
)

REM Configurar archivo .env
if not exist ".env" (
    echo [6/8] Configurando variables de entorno...
    copy .env.example .env
    echo ✓ Archivo .env creado desde .env.example
    echo ⚠ Revisa y modifica .env si necesitas configuración específica
) else (
    echo [6/8] Archivo .env ya existe
)

REM Ejecutar migraciones
echo [7/8] Ejecutando migraciones de base de datos...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Error al ejecutar migraciones
    pause
    exit /b 1
)

REM Crear datos de prueba
echo [8/8] Creando datos de prueba...
python manage.py create_sample_data
if errorlevel 1 (
    echo [ADVERTENCIA] Error al crear datos de prueba
    echo Puedes ejecutar manualmente: python manage.py create_sample_data
)

echo.
echo =====================================
echo   INSTALACION COMPLETADA
echo =====================================
echo.
echo ✅ Proyecto instalado correctamente
echo.
echo PARA EJECUTAR EL SERVIDOR:
echo   python manage.py runserver
echo.
echo USUARIOS DE PRUEBA CREADOS:
echo   - estudiante1 (contraseña: password123)
echo   - estudiante2 (contraseña: password123)
echo   - estudiante3 (contraseña: password123)
echo   - estudiante4 (contraseña: password123)
echo   - estudiante5 (contraseña: password123)
echo.
echo PARA CREAR UN ADMIN:
echo   python manage.py createsuperuser
echo.
echo URL DEL PROYECTO: http://127.0.0.1:8000
echo.
pause
