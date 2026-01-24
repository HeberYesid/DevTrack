#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "Python version:"
python --version

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Verifying database adapters..."
# Check if psycopg2 or psycopg (v3) is available
if python -c "import psycopg2" 2>/dev/null; then
    echo "psycopg2 OK"
elif python -c "import psycopg" 2>/dev/null; then
    echo "psycopg (v3) OK"
else
    echo "ERROR: Neither psycopg2 nor psycopg found in environment"
    python -m pip list
    exit 1
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
# NOTE: Migrations run automatically via Pre-Deploy Command in Render
