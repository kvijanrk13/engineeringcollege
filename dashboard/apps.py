# dashboard/apps.py
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # Import here to avoid circular imports
        from .startup import check_pdf_url_column
        check_pdf_url_column()