#!/bin/bash
set -e

echo "=================================================="
echo "🐳 DevTrack Backend - Inicialización"
echo "=================================================="

# Obtener valores de variables de entorno
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

echo "🔄 Esperando a que MySQL esté disponible en ${DB_HOST}:${DB_PORT}..."
./wait-for-it.sh ${DB_HOST}:${DB_PORT} --timeout=60 --strict -- echo "✅ MySQL está listo!"

echo ""
echo "🔄 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

echo ""
echo "🔄 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear || echo "⚠️  collectstatic falló (puede ser normal en desarrollo)"

echo ""
echo "✅ Inicialización completada exitosamente!"
echo "=================================================="
echo "🚀 Iniciando servidor Django..."
echo "=================================================="
echo ""

# Ejecutar el comando que se pase como argumento (CMD en Dockerfile)
exec "$@"
