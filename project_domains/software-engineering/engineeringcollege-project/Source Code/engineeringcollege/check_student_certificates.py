# check_student_certificates.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student


def check_student_certificates(ht_no='23C11A1201'):
    try:
        student = Student.objects.get(ht_no=ht_no)
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
                print(f"\n{field_label}: ✓ HAS FILE")
                print(f"  Type: {type(cert_field)}")

                # Get URL
                if hasattr(cert_field, 'url'):
                    url = cert_field.url
                    print(f"  URL: {url}")
                else:
                    url = str(cert_field)
                    print(f"  String value: {url[:100]}...")

                # Check if file exists in media
                if hasattr(cert_field, 'path') and os.path.exists(cert_field.path):
                    print(f"  File exists at: {cert_field.path}")
                    print(f"  File size: {os.path.getsize(cert_field.path)} bytes")
                else:
                    print(f"  File not found in local storage")
            else:
                print(f"\n{field_label}: ✗ No file")

        # Check photo
        print(f"\n{'=' * 60}")
        print(f"PHOTO:")
        if student.photo:
            print(f"✓ HAS PHOTO")
            if hasattr(student.photo, 'url'):
                print(f"  URL: {student.photo.url}")
            if hasattr(student.photo, 'path') and os.path.exists(student.photo.path):
                print(f"  File exists at: {student.photo.path}")
        else:
            print(f"✗ No photo")

    except Student.DoesNotExist:
        print(f"Student with HT No {ht_no} not found")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_student_certificates('23C11A1201')