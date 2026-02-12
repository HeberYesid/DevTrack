from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# PyMySQL solo se usa si se configura MySQL
if os.getenv('USE_MYSQL') == 'True':
    import pymysql
    pymysql.install_as_MySQLdb()

# Paths and env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')  # expects a .env file at backend/.env
load_dotenv(BASE_DIR.parent / '.env')  # also look in project root

# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

# ALLOWED_HOSTS configuration
# Temporarily allow all hosts for debugging Railway deployment
ALLOWED_HOSTS = ['*']
# allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '')
# if allowed_hosts_env:
#     # Split by comma for multiple hosts
#     ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',')]
# else:
#     # Default for development
#     ALLOWED_HOSTS = [
#         "localhost",
#         "127.0.0.1",
#         "devtrack-production-2b1d.up.railway.app",
#     ]
#     # Add Railway domain if available
#     railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
#     if railway_domain:
#         ALLOWED_HOSTS.append(railway_domain)


# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'csp',
    'drf_spectacular',
    'storages',

    'accounts',
    'courses.apps.CoursesConfig',
    'notifications.apps.NotificationsConfig',
    'messaging.apps.MessagingConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Sirve archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database configuration
# Soporta SQLite (local dev), MySQL o PostgreSQL (producción)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Render/Railway provee DATABASE_URL (PostgreSQL o MySQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True if 'postgresql' in DATABASE_URL else False
        )
    }
elif os.getenv('USE_MYSQL') == 'True':
    # MySQL para desarrollo (opcional)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'devtrack'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            }
        }
    }
else:
    # SQLite para desarrollo local (por defecto)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# R2 / S3 Configuration
USE_R2 = os.getenv('USE_R2', 'False') == 'True'

if USE_R2:
    # Cloudflare R2 Settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_QUERYSTRING_AUTH = True 
    AWS_S3_REGION_NAME = 'auto' 

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# DRF & JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

# API Schema
SPECTACULAR_SETTINGS = {
    'TITLE': 'DevTrack API',
    'DESCRIPTION': 'API para gestión académica, notas y reportes',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]

# En desarrollo local, permitir localhost y 127.0.0.1
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]

CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins (for Django admin and forms)
CSRF_TRUSTED_ORIGINS = [
    'https://devtrack-production-2b1d.up.railway.app',
    'https://*.railway.app',
]
# Add Railway domain if available
railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f"https://{railway_domain}")
# Add custom origins from env
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in csrf_origins_env.split(',') if o.strip()])

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'DevTrack <no-reply@devtrack.local>')

# Frontend/API base urls (for emails)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')

# Cache configuration for rate limiting
# Using LocMemCache for development (in production, use Redis or Memcached)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'devtrack-ratelimit',
    }
}

# Rate Limiting Configuration
# django-ratelimit uses this cache backend
RATELIMIT_ENABLE = os.getenv('RATELIMIT_ENABLE', 'True') == 'True'
RATELIMIT_USE_CACHE = 'default'

# Additional Security Settings (Production Ready)
# HTTPS/SSL Settings - Uncomment in production with HTTPS
# SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Cookie Security Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Use 'Strict' if same-origin only
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# CSRF Trusted Origins (CRÍTICO para producción)
CSRF_TRUSTED_ORIGINS = []
csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins.split(',')]
elif not DEBUG:
    # En producción sin CSRF_TRUSTED_ORIGINS explícito, usar ALLOWED_HOSTS
    CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host != '*']

# In production with HTTPS, uncomment:
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Content Security Policy (CSP)
# Define policies as tuple/list constants to support both old and new django-csp versions
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://accounts.google.com",
    "https://cdn.jsdelivr.net",
    "https://devtrack-production-2b1d.up.railway.app",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net",
)
CSP_IMG_SRC = ("'self'", "data:", "https://*", "https://cdn.jsdelivr.net")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com", "data:")
CSP_CONNECT_SRC = (
    "'self'",
    "https://accounts.google.com",
    "https://devtrack-production-2b1d.up.railway.app",
)
CSP_FRAME_SRC = ("'self'", "https://accounts.google.com")
CSP_WORKER_SRC = ("'self'", "blob:")

# Dictionary for django-csp 3.8+ (reuses above constants)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": CSP_DEFAULT_SRC,
        "script-src": CSP_SCRIPT_SRC,
        "style-src": CSP_STYLE_SRC,
        "img-src": CSP_IMG_SRC,
        "font-src": CSP_FONT_SRC,
        "connect-src": CSP_CONNECT_SRC,
        "frame-src": CSP_FRAME_SRC,
        "worker-src": CSP_WORKER_SRC,
    }
}

X_FRAME_OPTIONS = 'DENY'  # Already set by XFrameOptionsMiddleware
