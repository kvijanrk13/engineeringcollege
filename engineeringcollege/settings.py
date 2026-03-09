# engineeringcollege/settings.py - FIXED CLOUDINARY CONFIGURATION

from pathlib import Path
import os
import cloudinary
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.contrib.messages import constants as messages
from dotenv import load_dotenv

# Load environment variables from .env file - THIS MUST BE AT THE TOP
load_dotenv()

# ==================================================
# BASE DIRECTORY
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==================================================
# ENVIRONMENT DETECTION
# ==================================================

# Check if we're running on Render
ON_RENDER = os.environ.get('RENDER', False) == 'True'

# ==================================================
# SECURITY WARNING: don't run with debug turned on in production!
# ==================================================

# DEBUG must be defined BEFORE it's used
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# SECRET KEY - defined after DEBUG
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Only use default for local development
        SECRET_KEY = 'django-insecure-dev-key-for-local-development-only'
    else:
        raise ValueError("SECRET_KEY environment variable not set for production!")

# ==================================================
# ALLOWED HOSTS
# ==================================================

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
]

# Add the actual Render URL without wildcard for CSRF
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

if DEBUG:
    ALLOWED_HOSTS += ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# ==================================================
# APPLICATIONS
# ==================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # Local Apps
    'dashboard',
]

# ==================================================
# MIDDLEWARE
# ==================================================

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

# ==================================================
# ROOT URL CONFIG
# ==================================================

ROOT_URLCONF = 'engineeringcollege.urls'

# ==================================================
# TEMPLATES
# ==================================================

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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

# ==================================================
# WSGI
# ==================================================

WSGI_APPLICATION = 'engineeringcollege.wsgi.application'

# ==================================================
# DATABASE - FIXED Configuration
# ==================================================

# Initialize DATABASES dict
DATABASES = {}

if ON_RENDER:
    # On Render - use PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        DATABASES['default'] = dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    else:
        raise ImproperlyConfigured("DATABASE_URL environment variable not set on Render!")
else:
    # Local development - use SQLite (ALWAYS provide this)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Verify database configuration (this will always pass now)
if not DATABASES['default'].get('ENGINE'):
    raise ImproperlyConfigured(
        "Database ENGINE not configured properly. "
        "Please check your DATABASE_URL environment variable or local SQLite configuration."
    )

# Print database info for debugging (remove in production)
print(f"Database configured: ENGINE={DATABASES['default']['ENGINE']}")
print(f"ON_RENDER = {ON_RENDER}")

# ==================================================
# PASSWORD VALIDATION
# ==================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==================================================
# INTERNATIONALIZATION
# ==================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ==================================================
# STATIC FILES - WhiteNoise Configuration
# ==================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==================================================
# MEDIA FILES
# ==================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==================================================
# DEFAULT PRIMARY KEY
# ==================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================================================
# CLOUDINARY CONFIGURATION - FIXED
# ==================================================

# Get Cloudinary credentials from environment (loaded from .env file)
# DO NOT use default values - they must come from .env
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

# Check if Cloudinary is properly configured
CLOUDINARY_CONFIGURED = all([
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
])

# Configure Cloudinary only if all credentials exist
if CLOUDINARY_CONFIGURED:
    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
            'API_KEY': CLOUDINARY_API_KEY,
            'API_SECRET': CLOUDINARY_API_SECRET,
        }

        # Use Cloudinary for media files in production
        if ON_RENDER:
            DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

        print(f"[OK] Cloudinary configured successfully")
        print(f"      Cloud Name: {CLOUDINARY_CLOUD_NAME}")
        print(f"      API Key: {CLOUDINARY_API_KEY[:4]}...{CLOUDINARY_API_KEY[-4:]}")
        print(f"      API Secret: {'*' * 8}{CLOUDINARY_API_SECRET[-4:]}")
    except Exception as e:
        print(f"[ERROR] Cloudinary configuration error: {e}")
        CLOUDINARY_CONFIGURED = False
else:
    print("[WARNING] Cloudinary not configured - files will be saved locally only")
    if not CLOUDINARY_CLOUD_NAME:
        print("         - Missing CLOUDINARY_CLOUD_NAME (should be 'dsndirhuhe')")
    if not CLOUDINARY_API_KEY:
        print("         - Missing CLOUDINARY_API_KEY (should be '473455725389669')")
    if not CLOUDINARY_API_SECRET:
        print("         - Missing CLOUDINARY_API_SECRET")

# Make CLOUDINARY_CONFIGURED available in settings
# This is used by the is_cloudinary_configured function in views.py

# ==================================================
# SESSION CONFIGURATION (Important for Student Login)
# ==================================================

# Use database for session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ==================================================
# LOGIN REDIRECTS
# ==================================================

LOGIN_URL = 'dashboard:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'dashboard:login'

# ==================================================
# MESSAGE TAGS
# ==================================================

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ==================================================
# PRODUCTION SECURITY SETTINGS
# ==================================================

if ON_RENDER or not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Cookie security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'

    # Security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ==================================================
# LOGGING CONFIGURATION - REDUCED VERBOSITY
# ==================================================

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
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}