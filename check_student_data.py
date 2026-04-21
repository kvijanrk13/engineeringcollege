#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('F:\\IT DEPT DJANGO PROJECT\\engineeringcollege')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')

django.setup()

from dashboard.models import Student

def main():
    students = Student.objects.all()
    print(f'Total students: {students.count()}')

    if students.exists():
        student = students.first()
        print(f'First student: {student} (ID: {student.id})')
        print(f'Photo URL: {student.photo_url}')
        print(f'Photo file: {student.photo}')
        print(f'Cert achieve URL: {student.cert_achieve_url}')
        print(f'Cert achieve file: {student.cert_achieve}')
        print(f'Cert intern URL: {student.cert_intern_url}')
        print(f'Cert intern file: {student.cert_intern}')
        print(f'Cert courses URL: {student.cert_courses_url}')
        print(f'Cert courses file: {student.cert_courses}')
    else:
        print('No students found')

if __name__ == '__main__':
    main()