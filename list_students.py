# list_students.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student

def list_all_students():
    students = Student.objects.all().order_by('-created_at')
    
    print(f"\n{'='*60}")
    print(f"ALL STUDENTS ({students.count()})")
    print(f"{'='*60}\n")
    
    for student in students:
        print(f"ID: {student.id}")
        print(f"HT No: {student.ht_no}")
        print(f"Name: {student.student_name}")
        
        # Count certificates
        cert_count = 0
        cert_fields = ['cert_achieve', 'cert_intern', 'cert_courses', 'cert_sdp', 
                      'cert_extra', 'cert_placement', 'cert_national']
        
        for field in cert_fields:
            if getattr(student, field):
                cert_count += 1
        
        print(f"Certificates: {cert_count}")
        print(f"Photo: {'Yes' if student.photo else 'No'}")
        print(f"Created: {student.created_at}")
        print("-" * 40)

if __name__ == "__main__":
    list_all_students()