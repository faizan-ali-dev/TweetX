#!/bin/bash
cd tweetx
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn tweetx.wsgi:application --bind 0.0.0.0:8000
