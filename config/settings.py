# ------------------------------------
# Imports e utilidades
# ------------------------------------
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url
from datetime import timedelta
# from distutils.util import strtobool
from corsheaders.defaults import default_headers

load_dotenv()  # Carrega variáveis de ambiente do .env

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------
# Configurações básicas
# ------------------------------------

# DEBUG
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Ajuste para SECRET_KEY durante o build (collectstatic)


# SECRET_KEY
if 'collectstatic' in sys.argv:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dummy-secret-key-for-collectstatic')
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'dummy-allowed-hosts').split(',')
else:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY não definida no ambiente!")

    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')
    if not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS não definidos no ambiente!")
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(',')


# ------------------------------------
# Aplicativos
# ------------------------------------
INSTALLED_APPS = [
    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'corsheaders',
    'rest_framework',

    # Aplicações locais
    'apps.agenda',
    'apps.usuario',
    'apps.servicos',
]

# ------------------------------------
# Middleware
# ------------------------------------
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

# ------------------------------------
# URLs e WSGI
# ------------------------------------
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ------------------------------------
# Templates
# ------------------------------------
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

# ------------------------------------
# Banco de Dados
# ------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# ------------------------------------
# Arquivos estáticos e mídia
# ------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ------------------------------------
# Usuário customizado
# ------------------------------------
AUTH_USER_MODEL = 'usuario.Usuario'

# ------------------------------------
# Validação de senha
# ------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------
# Internacionalização
# ------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ------------------------------------
# Django REST Framework
# ------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': None,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.usuario.auth.authentication.CookieJWTAuthentication',
    ],
}

# ------------------------------------
# JWT (Simple JWT)
# ------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=60),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_OBTAIN_SERIALIZER": "apps.usuario.serializers_auth.CustomTokenObtainPairSerializer",
}

# ------------------------------------
# Cookies e segurança para Safari/iOS
# ------------------------------------
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CSRF: origens confiáveis (Next.js, deploy, etc.)
CSRF_TRUSTED_ORIGINS = [
    "https://sellet.up.railway.app",
    "http://localhost:3000",
    "https://hml.selletesmalteria.com.br",
    "https://selletesmalteria.com.br",
]

# Segurança extra HTTP
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG

# ------------------------------------
# CORS
# ------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://hml.selletesmalteria.com.br",
    "https://selletesmalteria.com.br",
]
CORS_ALLOW_ORIGIN_REGEXES = [
    r"^https://.*\.selletesmalteria\.com\.br$"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'access-control-allow-origin',
    'access-control-allow-credentials',
]

# ------------------------------------
# Logging
# ------------------------------------
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
        "level": "DEBUG" if DEBUG else "INFO",
    },
}
