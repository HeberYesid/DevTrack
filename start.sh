#!/bin/bash
set -e  # Exit on error

source /opt/venv/bin/activate
cd backend

echo "🔍 Environment Check:"
echo "PORT: ${PORT:-not set}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-not set}"
echo "RAILWAY_PUBLIC_DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-not set}"

# Try migrations, but don't fail if DB is not configured yet
python manage.py migrate --noinput || echo "⚠️  Skipping migrations (DB not configured)"

# Collect static files
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn on 0.0.0.0:${PORT:-8000}"

# Start gunicorn with explicit configuration (ignore gunicorn.conf.py)
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 4 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  --capture-output
