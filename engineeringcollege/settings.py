# ================================
# SETTINGS.PY (UPDATED FOR RENDER)
# ================================

from pathlib import Path
import os
import cloudinary
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ================================
# ✅ ENV DETECTION
# ================================
ON_RENDER = 'RENDER' in os.environ or 'DATABASE_URL' in os.environ
print(f"[DEBUG] ON_RENDER = {ON_RENDER}")

# ================================
# SECURITY
# ================================
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Use environment variable for SECRET_KEY (required for Render)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-for-local-only')

# Allowed hosts for Render
default_hosts = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'engineeringcollege.onrender.com',
    'anrkitdept.onrender.com',
]
env_hosts = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',') if host.strip()]
ALLOWED_HOSTS = ['*'] if DEBUG else list(dict.fromkeys(default_hosts + env_hosts))

default_origins = [
    'https://*.onrender.com',
    'https://engineeringcollege.onrender.com',
    'https://anrkitdept.onrender.com',
]
env_origins = [origin.strip() for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(default_origins + env_origins))

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

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
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'engineeringcollege.urls'

# ================================
# ✅ TEMPLATES
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
            ],
        },
    },
]

WSGI_APPLICATION = 'engineeringcollege.wsgi.application'

# ================================
# DATABASE (PostgreSQL on Render, SQLite locally)
# ================================
if ON_RENDER:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
    print(f"[OK] PostgreSQL connected")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("[OK] SQLite connected")

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
# STATIC FILES (Whitenoise for production)
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

# Use WhiteNoise for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================
# MEDIA FILES (Cloudinary for production)
# ================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ================================
# CLOUDINARY CONFIGURATION (FIXED - No Circular Reference)
# ================================
CLOUDINARY_CONFIGURED = False

# Expose Cloudinary credentials as Django settings attributes.
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    try:
        CLOUDINARY_CONFIGURED = True
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        # Use Cloudinary for media storage in production
        if ON_RENDER:
            DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
            print("[OK] Cloudinary configured successfully (Render)")
        else:
            print("[OK] Cloudinary configured locally")

    except Exception as e:
        print(f"[ERROR] Cloudinary configuration failed: {e}")
        CLOUDINARY_CONFIGURED = False
else:
    if ON_RENDER:
        print("[WARNING] Cloudinary credentials not found - using local storage")
    else:
        print("[WARNING] Cloudinary not configured - using local storage")

# ================================
# AUTH REDIRECTS
# ================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ================================
# TIMEZONE & LANGUAGE
# ================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ================================
# DEFAULT PRIMARY KEY
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# FILE UPLOAD SETTINGS
# ================================
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# ================================
# LOGGING (for debugging on Render)
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
