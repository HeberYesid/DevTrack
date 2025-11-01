#!/bin/bash
cd backend
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file -
