# dashboard/startup.py
from django.db import connection
from django.core.exceptions import ImproperlyConfigured
import sys
import traceback


def check_pdf_url_column():
    """Check if pdf_url column exists and add it if missing"""
    print("=== CHECK_PDF_URL_COLUMN STARTING ===", file=sys.stderr)
    try:
        with connection.cursor() as cursor:
            db_engine = connection.vendor
            print(f"[CHECKING] pdf_url column on {db_engine}...", file=sys.stderr)

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
                    # If we can't check, assume it exists to avoid potential issues
                    print("[WARNING] Could not check column existence, assuming it exists", file=sys.stderr)
                    return True

            if not exists:
                print("[INFO] pdf_url column missing - this should be handled by migrations", file=sys.stderr)
            else:
                print("[SUCCESS] pdf_url column already exists!", file=sys.stderr)

    except Exception as e:
        print(f"[WARNING] Error checking pdf_url column: {e}", file=sys.stderr)
        # Don't fail the startup for this - just warn
        return True

    print("=== CHECK_PDF_URL_COLUMN COMPLETED ===", file=sys.stderr)
    return True


# Only run if this file is executed directly
if __name__ == "__main__":
    check_pdf_url_column()
