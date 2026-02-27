# test_pdf_url.py
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from django.contrib.auth import authenticate

def test_pdf_via_url(faculty_id=7001):
    print(f"\n{'='*60}")
    print(f"TESTING PDF GENERATION VIA URL")
    print(f"{'='*60}\n")
    
    # Create a client
    client = Client()
    
    # First, login to get session
    print("Attempting to login...")
    
    # You need to have a superuser or staff user
    # Let's try to create a test user if it doesn't exist
    from django.contrib.auth.models import User
    
    # Try to get an existing user
    user = User.objects.filter(is_staff=True).first()
    
    if not user:
        # Create a test user
        user = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            is_staff=True
        )
        print("Created test user: testadmin / testpass123")
    
    # Login
    login_success = client.login(username=user.username, password='testpass123')
    
    if login_success:
        print("✓ Login successful")
        
        # Now try to access the PDF URL
        url = f'/dashboard/faculty/{faculty_id}/pdf/'
        print(f"Accessing URL: {url}")
        
        response = client.get(url)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the PDF
            pdf_file = f"url_test_{faculty_id}.pdf"
            with open(pdf_file, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved to: {pdf_file}")
            print(f"  Content-Type: {response.get('Content-Type', 'N/A')}")
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response: {response.content[:200]}")
    else:
        print("✗ Login failed")

if __name__ == "__main__":
    test_pdf_via_url(7001)