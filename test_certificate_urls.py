# test_certificate_urls.py
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student

def test_certificate_urls(ht_no='23C11A1201'):
    try:
        student = Student.objects.get(ht_no=ht_no)
        
        print(f"\n{'='*60}")
        print(f"TESTING CERTIFICATE URLS FOR: {student.student_name}")
        print(f"{'='*60}\n")
        
        certificate_fields = [
            ('cert_achieve', 'Achievement Certificates'),
            ('cert_intern', 'Internship Certificates'),
            ('cert_courses', 'Course Certificates'),
            ('cert_sdp', 'SDP Certificates'),
            ('cert_extra', 'Extracurricular Certificates'),
            ('cert_placement', 'Placement Certificates'),
            ('cert_national', 'National Exam Certificates'),
        ]
        
        for field_name, field_label in certificate_fields:
            cert_field = getattr(student, field_name, None)
            
            if cert_field:
                url = cert_field if isinstance(cert_field, str) else cert_field.url
                print(f"\n{field_label}:")
                print(f"  URL: {url}")
                
                # Test URL
                try:
                    response = requests.head(url, timeout=10, allow_redirects=True)
                    print(f"  Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        # Try to get content type
                        content_type = response.headers.get('Content-Type', 'Unknown')
                        print(f"  Content-Type: {content_type}")
                        
                        # Check if it's a PDF or image
                        if 'pdf' in content_type.lower():
                            print(f"  ✓ Is a PDF file")
                        elif 'image' in content_type.lower():
                            print(f"  ✓ Is an image file")
                        else:
                            print(f"  ⚠ Unknown file type")
                            
                        # Check file size
                        content_length = response.headers.get('Content-Length')
                        if content_length:
                            print(f"  Size: {int(content_length)/1024:.1f} KB")
                            
                    else:
                        print(f"  ✗ URL not accessible")
                        
                except Exception as e:
                    print(f"  ✗ Error testing URL: {e}")
            else:
                print(f"\n{field_label}: No file")
                
    except Student.DoesNotExist:
        print(f"Student with HT No {ht_no} not found")

if __name__ == "__main__":
    test_certificate_urls('23C11A1201')