# dashboard/management/commands/fix_db.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add pdf_url column if missing'

    def handle(self, *args, **options):
        self.stdout.write('Checking for pdf_url column...')
        
        with connection.cursor() as cursor:
            # Check if column exists
            cursor.execute("PRAGMA table_info(dashboard_student)")
            columns = cursor.fetchall()
            exists = any(col[1] == 'pdf_url' for col in columns)
            
            if not exists:
                self.stdout.write(self.style.WARNING('Adding pdf_url column...'))
                cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column added!'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column already exists!'))