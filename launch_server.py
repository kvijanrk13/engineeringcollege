# launch_server.py
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
    execute_from_command_line(['manage.py', 'runserver'])
