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
        # Skip during management commands and non-main processes
        if os.environ.get('RUN_MAIN') != 'true':
            return

        # Skip during common management commands
        skip_commands = ['migrate', 'makemigrations', 'shell', 'collectstatic',
                         'flush', 'test', 'createsuperuser', 'changepassword', 'check']
        for cmd in skip_commands:
            if cmd in sys.argv:
                return

        # Only run the actual startup task for runserver command
        if 'runserver' in sys.argv:
            try:
                # Import and run the startup check
                from .startup import check_pdf_url_column
                result = check_pdf_url_column()
            except Exception as e:
                # Don't let startup errors crash the server
                pass
