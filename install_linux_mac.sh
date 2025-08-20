#!/bin/bash
# =============================================================================
# SCRIPT DE INSTALACIÓN AUTOMÁTICA - DevTrack
# =============================================================================
# Este script automatiza la instalación completa del proyecto DevTrack
# para Linux/Mac. Ejecuta todos los pasos necesarios en orden.

echo ""
echo "====================================="
echo "  INSTALACION AUTOMATICA - DevTrack"
echo "====================================="
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no está instalado."
    echo "Por favor instala Python 3.11+ usando tu gestor de paquetes:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "[1/8] Python detectado correctamente"
echo ""

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "[2/8] Creando entorno virtual..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual"
        exit 1
    fi
else
    echo "[2/8] Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "[3/8] Activando entorno virtual..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo activar el entorno virtual"
    exit 1
fi

# Actualizar pip
echo "[4/8] Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias
echo "[5/8] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Error al instalar dependencias"
    echo ""
    echo "SOLUCION ALTERNATIVA para problemas con mysqlclient:"
    echo "1. Instala dependencias del sistema:"
    echo "   Ubuntu/Debian: sudo apt install default-libmysqlclient-dev build-essential"
    echo "   CentOS/RHEL: sudo yum install mysql-devel gcc gcc-c++"
    echo "   macOS: brew install mysql"
    echo ""
    echo "2. Instala dependencias básicas:"
    echo "   pip install django django-cors-headers pillow python-decouple whitenoise"
    echo ""
    exit 1
fi

# Configurar archivo .env
if [ ! -f ".env" ]; then
    echo "[6/8] Configurando variables de entorno..."
    cp .env.example .env
    echo "✓ Archivo .env creado desde .env.example"
    echo "⚠ Revisa y modifica .env si necesitas configuración específica"
else
    echo "[6/8] Archivo .env ya existe"
fi

# Ejecutar migraciones
echo "[7/8] Ejecutando migraciones de base de datos..."
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[ERROR] Error al ejecutar migraciones"
    exit 1
fi

# Crear datos de prueba
echo "[8/8] Creando datos de prueba..."
python manage.py create_sample_data
if [ $? -ne 0 ]; then
    echo "[ADVERTENCIA] Error al crear datos de prueba"
    echo "Puedes ejecutar manualmente: python manage.py create_sample_data"
fi

echo ""
echo "====================================="
echo "  INSTALACION COMPLETADA"
echo "====================================="
echo ""
echo "✅ Proyecto instalado correctamente"
echo ""
echo "PARA EJECUTAR EL SERVIDOR:"
echo "  python manage.py runserver"
echo ""
echo "USUARIOS DE PRUEBA CREADOS:"
echo "  - estudiante1 (contraseña: password123)"
echo "  - estudiante2 (contraseña: password123)"
echo "  - estudiante3 (contraseña: password123)"
echo "  - estudiante4 (contraseña: password123)"
echo "  - estudiante5 (contraseña: password123)"
echo ""
echo "PARA CREAR UN ADMIN:"
echo "  python manage.py createsuperuser"
echo ""
echo "URL DEL PROYECTO: http://127.0.0.1:8000"
echo ""
