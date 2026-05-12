#!/usr/bin/env python
"""
Student Profile Creation Script
Manages bulk student creation with certificate fields properly initialized.
"""
import os
import sys
import django
import io
from datetime import datetime, timedelta
import random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from django.utils import timezone
from dashboard.models import Student, CloudinaryUpload

# ============================================================================
# SAMPLE STUDENT DATA - Easily extensible
# ============================================================================

SAMPLE_STUDENTS = [
    {
        'ht_no': '23C11A1215',
        'student_name': 'STUDENT FIFTEEN',
        'father_name': 'Father Name',
        'mother_name': 'Mother Name',
        'gender': 'Male',
        'dob': '2004-05-15',
        'nationality': 'Indian',
        'category': 'General',
        'blood_group': 'O+',
        'email': 'student15@college.edu',
        'student_phone': '9876543210',
        'year': 4,
        'sem': 7,
        'cgpa': '8.5',
        'address': 'Address Line 1, City, State - 500001',
    },
    {
        'ht_no': '23C11A1216',
        'student_name': 'STUDENT SIXTEEN',
        'father_name': 'Father Name',
        'mother_name': 'Mother Name',
        'gender': 'Female',
        'dob': '2004-06-20',
        'nationality': 'Indian',
        'category': 'General',
        'blood_group': 'A+',
        'email': 'student16@college.edu',
        'student_phone': '9876543211',
        'year': 4,
        'sem': 7,
        'cgpa': '8.2',
        'address': 'Address Line 2, City, State - 500001',
    },
    {
        'ht_no': '23C11A1217',
        'student_name': 'STUDENT SEVENTEEN',
        'father_name': 'Father Name',
        'mother_name': 'Mother Name',
        'gender': 'Male',
        'dob': '2004-07-10',
        'nationality': 'Indian',
        'category': 'OBC',
        'blood_group': 'B+',
        'email': 'student17@college.edu',
        'student_phone': '9876543212',
        'year': 4,
        'sem': 7,
        'cgpa': '7.9',
        'address': 'Address Line 3, City, State - 500001',
    },
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_or_update_student(student_data):
    """Create or update a student with the given data."""
    ht_no = student_data['ht_no']
    
    # Get or create student
    student, created = Student.objects.get_or_create(
        ht_no=ht_no,
        defaults=student_data
    )
    
    if created:
        print(f"✓ Created new student: {student.student_name} (HT No: {ht_no}, ID: {student.id})")
    else:
        # Update existing student with new data
        for key, value in student_data.items():
            if key != 'ht_no':
                setattr(student, key, value)
        student.save()
        print(f"⚠ Updated existing student: {student.student_name} (HT No: {ht_no}, ID: {student.id})")
    
    return student, created


def bulk_create_students(students_data):
    """Bulk create students with proper initialization."""
    print("\n" + "=" * 70)
    print("BULK STUDENT CREATION")
    print("=" * 70 + "\n")
    
    created_count = 0
    updated_count = 0
    
    for student_data in students_data:
        try:
            student, created = create_or_update_student(student_data)
            if created:
                created_count += 1
            else:
                updated_count += 1
                
            # Verify student has all certificate field slots initialized
            cert_fields = [
                'cert_achieve', 'cert_intern', 'cert_courses',
                'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national'
            ]
            cert_urls = [
                'cert_achieve_url', 'cert_intern_url', 'cert_courses_url',
                'cert_sdp_url', 'cert_extra_url', 'cert_placement_url', 'cert_national_url'
            ]
            
            # Ensure all cert fields exist (they should by default, but double-check)
            for field in cert_fields + cert_urls:
                if not hasattr(student, field):
                    print(f"  ⚠ Warning: Student missing field {field}")
            
        except Exception as e:
            print(f"✗ Error creating student {student_data.get('ht_no')}: {e}")
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: Created {created_count} new students, Updated {updated_count} existing")
    print("=" * 70 + "\n")
    
    return created_count, updated_count


def list_all_students():
    """Display all students in the database."""
    print("\n" + "=" * 70)
    print("ALL STUDENTS IN DATABASE")
    print("=" * 70 + "\n")
    
    students = Student.objects.all().order_by('id')
    
    if not students.exists():
        print("No students found in database.\n")
        return
    
    print(f"Total: {students.count()} students\n")
    
    for student in students:
        print(f"  ID: {student.id:3d} | HT No: {student.ht_no:15s} | Name: {student.student_name}")
        print(f"           Email: {student.email or 'N/A'}")
        print(f"           Year: {student.year}, Sem: {student.sem}, CGPA: {student.cgpa or 'N/A'}")
        print(f"           Created: {student.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def verify_student_structure(student_id=None):
    """Verify student data structure and certificate initialization."""
    print("\n" + "=" * 70)
    print("STUDENT STRUCTURE VERIFICATION")
    print("=" * 70 + "\n")
    
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            students = [student]
        except Student.DoesNotExist:
            print(f"✗ Student with ID {student_id} not found!\n")
            return
    else:
        students = Student.objects.all()
    
    if not students:
        print("No students to verify.\n")
        return
    
    for student in students:
        print(f"Student: {student.student_name} (ID: {student.id}, HT No: {student.ht_no})")
        
        # Check certificate fields
        cert_fields = [
            ('cert_achieve', 'cert_achieve_url'),
            ('cert_intern', 'cert_intern_url'),
            ('cert_courses', 'cert_courses_url'),
            ('cert_sdp', 'cert_sdp_url'),
            ('cert_extra', 'cert_extra_url'),
            ('cert_placement', 'cert_placement_url'),
            ('cert_national', 'cert_national_url'),
        ]
        
        for file_field, url_field in cert_fields:
            file_val = getattr(student, file_field, None)
            url_val = getattr(student, url_field, None)
            status = "✓" if file_val or url_val else "○"
            print(f"  {status} {file_field:20s}: file={bool(file_val):5} | url={bool(url_val):5}")
        
        print(f"  Photo: {bool(student.photo):5} | Photo URL: {bool(student.photo_url):5}")
        print(f"  PDF Generated: {student.pdf_generated} | PDF File: {bool(student.pdf_file):5}")
        print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("STUDENT PROFILE MANAGEMENT SYSTEM")
    print("=" * 70 + "\n")
    
    # Create/update sample students
    created, updated = bulk_create_students(SAMPLE_STUDENTS)
    
    # List all students
    list_all_students()
    
    # Verify structure
    verify_student_structure()
    
    print("=" * 70)
    print("✓ Student profile management complete!")
    print("=" * 70 + "\n")
