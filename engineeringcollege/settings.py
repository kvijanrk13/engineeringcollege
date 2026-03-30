# ================================
# SETTINGS.PY (FINAL WORKING VERSION)
# ================================

from pathlib import Path
import os
import cloudinary
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# ✅ ENV DETECTION
# ================================
ON_RENDER = 'RENDER' in os.environ or 'DATABASE_URL' in os.environ
print(f"[DEBUG] ON_RENDER = {ON_RENDER}")

# ================================
# SECURITY
# ================================
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

ALLOWED_HOSTS = ['*'] if DEBUG else ['.onrender.com']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

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
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'engineeringcollege.urls'

# ================================
# ✅ TEMPLATES (FIXED)
# ================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # ✅ REQUIRED
                'django.contrib.auth.context_processors.auth',  # ✅ REQUIRED
                'django.contrib.messages.context_processors.messages',  # ✅ REQUIRED
            ],
        },
    },
]

WSGI_APPLICATION = 'engineeringcollege.wsgi.application'

# ================================
# DATABASE
# ================================
if ON_RENDER:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
    print("[OK] PostgreSQL connected")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("[OK] SQLite connected")

# ================================
# PASSWORD VALIDATION (SAFE DEFAULT)
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# ================================
# STATIC FILES (WHITENOISE)
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================
# MEDIA / CLOUDINARY
# ================================
MEDIA_URL = '/media/'

if ON_RENDER:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
)

# ================================
# AUTH REDIRECTS (OPTIONAL BUT GOOD)
# ================================
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ================================
# TIMEZONE
# ================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ================================
# DEFAULT PRIMARY KEY
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'