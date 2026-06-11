# dashboard/apps.py

from django.apps import AppConfig
import sys
import os


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        """
        Safe startup initialization (NON-BLOCKING & RUNS ONCE)
        """
        # Skip the parent manage.py process when autoreloading, but allow real web and WSGI startup.
        if os.path.basename(sys.argv[0]) in ('manage.py', 'django-admin.py', 'django-admin') and os.environ.get('RUN_MAIN') != 'true':
            return

        # Skip during common management commands
        skip_commands = ['migrate', 'makemigrations', 'shell', 'collectstatic',
                         'flush', 'test', 'createsuperuser', 'changepassword', 'check']
        for cmd in skip_commands:
            if cmd in sys.argv:
                return

        try:
            # Import and run the startup checks
            from .startup import check_pdf_url_column, ensure_default_admin_user
            check_pdf_url_column()
            ensure_default_admin_user()
            
            # Connect Django signals for automatic student profile initialization
            import dashboard.signals  # noqa
        except Exception:
            # Don't let startup errors crash the server
            pass
