#!/usr/bin/env python
"""
Bulk Add 100 Students Script
Generates and adds 100 students with realistic data.
Auto-increments HT numbers and distributes across years/semesters.
"""
import argparse
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
from dashboard.models import Student

# ============================================================================
# SAMPLE DATA TEMPLATES
# ============================================================================

FIRST_NAMES = [
    'AAKASH', 'AARJUN', 'AARYAN', 'ABHINAV', 'ABHINAY', 'ABHISHEK', 'ABIR', 'ADITYA',
    'ADITYA', 'ADITYA', 'ADITYAKUMAR', 'AGAM', 'AGARWAL', 'AGASTYA', 'AGENDRA', 'AGHIL',
    'AGHYADEEP', 'AGHYESH', 'AGYA', 'AHAAN', 'AHIR', 'AHLAM', 'AHMAD', 'AHMED',
    'AIDEN', 'AIMAN', 'AINESH', 'AION', 'AISHA', 'AISHANI', 'AISHITA', 'AISLEEN',
    'AISHNA', 'AISHWARYA', 'AISLEEN', 'AISLING', 'AISLINN', 'AISLYNN', 'AJAY', 'AJEET',
    'AJENDRA', 'AJEESH', 'AJIN', 'AJINKYA', 'AJIT', 'AJITENDRA', 'AJITESH', 'AJITPAL',
    'AJIYA', 'AJMAN', 'AJMER', 'AJMERA', 'AJMOL', 'AJNEET', 'AJOY', 'AJUB',
    'AJYAN', 'AJYOT', 'AJYOTI', 'AKALA', 'AKALE', 'AKALI', 'AKALL', 'AKALYA',
    'AKANDE', 'AKANE', 'AKANKSHA', 'AKANKSHYA', 'AKANSHA', 'AKANSHU', 'AKANT', 'AKANU',
    'AKANYE', 'AKANZA', 'AKANZO', 'AKAR', 'AKARA', 'AKARAM', 'AKARAN', 'AKARIA'
]

LAST_NAMES = [
    'KUMAR', 'SHARMA', 'SINGH', 'PATEL', 'GUPTA', 'KHAN', 'VERMA', 'REDDY',
    'MISHRA', 'IYER', 'NAIR', 'PILLAI', 'DESAI', 'JOSHI', 'RAI', 'RAY',
    'SINHA', 'KAPOOR', 'MALHOTRA', 'BHATTACHARYA', 'CHATTERJEE', 'BOSE', 'DUTTA', 'GHOSH',
    'MUKHERJEE', 'BANERJEE', 'ROY', 'DASGUPTA', 'CHAKRABORTY', 'GANGULY', 'MAJUMDAR', 'NATH',
    'PATHAK', 'PANDEY', 'TRIPATHI', 'SHUKLA', 'DUBEY', 'SAXENA', 'AGARWAL', 'ARORA',
    'BHATNAGAR', 'BHARDWAJ', 'AWASTHI', 'RANI', 'CHOUDHARY', 'THAKUR', 'RATHOD', 'RAGHAV'
]

CITIES = [
    'Hyderabad', 'Bangalore', 'Delhi', 'Mumbai', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad',
    'Jaipur', 'Lucknow', 'Chandigarh', 'Kochi', 'Visakhapatnam', 'Indore', 'Thane', 'Bhopal'
]

def get_next_ht_numbers(count=100):
    """Generate a sequence of HT numbers starting after the highest existing student."""
    all_ht_numbers = Student.objects.values_list('ht_no', flat=True)
    max_number = 1199
    for ht in all_ht_numbers:
        if isinstance(ht, str) and ht.startswith('23C11A'):
            try:
                numeric = int(ht.replace('23C11A', ''))
                if numeric > max_number:
                    max_number = numeric
            except ValueError:
                continue
    
    return [f"23C11A{max_number + 1 + i}" for i in range(count)]


def generate_students(count=100):
    """Generate student data with auto-incrementing HT numbers."""
    students = []
    ht_numbers = get_next_ht_numbers(count=count)
    
    for i, ht_no in enumerate(ht_numbers):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Distribute across years (1-4)
        year = random.randint(1, 4)
        
        # Distribute semesters (1-8, but based on year)
        sem = (year - 1) * 2 + random.randint(1, 2)
        
        # Generate random email
        email_base = f"{first_name.lower()}{last_name.lower()}"
        email = f"{email_base}{max(0, i):03d}@college.edu"
        
        # Generate phone
        phone = f"98765{43200 + i:05d}"
        
        # Random CGPA between 6.5 and 9.5
        cgpa = round(random.uniform(6.5, 9.5), 2)
        
        # Random father/mother names
        father_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        mother_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Random gender
        gender = random.choice(['Male', 'Female'])
        
        # Random city
        city = random.choice(CITIES)
        
        student_data = {
            'ht_no': ht_no,
            'student_name': f"{first_name} {last_name}",
            'father_name': father_name,
            'mother_name': mother_name,
            'gender': gender,
            'dob': (datetime.now() - timedelta(days=random.randint(6570, 7300))).date(),
            'nationality': 'Indian',
            'category': random.choice(['General', 'OBC', 'SC', 'ST']),
            'blood_group': random.choice(['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']),
            'aadhar': f"{random.randint(100000000000, 999999999999)}",
            'email': email,
            'student_phone': phone,
            'year': year,
            'sem': sem,
            'cgpa': str(cgpa),
            'address': f"{city}, Telangana - {random.randint(500000, 509999)}",
            'task_registered': random.choice(['Yes', 'No']),
            'csi_registered': random.choice(['Yes', 'No']),
            'admission_type': random.choice(['Convener Quota', 'Management Quota', 'EAMCET']),
            'eamcet_rank': f"{random.randint(10000, 500000)}" if random.random() > 0.5 else None,
        }
        
        students.append(student_data)
    
    return students


def add_students_to_database(students_data):
    """Add students to database with progress tracking."""
    print("\n" + "=" * 80)
    print(f"ADDING {len(students_data)} STUDENTS TO DATABASE")
    print("=" * 80 + "\n")
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, student_data in enumerate(students_data, 1):
        try:
            student, created = Student.objects.get_or_create(
                ht_no=student_data['ht_no'],
                defaults=student_data
            )
            
            if created:
                created_count += 1
                if idx % 10 == 0 or idx == 1:
                    print(f"  [{idx:3d}/{len(students_data)}] ✓ Created: {student.student_name} ({student.ht_no}, ID: {student.id})")
            else:
                skipped_count += 1
                print(f"  [{idx:3d}/{len(students_data)}] ⚠ Exists: {student.student_name} ({student.ht_no}, ID: {student.id})")
        
        except Exception as e:
            error_count += 1
            print(f"  [{idx:3d}/{len(students_data)}] ✗ Error for {student_data.get('ht_no')}: {e}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Created:  {created_count} new students")
    print(f"  Skipped:  {skipped_count} existing students")
    print(f"  Errors:   {error_count} failures")
    print(f"  Total:    {created_count + skipped_count + error_count}/{len(students_data)}")
    print("=" * 80 + "\n")
    
    return created_count, skipped_count, error_count


def verify_all_students():
    """Verify all students in database."""
    print("=" * 80)
    print("FINAL VERIFICATION")
    print("=" * 80 + "\n")
    
    total_students = Student.objects.count()
    print(f"Total students in database: {total_students}\n")
    
    # Group by year
    for year in range(1, 5):
        year_count = Student.objects.filter(year=year).count()
        sem_counts = {}
        for sem in range(1, 9):
            sem_count = Student.objects.filter(year=year, sem=sem).count()
            if sem_count > 0:
                sem_counts[sem] = sem_count
        
        print(f"Year {year}: {year_count} students")
        if sem_counts:
            print(f"  Semesters: {sem_counts}\n")
    
    # Check students with certificates
    with_certs = Student.objects.exclude(
        cert_achieve__exact='',
        cert_intern__exact='',
        cert_courses__exact='',
        cert_sdp__exact='',
        cert_extra__exact='',
        cert_placement__exact='',
        cert_national__exact=''
    ).count()
    
    print(f"\nStudents with certificates: {with_certs}")
    print(f"Students ready for uploads: {total_students - with_certs}")
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bulk add student profiles.')
    parser.add_argument('--count', type=int, default=100, help='Number of students to create')
    args = parser.parse_args()
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print(f"║" + f"BULK STUDENT ADDITION - {args.count} STUDENTS".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Generate students
    print(f"\n[1/3] Generating {args.count} student profiles...")
    students_data = generate_students(args.count)
    print(f"      ✓ Generated {len(students_data)} student records")
    
    # Add to database
    print("\n[2/3] Adding students to database...")
    created, skipped, errors = add_students_to_database(students_data)
    
    # Verify
    print("[3/3] Verifying database...")
    verify_all_students()
    
    print("╔" + "=" * 78 + "╗")
    print("║" + "✓ BULK STUDENT ADDITION COMPLETE".center(78) + "║")
    print("║" + f"  {created} new students created, ready for certificate uploads!".center(76) + " ║")
    print("╚" + "=" * 78 + "╝\n")
