# dashboard/management/commands/check_columns.py
from django.core.management.base import BaseCommand
from dashboard.startup import check_pdf_url_column


class Command(BaseCommand):
    help = 'Check and fix database column issues'

    def handle(self, *args, **options):
        self.stdout.write("Running column check...")
        result = check_pdf_url_column()
        if result:
            self.stdout.write(
                self.style.SUCCESS('Column check completed successfully')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Column check failed')
            )
