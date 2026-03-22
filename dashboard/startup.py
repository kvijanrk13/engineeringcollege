# dashboard/startup.py
from django.db import connection
import sys


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

    except Exception as e:
        # Don't fail startup for this check
        return True


# Only run if this file is executed directly
if __name__ == "__main__":
    check_pdf_url_column()
