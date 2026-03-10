# dashboard/management/commands/fix_pdf_url_final.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add pdf_url column to student table if missing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('CHECKING PDF_URL COLUMN'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        with connection.cursor() as cursor:
            db_type = connection.vendor
            self.stdout.write(f'Database type: {db_type}')
            
            # Check if column exists
            if db_type == 'postgresql':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' AND column_name='pdf_url'
                """)
                exists = cursor.fetchone() is not None
            else:  # sqlite
                cursor.execute("PRAGMA table_info(dashboard_student)")
                columns = cursor.fetchall()
                exists = any(col[1] == 'pdf_url' for col in columns)
            
            if not exists:
                self.stdout.write(self.style.WARNING('⚠️ pdf_url column missing! Adding it now...'))
                try:
                    cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                    self.stdout.write(self.style.SUCCESS('✅ pdf_url column added successfully!'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error adding column: {e}'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column already exists!'))
        
        self.stdout.write(self.style.SUCCESS('=' * 60))