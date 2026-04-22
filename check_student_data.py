import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student

students = Student.objects.all()
print(f"Total students: {len(students)}")

for s in students:
    print(f"\nStudent: {s.student_name} ({s.ht_no})")
    print(f"  Photo: {s.photo}")
    print(f"  Photo URL: {s.photo_url}")
    print(f"  Cert Achieve: {s.cert_achieve}")
    print(f"  Cert Achieve URL: {s.cert_achieve_url}")
    print(f"  Cert Intern: {s.cert_intern}")
    print(f"  Cert Intern URL: {s.cert_intern_url}")
    print(f"  PDF File: {s.pdf_file}")
    print(f"  PDF URL: {s.pdf_url}")
