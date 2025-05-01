from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

import socket

# Força uso de IPv4 no Railway (evita o uso de IPv6 que está falhando)
def force_ipv4():
    original_getaddrinfo = socket.getaddrinfo

    def getaddrinfo_ipv4(*args, **kwargs):
        return [
            info for info in original_getaddrinfo(*args, **kwargs)
            if info[0] == socket.AF_INET
        ]

    socket.getaddrinfo = getaddrinfo_ipv4

# Só ativa no Railway
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_STATIC_URL"):
    force_ipv4()

# Carrega variáveis do .env
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS = [
    "https://sellet.up.railway.app"
]



# Aplicativos instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',

    'apps.agenda',
    'apps.usuario',
    'apps.servicos',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs e WSGI
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Banco de dados via Supabase (.env DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG  # SSL apenas se for produção
    )
}

# Usuário customizado
AUTH_USER_MODEL = 'usuario.Usuario'

# Validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"



# Configuração padrão do DRF
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': None,
}

# CORS para o frontend local
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]


# Segurança de cookies (obrigatório para HTTPS em produção)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Segurança de resposta (evita XSS e sniffing de MIME)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
