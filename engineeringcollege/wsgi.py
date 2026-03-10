"""
WSGI config for engineeringcollege project.
"""

import os
import sys
import traceback

# Print Python path for debugging
print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    from django.core.wsgi import get_wsgi_application
except Exception as e:
    print("ERROR importing Django:", e)
    traceback.print_exc()
    raise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')

try:
    application = get_wsgi_application()
    print("✅ WSGI application created successfully")
except Exception as e:
    print("❌ Failed to create WSGI application:", e)
    traceback.print_exc()
    raise