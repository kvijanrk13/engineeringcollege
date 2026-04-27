#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student
from dashboard.views import generate_student_pdf
import traceback

def test_full_student_pdf(student_id=21):
    try:
        student = Student.objects.get(id=student_id)
        print(f"Testing full student PDF generation for: {student.student_name} ({student.ht_no})")
        
        # Call the actual function that generates PDF bytes
        pdf_bytes = generate_student_pdf(student, return_bytes=True)
        
        if pdf_bytes and len(pdf_bytes) > 100:
            output_file = f"full_test_student_{student.ht_no}.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            print(f"SUCCESS: Full PDF generated: {output_file} ({len(pdf_bytes)} bytes)")
            return True
        else:
            print(f"FAILED: No PDF bytes returned (got {pdf_bytes})")
            return False
            
    except Exception as e:
        print(f"FAILED with exception: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_student_pdf(21)
    input("\nPress Enter to exit...")