# ================================
# SETTINGS.PY (POSTGRESQL + NEON)
# ================================

from pathlib import Path
import os
import cloudinary
import dj_database_url
from dotenv import load_dotenv

# ================================
# BASE DIRECTORY
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# LOAD ENV VARIABLES
# ================================
load_dotenv(BASE_DIR / '.env')

# ================================
# DJANGO SETTINGS
# ================================
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-for-local-development-only'
)

# ================================
# COLLEGE SETTINGS
# ================================
COLLEGE_NAME = os.environ.get('COLLEGE_NAME', 'Engineering College')
DEPARTMENT_NAME = os.environ.get('DEPARTMENT_NAME', 'Information Technology')
ACADEMIC_YEAR = os.environ.get('ACADEMIC_YEAR', '2026-2027')

# ================================
# GOOGLE SIGN-IN SETTINGS
# ================================
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '')

# ================================
# EMAIL SETTINGS
# ================================
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ecprj2026@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    EMAIL_HOST_USER or 'ecprj2026@gmail.com'
)

ALLOWED_HOSTS = [
    '*',
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'engineeringcollege.onrender.com',
    'anrkitdept.onrender.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://engineeringcollege.onrender.com',
    'https://anrkitdept.onrender.com',
]

# ================================
# SSL / SECURITY SETTINGS
# ================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG and os.environ.get('DISABLE_SSL_REDIRECT', 'False') != 'True':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ================================
# INSTALLED APPS
# ================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary',
    'cloudinary_storage',

    'dashboard',
    'car_price_app',
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ================================
# ROOT URL CONFIG
# ================================
ROOT_URLCONF = 'engineeringcollege.urls'

# ================================
# TEMPLATES
# ================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'dashboard.context_processors.college_info',
            ],
        },
    },
]

# ================================
# WSGI
# ================================
WSGI_APPLICATION = 'engineeringcollege.wsgi.application'

# ================================
# DATABASE (NEON POSTGRESQL)
# ================================
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL not found in .env"
    )

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
}

print("Using PostgreSQL Database")

# ================================
# PASSWORD VALIDATION
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ================================
# LANGUAGE / TIMEZONE
# ================================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# ================================
# STATIC FILES
# ================================
STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# ================================
# MEDIA FILES
# ================================
MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# ================================
# CLOUDINARY CONFIGURATION
# ================================
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')

CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')

CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

CLOUDINARY_CONFIGURED = bool(
    CLOUDINARY_CLOUD_NAME and
    CLOUDINARY_API_KEY and
    CLOUDINARY_API_SECRET
)

if CLOUDINARY_CONFIGURED:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )

    print("Cloudinary initialized successfully.")

# ================================
# LOGIN SETTINGS
# ================================
LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/dashboard/faculty/list/'

LOGOUT_REDIRECT_URL = '/admin-login/'

# ================================
# DEFAULT PRIMARY KEY
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# FILE UPLOAD SETTINGS
# ================================
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

# ================================
# LOGGING
# ================================
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
        'level': 'INFO',
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },

        'dashboard': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
