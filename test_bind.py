# test_bind.py
import os
import sys
import django
from django.core.management import execute_from_command_line


def test_server_binding():
    print("=== TESTING SERVER BINDING ===")

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')

    try:
        django.setup()
        print("✅ Django setup successful")

        # Try to manually create a simple HTTP server to test binding
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', 8000))
            print("✅ Successfully bound to 127.0.0.1:8000")
            sock.close()
        except Exception as e:
            print(f"❌ Failed to bind to 127.0.0.1:8000 - {e}")

        # Now try Django server
        print("🔧 Attempting to start Django server...")
        execute_from_command_line(['manage.py', 'runserver', '--noreload'])

    except SystemExit:
        print("✅ Server process completed normally")
    except Exception as e:
        print(f"❌ Server failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_server_binding()
