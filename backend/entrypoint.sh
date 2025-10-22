#!/bin/bash
set -e

echo "=================================================="
echo "ðŸ³ DevTrack Backend - InicializaciÃ³n"
echo "=================================================="

# Obtener valores de variables de entorno
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

echo "ðŸ”„ Esperando a que MySQL estÃ© disponible en ${DB_HOST}:${DB_PORT}..."
./wait-for-it.sh ${DB_HOST}:${DB_PORT} --timeout=60 --strict -- echo "âœ… MySQL estÃ¡ listo!"

echo ""
echo "ðŸ”„ Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

echo ""
echo "ðŸ”„ Recolectando archivos estÃ¡ticos..."
python manage.py collectstatic --noinput --clear || echo "âš ï¸  collectstatic fallÃ³ (puede ser normal en desarrollo)"

echo ""
echo "âœ… InicializaciÃ³n completada exitosamente!"
echo "=================================================="
echo "ðŸš€ Iniciando servidor Django..."
echo "=================================================="
echo ""

# Ejecutar el comando que se pase como argumento (CMD en Dockerfile)
exec "$@"
