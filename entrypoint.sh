#!/bin/bash
set -e

echo ">> Rodando migrações do Django..."
python manage.py migrate --noinput

echo ">> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo ">> Iniciando servidor Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8080
