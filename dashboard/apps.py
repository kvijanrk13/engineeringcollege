# dashboard/apps.py
from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    def ready(self):
        try:
            from .startup import check_pdf_url_column
            check_pdf_url_column()
        except ImportError as e:
            print(f"⚠️ Could not import startup function: {e}")
        except Exception as e:
            print(f"⚠️ Error in startup: {e}")