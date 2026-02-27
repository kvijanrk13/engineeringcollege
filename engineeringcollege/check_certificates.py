# check_certificates.py
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student


def check_student_certificates(student_id):
    try:
        student = Student.objects.get(id=student_id)
        print(f"\n{'=' * 60}")
        print(f"Checking certificates for: {student.student_name} (HT: {student.ht_no})")
        print(f"{'=' * 60}\n")

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
                print(f"\n{field_label}:")
                print(f"  Type: {type(cert_field)}")

                # Get URL
                if hasattr(cert_field, 'url'):
                    url = cert_field.url
                    print(f"  URL: {url}")
                else:
                    url = str(cert_field)
                    print(f"  String value: {url[:100]}...")

                # Test if URL is accessible
                try:
                    response = requests.head(url, timeout=5)
                    print(f"  Status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"  Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                        print(f"  ✓ Accessible")
                    else:
                        print(f"  ✗ Not accessible")
                except Exception as e:
                    print(f"  ✗ Error accessing: {e}")
            else:
                print(f"\n{field_label}: No file uploaded")

    except Student.DoesNotExist:
        print(f"Student with ID {student_id} not found")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Check for student with ID 1 (adjust as needed)
    # You can also search by HT No
    try:
        student = Student.objects.get(ht_no='23C11A1201')
        check_student_certificates(student.id)
    except Student.DoesNotExist:
        print("Student with HT No '23C11A1201' not found")
        # List all students
        print("\nAvailable students:")
        for s in Student.objects.all()[:5]:
            print(f"  ID: {s.id}, HT: {s.ht_no}, Name: {s.student_name}")