# dashboard/management/commands/fix_db.py
from django.core.management.base import BaseCommand
from django.db import connection
import sys

class Command(BaseCommand):
    help = 'Force add pdf_url column to student table'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('FORCE ADD PDF_URL COLUMN'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        with connection.cursor() as cursor:
            # Get database info
            db_engine = connection.vendor
            self.stdout.write(f'Database engine: {db_engine}')
            self.stdout.write(f'Database name: {connection.settings_dict["NAME"]}')
            
            # Try multiple methods to add the column
            success = False
            
            # Method 1: Check if column exists
            if db_engine == 'postgresql':
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
                self.stdout.write(f'Existing columns: {[col[1] for col in columns]}')
            
            if not exists:
                self.stdout.write(self.style.WARNING('⚠️ pdf_url column MISSING! Adding now...'))
                
                # Method 2: Add the column
                try:
                    if db_engine == 'postgresql':
                        cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                    else:
                        cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
                    self.stdout.write(self.style.SUCCESS('✅ Column added successfully!'))
                    success = True
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error adding column: {e}'))
                    
                    # Method 3: Try with different data type
                    try:
                        self.stdout.write('🔄 Trying with TEXT data type...')
                        if db_engine == 'postgresql':
                            cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url text NULL;")
                        else:
                            cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url text NULL;")
                        self.stdout.write(self.style.SUCCESS('✅ Column added as TEXT!'))
                        success = True
                    except Exception as e2:
                        self.stdout.write(self.style.ERROR(f'❌ Still failed: {e2}'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column already exists!'))
                success = True
            
            # Method 4: Verify the column now exists
            if db_engine == 'postgresql':
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' AND column_name='pdf_url'
                """)
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS(f'✅ Verified: {result[0]} ({result[1]})'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Column still missing after all attempts!'))
            else:
                cursor.execute("PRAGMA table_info(dashboard_student)")
                columns = cursor.fetchall()
                for col in columns:
                    if col[1] == 'pdf_url':
                        self.stdout.write(self.style.SUCCESS(f'✅ Verified: {col[1]} (type: {col[2]})'))
                        break
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if success:
            self.stdout.write(self.style.SUCCESS('✅ FIX COMPLETED SUCCESSFULLY'))
        else:
            self.stdout.write(self.style.ERROR('❌ FIX FAILED - Manual intervention needed'))
            sys.exit(1)  # Fail the build so we know it didn't work
        
        self.stdout.write(self.style.SUCCESS('=' * 60))