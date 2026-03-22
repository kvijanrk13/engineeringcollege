# start_server.py
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
    try:
        django.setup()
        print("Django initialized successfully")
        execute_from_command_line(['manage.py', 'runserver'])
    except SystemExit:
        pass  # Normal for runserver
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
