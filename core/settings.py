"""
Django settings for core project.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

# Adicionar host do Render automaticamente
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',  # Documentação Swagger
    # Local apps
    'profissionais',
    'consultas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'test_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configurações específicas para produção
if not DEBUG:
    # Para produção, evitar problemas com arquivos estáticos
    STATICFILES_DIRS = []
    # Desativar a interface web do Swagger para evitar erros de arquivos estáticos
    SWAGGER_UI = False
else:
    # Em desenvolvimento, permitir arquivos estáticos locais
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Em desenvolvimento, habilitar a interface web do DRF
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
        'rest_framework.permissions.AllowAny',
    ]

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Swagger Settings - Configuração para produção
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token JWT no formato: Bearer <token>'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'DOC_EXPANSION': 'none',
    'DEFAULT_MODEL_RENDERING': 'example',
    'VALIDATOR_URL': None,  # Desativa validação
}

# Configuração específica para produção - desativar UI do Swagger se necessário
if not DEBUG:
    SWAGGER_SETTINGS.update({
        'USE_SESSION_AUTH': False,
        'VALIDATOR_URL': None,
        'SHOW_REQUEST_HEADERS': True,
        'OPERATIONS_SORTER': 'alpha',
        'TAGS_SORTER': 'alpha',
        'DOC_EXPANSION': 'none',
        'DEEP_LINKING': True,
        'PERSIST_AUTHORIZATION': True,
        'DISPLAY_OPERATION_ID': False,
    })
    
    # Forçar uso de CDN para recursos do Swagger em produção
    SWAGGER_SETTINGS['DEFAULT_API_URL'] = None

# Configurações de logging para debug
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Configuração de segurança para produção
if not DEBUG:
    # Security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS PARA CI/TESTES
# =============================================================================

# No seu settings.py, na seção de configurações CI, adicione:
if os.environ.get('GITHUB_ACTIONS') == 'true' or os.environ.get('CI') == 'true':
    print("=== Ambiente CI detectado ===")
    
    # SOLUÇÃO DEFINITIVA: Desativa completamente redirecionamentos
    APPEND_SLASH = False
    DEBUG = False
    PREPEND_WWW = False
    
    # DESATIVA redirecionamentos SSL
    SECURE_SSL_REDIRECT = False
    SECURE_REDIRECT_EXEMPT = [r'.*']  # Exempt all URLs from redirect
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
    # Configurações de banco
    DATABASES['default']['TEST'] = {
        'NAME': 'test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
    
    # Otimizações de performance
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    
    print("Configuração CI aplicada - Redirecionamentos SSL desativados")