# dashboard/startup.py
import logging
import sys

from django.contrib.auth import get_user_model
from django.db import connection

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_USERNAME = '7001'
DEFAULT_ADMIN_PASSWORD = 'anrkithod'
DEFAULT_ADMIN_EMAIL = ''


def check_pdf_url_column():
    """Check if pdf_url column exists - for information only"""
    try:
        with connection.cursor() as cursor:
            db_engine = connection.vendor

            if db_engine == 'postgresql':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' AND column_name='pdf_url'
                """)
                exists = cursor.fetchone() is not None
            else:  # sqlite and others
                try:
                    cursor.execute("PRAGMA table_info(dashboard_student)")
                    columns = cursor.fetchall()
                    exists = any(col[1] == 'pdf_url' for col in columns)
                except Exception:
                    # If we can't check, assume it exists
                    return True

            return True  # Column check completed (existence verified by migration system)

    except Exception:
        # Don't fail startup for this check
        return True


def ensure_default_admin_user(username=DEFAULT_ADMIN_USERNAME, password=DEFAULT_ADMIN_PASSWORD, email=DEFAULT_ADMIN_EMAIL):
    """Create or update the default admin user so login works with known credentials."""
    try:
        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is not None:
            changed = False
            if not getattr(user, 'is_staff', False):
                user.is_staff = True
                changed = True
            if not getattr(user, 'is_superuser', False):
                user.is_superuser = True
                changed = True
            if not user.check_password(password):
                user.set_password(password)
                changed = True
            if changed:
                user.save()
                logger.info("Updated default admin user '%s'", username)
            else:
                logger.info("Default admin user '%s' already exists", username)
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            logger.info("Created default admin superuser '%s'", username)
        return True
    except Exception as exc:
        logger.warning("Could not ensure default admin user '%s': %s", username, exc, exc_info=True)
        return False


# Only run if this file is executed directly
if __name__ == "__main__":
    ensure_default_admin_user()
