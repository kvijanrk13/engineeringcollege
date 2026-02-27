# test_pdf_url_fixed.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from dashboard.models import Faculty

def test_pdf_url(faculty_id=7001):
    print(f"\n{'='*60}")
    print(f"TESTING PDF GENERATION VIA URL")
    print(f"{'='*60}\n")
    
    # Create a client
    client = Client()
    
    # First, let's check if faculty exists
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        print(f"✓ Faculty found: {faculty.staff_name}")
    except Faculty.DoesNotExist:
        print(f"✗ Faculty with code {faculty_id} not found")
        return
    
    # Try to get an existing superuser
    user = User.objects.filter(is_superuser=True).first()
    
    if not user:
        user = User.objects.filter(is_staff=True).first()
    
    if not user:
        # Create a test superuser
        print("No admin user found. Creating test superuser...")
        user = User.objects.create_superuser(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
        print("✓ Created test superuser: testadmin / testpass123")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # Login
    login_success = client.login(username=user.username, password='testpass123')
    
    if not login_success and user.username != 'testadmin':
        # Try with a different password
        print("Login failed. Trying to set password...")
        user.set_password('testpass123')
        user.save()
        login_success = client.login(username=user.username, password='testpass123')
    
    if login_success:
        print("✓ Login successful")
        
        # Now try to access the PDF URL
        url = f'/dashboard/faculty/{faculty.id}/pdf/'
        print(f"Accessing URL: {url}")
        
        response = client.get(url)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Save the PDF
            pdf_file = f"url_test_{faculty.employee_code}.pdf"
            with open(pdf_file, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved to: {pdf_file}")
            print(f"  File size: {len(response.content)} bytes")
            print(f"  Content-Type: {response.get('Content-Type', 'N/A')}")
        elif response.status_code == 302:
            print(f"✗ Redirected to: {response.get('Location', 'Unknown')}")
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Response content: {response.content[:200]}")
    else:
        print("✗ Login failed")
        print("  You may need to create a superuser manually:")
        print("  Run: python manage.py createsuperuser")

if __name__ == "__main__":
    test_pdf_url(7001)