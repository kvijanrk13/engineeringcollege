# dashboard/apps.py
from django.apps import AppConfig
from django.db import connection
import os


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # Only run on Render, not locally
        if os.environ.get('RENDER', False) == 'True':
            self.add_pdf_url_column()

    def add_pdf_url_column(self):
        """Add pdf_url column if it doesn't exist"""
        try:
            with connection.cursor() as cursor:
                # Check if column exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' 
                    AND column_name='pdf_url'
                """)

                if not cursor.fetchone():
                    cursor.execute("""
                        ALTER TABLE dashboard_student 
                        ADD COLUMN pdf_url varchar(200) NULL
                    """)
                    print("✅ Added pdf_url column via AppConfig")
                else:
                    print("✅ pdf_url column already exists")
        except Exception as e:
            print(f"⚠️ Could not add pdf_url column: {e}")