import os
import django
import cloudinary
import cloudinary.uploader
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student

def sync_all_students_to_cloudinary():
    """
    Scans all student records and uploads their local photo/certificates to Cloudinary,
    then updates the corresponding _url fields.
    """
    students = Student.objects.all()
    total_updated = 0
    
    fields = [
        ('photo', 'photo_url', 'student_photos'),
        ('cert_achieve', 'cert_achieve_url', 'student_certificates'),
        ('cert_intern', 'cert_intern_url', 'student_certificates'),
        ('cert_courses', 'cert_courses_url', 'student_certificates'),
        ('cert_sdp', 'cert_sdp_url', 'student_certificates'),
        ('cert_extra', 'cert_extra_url', 'student_certificates'),
        ('cert_placement', 'cert_placement_url', 'student_certificates'),
        ('cert_national', 'cert_national_url', 'student_certificates'),
    ]
    
    print(f"Checking {students.count()} students for unsynced local files...")
    
    for student in students:
        student_updated = False
        print(f"\nChecking student {student.ht_no} ({student.student_name})...")
        
        for file_field_name, url_field_name, folder in fields:
            file_field = getattr(student, file_field_name)
            url_field = getattr(student, url_field_name)
            
            # If the student has a local file but no Cloudinary URL
            if file_field and not url_field:
                if hasattr(file_field, 'path') and os.path.exists(file_field.path):
                    print(f"  Uploading {file_field_name} to Cloudinary...")
                    try:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        result = cloudinary.uploader.upload(
                            file_field.path,
                            resource_type="auto",
                            folder=folder,
                            public_id=f"student_{student.ht_no}_{file_field_name}_{timestamp}",
                            overwrite=True
                        )
                        setattr(student, url_field_name, result['secure_url'])
                        student_updated = True
                        print(f"  ✓ Success: {result['secure_url']}")
                    except Exception as e:
                        print(f"  ✗ Error uploading {file_field_name}: {e}")
                else:
                    print(f"  ! Local file {file_field_name} referenced in DB but not found on disk.")
        
        if student_updated:
            student.save()
            total_updated += 1
            print(f"✓ Saved updated Cloudinary URLs for student {student.ht_no}")
            
    print(f"\n{'='*60}")
    print(f"SYNC COMPLETE. Updated {total_updated} students.")
    print(f"{'='*60}")

if __name__ == "__main__":
    sync_all_students_to_cloudinary()