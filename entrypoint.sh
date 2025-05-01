#!/bin/bash
set -e

echo ">> Rodando migrações do Django..."
python manage.py migrate --noinput

echo ">> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo ">> Criando superusuário (admin@admin.com)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="admin@admin.com").exists():
    User.objects.create_superuser(
        email="admin@admin.com",
        password="admin",
        nome="Admin"
    )
EOF

echo ">> Iniciando servidor Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8080
