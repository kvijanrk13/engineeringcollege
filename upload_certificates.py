# upload_certificates.py
import os
import django
import cloudinary
import cloudinary.uploader
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student

def upload_certificate_for_student(ht_no, cert_type, file_path):
    """
    Manually upload a certificate for a student
    
    cert_type options: 
    - 'achieve' for Achievement Certificates
    - 'intern' for Internship Certificates
    - 'courses' for Course Certificates
    - 'sdp' for SDP Certificates
    - 'extra' for Extracurricular Certificates
    - 'placement' for Placement Certificates
    - 'national' for National Exam Certificates
    """
    try:
        student = Student.objects.get(ht_no=ht_no)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        field_mapping = {
            'achieve': 'cert_achieve',
            'intern': 'cert_intern',
            'courses': 'cert_courses',
            'sdp': 'cert_sdp',
            'extra': 'cert_extra',
            'placement': 'cert_placement',
            'national': 'cert_national'
        }
        
        if cert_type not in field_mapping:
            print(f"Invalid certificate type. Choose from: {', '.join(field_mapping.keys())}")
            return
        
        field_name = field_mapping[cert_type]
        
        print(f"\nUploading {cert_type} certificate for {student.student_name}...")
        print(f"File: {file_path}")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="auto",
            folder=f"student_documents/{cert_type}",
            public_id=f"{cert_type}_{student.ht_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            overwrite=True
        )
        
        print(f"✓ Uploaded to Cloudinary: {result['secure_url']}")
        
        # Update student record
        setattr(student, field_name, result['secure_url'])
        student.save()
        
        print(f"✓ Student record updated")
        print(f"✓ Certificate added successfully!")
        
    except Student.DoesNotExist:
        print(f"Student with HT No {ht_no} not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("CERTIFICATE UPLOAD SCRIPT")
    print("="*60)
    
    ht_no = input("Enter student HT No (e.g., 23C11A1201): ").strip()
    
    print("\nCertificate types:")
    print("  achieve - Achievement Certificates")
    print("  intern - Internship Certificates")
    print("  courses - Course Certificates")
    print("  sdp - SDP Certificates")
    print("  extra - Extracurricular Certificates")
    print("  placement - Placement Certificates")
    print("  national - National Exam Certificates")
    
    cert_type = input("\nEnter certificate type: ").strip()
    file_path = input("Enter full path to certificate file: ").strip()
    
    upload_certificate_for_student(ht_no, cert_type, file_path)