# dashboard/apps.py
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        """
        Initialize startup checks when Django is ready
        """
        try:
            # Import here to avoid AppRegistryNotReady error
            from .startup import check_pdf_url_column
            check_pdf_url_column()
        except Exception as e:
            print(f"[ERROR] Error in startup: {e}")