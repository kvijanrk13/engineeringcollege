# dashboard/startup.py
from django.db import connection
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
            else:  # sqlite
                cursor.execute("PRAGMA table_info(dashboard_student)")
                columns = cursor.fetchall()
                exists = any(col[1] == 'pdf_url' for col in columns)

            if not exists:
                print("[WARNING] pdf_url column missing! Adding it now...", file=sys.stderr)
                cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                print("[SUCCESS] pdf_url column added successfully!", file=sys.stderr)
            else:
                print("[SUCCESS] pdf_url column already exists!", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Error checking/adding pdf_url column: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # Return False to indicate failure, but don't raise exception
        return False

    print("=== CHECK_PDF_URL_COLUMN COMPLETED ===", file=sys.stderr)
    return True


# Only run if this file is executed directly
if __name__ == "__main__":
    check_pdf_url_column()