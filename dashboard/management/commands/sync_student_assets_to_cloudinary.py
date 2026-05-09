# management/commands/sync_student_assets_to_cloudinary.py
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary.uploader
import cloudinary
import os
from dashboard.models import Student
import sys

class Command(BaseCommand):
    help = 'Sync student photos and certificates from local storage to Cloudinary, updating database URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )
        parser.add_argument(
            '--student-id',
            type=int,
            help='Only sync specific student ID',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip students that already have Cloudinary URLs',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_id = options['student_id']
        skip_existing = options['skip_existing']

        if not getattr(settings, 'CLOUDINARY_CONFIGURED', False):
            self.stdout.write(self.style.ERROR('Cloudinary is not configured. Exiting.'))
            sys.exit(1)

        # Initialize Cloudinary
        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', None)
        api_key = getattr(settings, 'CLOUDINARY_API_KEY', None)
        api_secret = getattr(settings, 'CLOUDINARY_API_SECRET', None)

        if not all([cloud_name, api_key, api_secret]):
            self.stdout.write(self.style.ERROR('Cloudinary credentials incomplete. Exiting.'))
            sys.exit(1)

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )

        students = Student.objects.all()
        if specific_id:
            students = students.filter(id=specific_id)

        total = students.count()
        self.stdout.write(f'Processing {total} students...')

        updated_count = 0
        for student in students:
            self.stdout.write(f'\n--- Student: {student.student_name} (ID: {student.id}, HT: {student.ht_no}) ---')

            needs_save = False

            # Check photo
            if student.photo and not skip_existing:
                photo_path = student.photo.path
                if os.path.exists(photo_path):
                    public_id = f'{student.ht_no}_photo'
                    self.stdout.write(f'  Uploading photo: {photo_path} -> student_photos/{public_id}')
                    if not dry_run:
                        try:
                            result = cloudinary.uploader.upload(
                                photo_path,
                                folder='student_photos',
                                public_id=public_id,
                                overwrite=True,
                                resource_type='image'
                            )
                            student.photo_url = result.get('secure_url')
                            needs_save = True
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Photo uploaded: {result.get("secure_url")}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  ✗ Photo upload failed: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Photo file not found: {photo_path}'))
            elif skip_existing and student.photo_url:
                self.stdout.write(f'  ✓ Skipping photo (already has Cloudinary URL)')
            elif not student.photo:
                self.stdout.write(f'  - No photo field')

            # Check certificates
            cert_fields = [
                ('cert_achieve', 'achievement'),
                ('cert_intern', 'internship'),
                ('cert_courses', 'courses'),
                ('cert_sdp', 'sdp'),
                ('cert_extra', 'extra'),
                ('cert_placement', 'placement'),
                ('cert_national', 'national'),
            ]

            for field_name, cert_type in cert_fields:
                file_field = getattr(student, field_name)
                url_field_name = f'{field_name}_url'
                if file_field and not skip_existing:
                    file_path = file_field.path
                    if os.path.exists(file_path):
                        public_id = f'{student.ht_no}_{cert_type}'
                        self.stdout.write(f'  Uploading {cert_type} cert: {file_path} -> student_certs/{cert_type}/{public_id}')
                        if not dry_run:
                            try:
                                result = cloudinary.uploader.upload(
                                    file_path,
                                    folder=f'student_certs/{cert_type}',
                                    public_id=public_id,
                                    overwrite=True,
                                    resource_type='raw'
                                )
                                setattr(student, url_field_name, result.get('secure_url'))
                                needs_save = True
                                self.stdout.write(self.style.SUCCESS(f'  ✓ {cert_type} cert uploaded: {result.get("secure_url")}'))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'  ✗ {cert_type} cert upload failed: {e}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  ⚠ {cert_type} cert file not found: {file_path}'))
                elif skip_existing and getattr(student, url_field_name):
                    self.stdout.write(f'  ✓ Skipping {cert_type} cert (already has Cloudinary URL)')
                elif not file_field:
                    self.stdout.write(f'  - No {cert_type} cert field')

            # Save after all fields updated
            if needs_save:
                student.save()
                updated_count += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nDry run complete. Would have updated assets for {total} students.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSync complete. Updated {updated_count} students with Cloudinary URLs.'))
