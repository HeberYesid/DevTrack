#!/usr/bin/env bash
# Startup script for Render - ejecuta migraciones y luego inicia el servidor

set -o errexit

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

email = 'admin@devtrack.com'
password = 'admin123'

if not User.objects.filter(email=email).exists():
    user = User.objects.create(
        username=email,
        email=email,
        first_name='Admin',
        last_name='DevTrack',
        role='ADMIN',
        is_staff=True,
        is_superuser=True,
        is_email_verified=True
    )
    user.set_password(password)
    user.save()
    print(f'✅ Superuser created: {email} / {password}')
    print('⚠️  IMPORTANT: Change password after first login!')
else:
    print(f'✅ Superuser already exists: {email}')
" || echo "⚠️ Superuser creation skipped"

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
