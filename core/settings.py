"""
Django settings for core project.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-key-for-dev-only-change-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Configuração de ALLOWED_HOSTS
allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(",")]

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
    'sslserver',  # Servidor SSL para desenvolvimento
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
        'NAME': os.getenv('POSTGRES_DB', 'lacrei_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'db'),
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
    "https://localhost:3000",
    "https://127.0.0.1:3000",
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
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'sslserver': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# CONFIGURAÇÕES SSL/HTTPS
# =============================================================================

# Configurações de segurança para HTTPS
SECURE_SSL_REDIRECT = False  # Deixar False pois o runsslserver já lida com HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configurar CSRF_TRUSTED_ORIGINS para HTTPS
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
    'https://*.amazonaws.com',
    'https://*.onrender.com'
]

# Adicionar automaticamente o IP do EC2 aos trusted origins
EC2_IP = os.environ.get('EC2_IP')
if EC2_IP:
    CSRF_TRUSTED_ORIGINS.extend([
        f'http://{EC2_IP}:8000',
        f'https://{EC2_IP}:8000'
    ])

# Adicionar hosts SSL aos allowed hosts
if not DEBUG:
    ALLOWED_HOSTS.extend([
        '*.amazonaws.com',
        '*.compute.amazonaws.com',
        '*.elasticbeanstalk.com',
        'ec2-*-*-*-*.compute-1.amazonaws.com'
    ])

# Configuração específica para SSL no desenvolvimento
if DEBUG:
    # Permitir acesso via IP no desenvolvimento
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0', '::1'])
    
    # Para desenvolvimento com SSL, desativar algumas verificações
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

# Configurações de segurança para produção
if not DEBUG:
    # Security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

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

# =============================================================================
# CONFIGURAÇÕES ADICIONAIS PARA SSL SERVER
# =============================================================================

# Configurações específicas para django-sslserver
SSL_PORT = 8000
SSL_CERTIFICATE = os.path.join(BASE_DIR, 'cert.pem')
SSL_PRIVATE_KEY = os.path.join(BASE_DIR, 'key.pem')

# Verificar se os arquivos de certificado existem
SSL_CERTIFICATE_EXISTS = os.path.exists(SSL_CERTIFICATE)
SSL_PRIVATE_KEY_EXISTS = os.path.exists(SSL_PRIVATE_KEY)

if SSL_CERTIFICATE_EXISTS and SSL_PRIVATE_KEY_EXISTS:
    print(f"✅ Certificado SSL encontrado: {SSL_CERTIFICATE}")
    print(f"✅ Chave privada SSL encontrada: {SSL_PRIVATE_KEY}")
else:
    print(f"⚠️  Certificado SSL não encontrado: {SSL_CERTIFICATE}")
    print(f"⚠️  Chave privada SSL não encontrada: {SSL_PRIVATE_KEY}")
    print("💡 Execute: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj \"/C=BR/ST=SaoPaulo/L=SaoPaulo/O=Lacrei/CN=localhost\"")

# Configuração de URLs seguras para Swagger/DRF
if SSL_CERTIFICATE_EXISTS and SSL_PRIVATE_KEY_EXISTS:
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

print(f"=== Configurações SSL Carregadas ===")
print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
print(f"SSL Certificate: {SSL_CERTIFICATE_EXISTS}")
print(f"SSL Private Key: {SSL_PRIVATE_KEY_EXISTS}")