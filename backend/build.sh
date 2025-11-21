#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "Python version:"
python --version

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Verifying psycopg2 installation..."
python -c "import psycopg2; print('psycopg2 OK')" || python -c "import psycopg; print('psycopg OK')"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
# NOTE: Migrations run automatically via Pre-Deploy Command in Render
