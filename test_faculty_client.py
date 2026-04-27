#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from django.test import Client
from dashboard.models import Faculty

def test_faculty_pdf_via_client(faculty_id=100):
    try:
        faculty = Faculty.objects.get(id=faculty_id)
        print(f"Testing faculty PDF via test client for: {faculty.staff_name}")
        
        client = Client()
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            user = User.objects.create_user(username='testuser', password='testpass', is_staff=True, is_superuser=True)
        
        logged_in = client.login(username='testuser', password='testpass')
        print(f"Login successful: {logged_in}")
        
        url = f'/faculty/pdf/{faculty_id}/'
        print(f"Making request to: {url}")
        response = client.get(url)
        
        print(f"Response status: {response.status_code}")
        print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and response.get('Content-Type', '') == 'application/pdf':
            output_file = f"client_test_faculty_{faculty.employee_code}.pdf"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"SUCCESS: PDF saved to {output_file}")
            return True
        else:
            print(f"FAILED: Not a valid PDF response")
            print(f"Content preview: {response.content[:500]}")
            return False
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_faculty_pdf_via_client(100)
    sys.exit(0 if success else 1)