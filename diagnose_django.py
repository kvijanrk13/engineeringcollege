# diagnose_django.py
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line


def debug_startup():
    print("=== DJANGO DIAGNOSTIC STARTUP ===")
    print("1. About to setup Django...")

    try:
        django.setup()
        print("2. Django setup completed successfully!")
    except Exception as e:
        print(f"2. Django setup FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    print("3. About to run server...")
    try:
        execute_from_command_line(['manage.py', 'runserver'])
        print("4. Server command completed!")
    except Exception as e:
        print(f"4. Server command FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
    debug_startup()
