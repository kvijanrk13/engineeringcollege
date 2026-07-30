"""Settings used only by the automated Django test suite."""

from .settings import *  # noqa: F403


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
SECURE_SSL_REDIRECT = False

# The project contains large production data migrations, including a historical
# student seed that cannot run against a fresh Django test state. Unit and view
# tests need schemas, not production seed data, so these apps use syncdb in tests.
MIGRATION_MODULES = {
    "car_price_app": None,
    "dashboard": None,
    "library": None,
    "student": None,
}
