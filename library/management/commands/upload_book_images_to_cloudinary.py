import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from library.models import Book


class Command(BaseCommand):
    help = 'Upload local book images to Cloudinary and update URLs'

    def handle(self, *args, **options):
        if not getattr(settings, 'CLOUDINARY_CONFIGURED', False):
            self.stdout.write(self.style.ERROR('Cloudinary is not configured'))
            return

        fs = FileSystemStorage()
        uploaded = 0
        skipped = 0
        failed = 0

        for book in Book.objects.all():
            if not book.image:
                skipped += 1
                continue

            local_path = fs.path(book.image.name)
            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f'File not found: {local_path}'))
                skipped += 1
                continue

            try:
                with open(local_path, 'rb') as f:
                    book.image.save(os.path.basename(local_path), f, save=True)
                uploaded += 1
                self.stdout.write(self.style.SUCCESS(f'Uploaded: {book.name}'))
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f'Failed: {book.name} - {e}'))

        self.stdout.write(self.style.SUCCESS(f'Uploaded: {uploaded}, Skipped: {skipped}, Failed: {failed}'))
