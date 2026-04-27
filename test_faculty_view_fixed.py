#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from dashboard.models import Faculty
from dashboard.views import generate_faculty_pdf
import traceback

def test_faculty_pdf_view(faculty_id=100):
    try:
        faculty = Faculty.objects.get(id=faculty_id)
        print(f"Testing faculty PDF view for: {faculty.staff_name} (ID: {faculty.id})")
        
        # Create a fake request with all needed middleware
        factory = RequestFactory()
        request = factory.get(f'/faculty/pdf/{faculty_id}/')
        
        # Add user
        try:
            user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            user = User.objects.create_user(username='testuser', password='testpass', is_staff=True, is_superuser=True)
        request.user = user
        
        # Add messages middleware support
        setattr(request, '_messages', FallbackStorage(request))
        
        # Call the view
        print("Calling generate_faculty_pdf view...")
        response = generate_faculty_pdf(request, faculty_id)
        
        if response and hasattr(response, 'content') and len(response.content) > 100:
            output_file = f"view_test_faculty_{faculty.employee_code}.pdf"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"SUCCESS: PDF generated: {output_file} ({len(response.content)} bytes)")
            print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
            print(f"Content-Disposition: {response.get('Content-Disposition', 'N/A')}")
            return True
        else:
            print(f"FAILED: Invalid response type: {type(response)}")
            if hasattr(response, 'status_code'):
                print(f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAILED with exception: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_faculty_pdf_view(100)
    sys.exit(0 if success else 1)