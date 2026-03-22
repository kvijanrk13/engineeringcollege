# debug_server.py
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line


def debug_django_startup():
    print("=== DJANGO SERVER DEBUG ===")
    print("1. Setting up Django environment...")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')

    try:
        print("2. Initializing Django...")
        django.setup()
        print("3. Django initialized successfully!")

        print("4. Checking if runserver command exists...")
        from django.core.management import execute_from_command_line
        import django.core.management.commands.runserver as runserver_module

        print("5. About to execute runserver command...")
        # This should start the server
        execute_from_command_line(['manage.py', 'runserver', '--noreload'])

        print("6. Server command completed (this shouldn't happen normally)")

    except SystemExit as e:
        print(f"7. SystemExit caught with code: {e.code}")
        # This is normal for runserver
        pass
    except Exception as e:
        print(f"7. Error during startup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    debug_django_startup()
    print("8. Script finished")
