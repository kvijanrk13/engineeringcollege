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

# SECURITY: Fail fast if DEBUG=True in production (when SECRET_KEY is not the default dev key)
if not DEBUG and os.environ.get('SECRET_KEY', '').startswith('django-insecure-dev-key'):
    raise RuntimeError("SECURITY ERROR: Production SECRET_KEY must be set!")

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-for-local-development-only'
)

# SECURITY: Validate SECRET_KEY strength in production
if not DEBUG:
    if len(SECRET_KEY) < 50:
        raise RuntimeError("SECURITY ERROR: Production SECRET_KEY must be at least 50 characters!")
    if SECRET_KEY == 'django-insecure-dev-key-for-local-development-only':
        raise RuntimeError("SECURITY ERROR: Default SECRET_KEY detected in production!")

# ================================
# COLLEGE SETTINGS
# ================================
COLLEGE_NAME = os.environ.get('COLLEGE_NAME', 'Engineering College')
DEPARTMENT_NAME = os.environ.get('DEPARTMENT_NAME', 'Information Technology')
ACADEMIC_YEAR = os.environ.get('ACADEMIC_YEAR', '2026-2027')

# ================================
# GOOGLE SIGN-IN SETTINGS
# ================================
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
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

# ================================
# ALLOWED HOSTS - SECURITY: Restrict to specific domains only
# ================================
# Never use ['*'] in production! Explicitly list allowed domains.
# Get from environment variable, comma-separated
_allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if _allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]
else:
    # Default for local development only
    if DEBUG:
        ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
    else:
        # Production fallback - still restrict, don't use '*'
        ALLOWED_HOSTS = [
            '.onrender.com',
            'kvkprojects.onrender.com',
            'anrkitdept.onrender.com',
            'engineeringcollege.onrender.com',
        ]

# SECURITY: Validate ALLOWED_HOSTS in production
if not DEBUG and ('*' in ALLOWED_HOSTS or len(ALLOWED_HOSTS) == 0):
    raise RuntimeError("SECURITY ERROR: ALLOWED_HOSTS must be explicitly set in production!")

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://kvkprojects.onrender.com',
    'https://anrkitdept.onrender.com',
    'https://engineeringcollege.onrender.com',
]

# Add any additional CSRF trusted origins from environment
_csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if _csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([h.strip() for h in _csrf_origins_env.split(',') if h.strip()])

# ================================
# SSL / SECURITY SETTINGS - HARDENED
# ================================
# Trust the X-Forwarded-Proto header from Render's load balancer
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Force HTTPS in production - cannot be disabled via env var
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS - Force browser to use HTTPS for 1 year (31536000 seconds)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Prevent MIME type sniffing
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Prevent clickjacking - deny framing
    SECURE_FRAME_DENY = True  # Django 4.0+
    X_FRAME_OPTIONS = 'DENY'
    
    # Referrer Policy - strict origin when cross-origin
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    
    # Cross-Origin Opener Policy - isolate browsing context
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    
    # Cross-Origin Resource Policy - restrict resources
    SECURE_CROSS_ORIGIN_RESOURCE_POLICY = 'same-origin'
    
    # Permissions Policy - restrict browser features
    PERMISSIONS_POLICY = {
        'accelerometer': '()',
        'camera': '()',
        'geolocation': '()',
        'gyroscope': '()',
        'magnetometer': '()',
        'microphone': '()',
        'payment': '()',
        'usb': '()',
    }
    
    # Cookie security
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SAMESITE = 'Strict'
    
    # Session security
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_COOKIE_AGE = 3600  # 1 hour
    SESSION_SAVE_EVERY_REQUEST = True
    
    # CSRF protection
    CSRF_USE_SESSIONS = True  # Store CSRF token in session instead of cookie
    CSRF_COOKIE_AGE = 3600
    
else:
    # Development settings - less strict but still secure
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

# ================================
# CONTENT SECURITY POLICY (CSP)
# ================================
# Strict CSP to prevent XSS attacks
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", 'https://apis.google.com', 'https://www.google.com', 'https://www.gstatic.com'],
        'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://fonts.gstatic.com'],
        'img-src': ["'self'", 'data:', 'https:', 'https://res.cloudinary.com', 'https://anurag.ac.in'],
        'font-src': ["'self'", 'https://fonts.gstatic.com', 'https://fonts.googleapis.com', 'data:'],
        'connect-src': ["'self'", 'https://api.cloudinary.com', 'https://res.cloudinary.com'],
        'frame-src': ["'self'", 'https://accounts.google.com', 'https://www.google.com'],
        'form-action': ["'self'"],
        'frame-ancestors': ["'none'"],
        'base-uri': ["'self'"],
        'object-src': ["'none'"],
    }
}

# CSP for report-only mode in development
if DEBUG:
    CONTENT_SECURITY_POLICY['REPORT_ONLY'] = True

# ================================
# ADDITIONAL SECURITY HEADERS
# ================================
# Feature Policy / Permissions Policy (already set above)

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

    'csp',  # Content Security Policy middleware
    'cloudinary',
    'cloudinary_storage',
    'django_extensions',

    'dashboard',
    'car_price_app',

    'library',
    'student',
    'etors',
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    # Security middleware must be first
    'django.middleware.security.SecurityMiddleware',
    
    # CSP middleware - after SecurityMiddleware, before others
    'csp.middleware.CSPMiddleware',
    
    # WhiteNoise for static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Custom middleware
    'dashboard.middleware.DatabaseConnectionRetryMiddleware',
    
    # Standard Django middleware
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
        conn_max_age=int(os.environ.get('DATABASE_CONN_MAX_AGE', '0')),
        conn_health_checks=True,
        ssl_require=True
    )
}

print("Using PostgreSQL Database")

# ================================
# ADMIN SECURITY - Obfuscate admin URL
# ================================
# Change admin URL from default '/admin/' to something unpredictable
# Set ADMIN_URL in environment variable for production
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin-panel-secure-2026/')

# ================================
# PASSWORD VALIDATION - ENHANCED
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased from 8 to 12
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Custom: Require uppercase, lowercase, digit, special char
    {
        'NAME': 'dashboard.validators.ComplexityValidator',
    },
]

# ================================
# FILE UPLOAD SECURITY
# ================================
# Restrict file uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Allowed upload extensions (configure in views/forms)
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.webp']
ALLOWED_UPLOAD_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/png', 'image/jpeg', 'image/gif', 'image/webp',
]

# ================================
# SECURITY LOGGING - ENHANCED
# ================================
LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': 'SECURITY {levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'security_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'security',
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

        # Security-specific loggers
        'django.security': {
            'handlers': ['security_console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['security_console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'django.security.csrf': {
            'handlers': ['security_console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'csp': {
            'handlers': ['security_console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ================================
# RATE LIMITING (if django-ratelimit installed)
# ================================
# RATELIMIT_ENABLE = True
# RATELIMIT_USE_CACHE = 'default'
# RATELIMIT_VIEW = 'dashboard.views.ratelimited_view'

# ================================
# CACHING FOR RATE LIMITING
# ================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ================================
# SECURE DEFAULTS FOR FORMS
# ================================
# Ensure forms use CSRF by default
CSRF_FAILURE_VIEW = 'dashboard.views.csrf_failure'

# ================================
# AEC LIBRARY (django-library-management integrated at /aeclibrary/)
# ================================
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "").strip()
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
# Force fresh render deploy to clear template/static cache.
MOOCS_DEPLOY_TIMESTAMP = "2026-10-02T20-37"
