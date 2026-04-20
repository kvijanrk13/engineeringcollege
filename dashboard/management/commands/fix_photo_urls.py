from django.core.management.base import BaseCommand
from dashboard.models import Student
import os
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Fix broken photo URLs by switching to local files where available'

    def handle(self, *args, **options):
        students = Student.objects.exclude(photo_url__isnull=True).exclude(photo_url='')

        self.stdout.write(f'Checking {students.count()} students with photo URLs...')

        fixed_count = 0

        for student in students:
            try:
                # Test if the Cloudinary URL works
                response = requests.head(student.photo_url, timeout=10)
                if response.status_code == 200:
                    self.stdout.write(f'✓ {student.student_name}: URL is valid')
                    continue

                # URL is broken, check if we have a local file
                if student.photo and os.path.exists(student.photo.path):
                    self.stdout.write(f'↻ {student.student_name}: Switching to local file')
                    student.photo_url = None  # Clear broken URL
                    student.save()
                    fixed_count += 1
                else:
                    self.stdout.write(f'✗ {student.student_name}: No local file available')

            except Exception as e:
                self.stdout.write(f'✗ {student.student_name}: Error checking URL - {e}')

        self.stdout.write(f'Fixed {fixed_count} students with broken photo URLs')