#!/bin/bash
source /opt/venv/bin/activate
cd backend

# Check environment variables for debugging
echo "🔍 Verificando variables de entorno..."
python check_env.py

# Try migrations, but don't fail if DB is not configured yet
python manage.py migrate --noinput || echo "Skipping migrations (DB not configured)"

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file -
