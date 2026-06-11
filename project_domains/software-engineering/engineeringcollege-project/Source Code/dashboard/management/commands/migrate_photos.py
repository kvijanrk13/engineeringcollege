from django.core.management.base import BaseCommand
from dashboard.models import Student
from dashboard.views import is_cloudinary_configured
import cloudinary.uploader
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Migrate existing local student photos to Cloudinary'

    def handle(self, *args, **options):
        if not is_cloudinary_configured():
            self.stdout.write(
                self.style.ERROR('Cloudinary is not configured. Please set up Cloudinary credentials.')
            )
            return

        students_with_local_photos = Student.objects.exclude(photo__isnull=True).filter(photo_url__isnull=True)

        if not students_with_local_photos.exists():
            self.stdout.write(
                self.style.SUCCESS('No students with local photos found that need migration.')
            )
            return

        self.stdout.write(f'Found {students_with_local_photos.count()} students with local photos to migrate.')

        migrated_count = 0
        failed_count = 0

        for student in students_with_local_photos:
            try:
                # Get the file path
                photo_path = student.photo.path

                if not os.path.exists(photo_path):
                    self.stdout.write(
                        self.style.WARNING(f'Photo file not found for student {student.ht_no}: {photo_path}')
                    )
                    failed_count += 1
                    continue

                # Upload to Cloudinary
                with open(photo_path, 'rb') as photo_file:
                    result = cloudinary.uploader.upload(
                        photo_file,
                        resource_type="auto",
                        folder="student_documents/photos",
                        public_id=f"student_{student.ht_no}_{student.pk}",
                        overwrite=True
                    )

                # Update student record
                student.photo_url = result.get('secure_url')
                student.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Migrated photo for student {student.ht_no}')
                )
                migrated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to migrate photo for student {student.ht_no}: {str(e)}')
                )
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Migration complete: {migrated_count} migrated, {failed_count} failed')
        )