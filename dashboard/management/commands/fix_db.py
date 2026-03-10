# dashboard/management/commands/fix_db.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix database schema issues'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Running database fixes...')
        
        with connection.cursor() as cursor:
            # Check and add pdf_url column
            db_engine = connection.vendor
            
            if db_engine == 'postgresql':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' AND column_name='pdf_url'
                """)
                exists = cursor.fetchone() is not None
            else:
                cursor.execute("PRAGMA table_info(dashboard_student)")
                columns = cursor.fetchall()
                exists = any(col[1] == 'pdf_url' for col in columns)
            
            if not exists:
                self.stdout.write(self.style.WARNING('⚠️ Adding pdf_url column...'))
                cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column added!'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column exists!'))