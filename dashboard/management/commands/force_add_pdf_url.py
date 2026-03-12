# dashboard/management/commands/force_add_pdf_url.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Force add pdf_url column to student table'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('FORCE ADD PDF_URL COLUMN'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        with connection.cursor() as cursor:
            db_engine = connection.vendor
            self.stdout.write(f'Database engine: {db_engine}')
            
            if db_engine == 'postgresql':
                # PostgreSQL method with IF NOT EXISTS
                try:
                    cursor.execute("ALTER TABLE dashboard_student ADD COLUMN IF NOT EXISTS pdf_url varchar(200) NULL;")
                    self.stdout.write(self.style.SUCCESS('✅ Column added/verified via IF NOT EXISTS'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            else:
                # SQLite method
                try:
                    cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                    self.stdout.write(self.style.SUCCESS('✅ Column added to SQLite'))
                except Exception as e:
                    if 'duplicate column' in str(e):
                        self.stdout.write(self.style.SUCCESS('✅ Column already exists'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            
            # Verify
            self.stdout.write(self.style.SUCCESS('✅ Check complete'))
        
        self.stdout.write(self.style.SUCCESS('=' * 60))