#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty, Student

print("All faculties:")
for f in Faculty.objects.all():
    print(f"  ID: {f.id}, Employee Code: {f.employee_code}, Name: {f.staff_name}")

print("\nAll students:")
for s in Student.objects.all():
    print(f"  ID: {s.id}, HT No: {s.ht_no}, Name: {s.student_name}")