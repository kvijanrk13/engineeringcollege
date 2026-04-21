#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('F:\\IT DEPT DJANGO PROJECT\\engineeringcollege')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')

django.setup()

from dashboard.models import Student
from dashboard.views import collect_student_files

def main():
    students = Student.objects.all()
    if students.exists():
        student = students.first()
        print(f'Testing collect_student_files for student: {student}')

        photo_file, image_files, pdf_files, temp_files = collect_student_files(student)

        print(f'Photo file: {photo_file}')
        print(f'Image files: {image_files}')
        print(f'PDF files: {pdf_files}')
        print(f'Temp files: {temp_files}')

        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                print(f'Cleaned up: {temp_file}')

    else:
        print('No students found')

if __name__ == '__main__':
    main()