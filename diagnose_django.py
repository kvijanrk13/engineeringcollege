# diagnose_django.py
import os
import sys
import django
from django.conf import settings
from django.db import connection


def debug_startup():
    print("=== DJANGO DIAGNOSTIC STARTUP ===")
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

    try:
        django.setup()
        print("1. Django setup completed successfully!")
    except Exception as e:
        print(f"1. Django setup FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    print("2. Settings summary:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
    print(f"   DATABASE HOST: {settings.DATABASES['default'].get('HOST')}")
    print(f"   DATABASE NAME: {settings.DATABASES['default'].get('NAME')}")
    print(f"   DATABASE USER: {settings.DATABASES['default'].get('USER')}")

    print("3. Checking database connectivity...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"   Database connected successfully, SELECT 1 -> {result}")
    except Exception as e:
        print(f"   Database connection FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
    debug_startup()
