import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty
from django.test import RequestFactory
from dashboard.views import generate_faculty_pdf
from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
settings.ALLOWED_HOSTS.append('testserver')

faculty = Faculty.objects.first()
print(f"Testing for faculty: {faculty.employee_code}")

rf = RequestFactory()
request = rf.get(f'/faculty/{faculty.employee_code}/pdf/', HTTP_HOST='testserver')
request.user = type('User', (), {'is_authenticated': True, 'username': 'test'})()
setattr(request, 'session', 'session')
messages = FallbackStorage(request)
setattr(request, '_messages', messages)

response = generate_faculty_pdf(request, faculty.id)
print("Done. Response status:", response.status_code)
