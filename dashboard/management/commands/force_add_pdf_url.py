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
            
            success = False
            
            # Try multiple methods to add the column
            if db_engine == 'postgresql':
                # Method 1: Check and add with DO block
                try:
                    cursor.execute("""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_name='dashboard_student' AND column_name='pdf_url'
                            ) THEN
                                ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;
                                RAISE NOTICE 'Column added';
                            END IF;
                        END $$;
                    """)
                    self.stdout.write(self.style.SUCCESS('✅ Column check/added via DO block'))
                    success = True
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Method 1 failed: {e}'))
                    
                    # Method 2: Direct ALTER (ignoring if exists)
                    try:
                        cursor.execute("ALTER TABLE dashboard_student ADD COLUMN IF NOT EXISTS pdf_url varchar(200) NULL;")
                        self.stdout.write(self.style.SUCCESS('✅ Column added via IF NOT EXISTS'))
                        success = True
                    except Exception as e2:
                        self.stdout.write(self.style.ERROR(f'❌ Method 2 failed: {e2}'))
            else:
                # SQLite method
                try:
                    cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                    self.stdout.write(self.style.SUCCESS('✅ Column added to SQLite'))
                    success = True
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ SQLite error: {e}'))
            
            # Verify column exists
            if db_engine == 'postgresql':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' AND column_name='pdf_url'
                """)
                if cursor.fetchone():
                    self.stdout.write(self.style.SUCCESS('✅ VERIFIED: pdf_url column exists'))
                else:
                    self.stdout.write(self.style.ERROR('❌ VERIFICATION FAILED: Column still missing'))
            else:
                cursor.execute("PRAGMA table_info(dashboard_student)")
                columns = cursor.fetchall()
                if any(col[1] == 'pdf_url' for col in columns):
                    self.stdout.write(self.style.SUCCESS('✅ VERIFIED: pdf_url column exists'))
                else:
                    self.stdout.write(self.style.ERROR('❌ VERIFICATION FAILED: Column still missing'))
        
        self.stdout.write(self.style.SUCCESS('=' * 60))