#!/usr/bin/env bash
# Startup script for Render - ejecuta migraciones y luego inicia el servidor

set -o errexit

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(email='admin@devtrack.com').exists():
    User.objects.create_superuser(
        email='admin@devtrack.com',
        first_name='Admin',
        last_name='DevTrack',
        password='admin123',
        role='ADMIN'
    )
    print('Superuser created: admin@devtrack.com / admin123')
else:
    print('Superuser already exists')
" || echo "Superuser creation skipped"

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
