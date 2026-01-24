#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "Python version:"
python --version

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install psycopg2-binary "psycopg[binary]"

echo "Verifying database adapters..."
python -m pip list | grep psyc

# Try to import and log detail if it fails
python -c "import psycopg2; print('psycopg2 OK')" || \
python -c "import psycopg; print('psycopg (v3) OK')" || \
{ echo "ERROR: Database adapters not found in PYTHONPATH"; python -c "import sys; print(sys.path)"; python -m pip show psycopg2-binary "psycopg"; exit 1; }

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
# NOTE: Migrations run automatically via Pre-Deploy Command in Render
