# dashboard/startup.py
from django.db import connection
import os


def check_pdf_url_column():
    """Check if pdf_url column exists and add it if missing"""
    try:
        with connection.cursor() as cursor:
            # Check database type
            db_engine = connection.vendor
            print(f"[CHECKING] pdf_url column on {db_engine}...")

            # Check if column exists
            if db_engine == 'postgresql':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' AND column_name='pdf_url'
                """)
                exists = cursor.fetchone() is not None
            else:  # sqlite
                cursor.execute("PRAGMA table_info(dashboard_student)")
                columns = cursor.fetchall()
                exists = any(col[1] == 'pdf_url' for col in columns)

            if not exists:
                print("[WARNING] pdf_url column missing! Adding it now...")
                cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                print("[SUCCESS] pdf_url column added successfully!")
            else:
                print("[SUCCESS] pdf_url column already exists!")
    except Exception as e:
        print(f"[ERROR] Error checking/adding pdf_url column: {e}")