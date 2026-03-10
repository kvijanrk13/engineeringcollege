# dashboard/management/commands/fix_pdf_url.py

from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
import sys

class Command(BaseCommand):
    help = 'Fix pdf_url column in student table for PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force add the column even if it exists',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('FIX PDF_URL COLUMN COMMAND'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Get the student model
        Student = apps.get_model('dashboard', 'Student')
        table_name = Student._meta.db_table
        
        self.stdout.write(f'Checking table: {table_name}')
        
        with connection.cursor() as cursor:
            # Check which database engine we're using
            db_engine = connection.vendor
            self.stdout.write(f'Database engine: {db_engine}')
            
            # Check if column exists based on database engine
            column_exists = False
            
            if db_engine == 'postgresql':
                # PostgreSQL check
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name=%s AND column_name=%s
                """, [table_name, 'pdf_url'])
                column_exists = cursor.fetchone() is not None
                
            elif db_engine == 'sqlite':
                # SQLite check
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_exists = any(col[1] == 'pdf_url' for col in columns)
                
            else:
                self.stdout.write(self.style.WARNING(f'Unknown database engine: {db_engine}'))
            
            # Add column if it doesn't exist or force flag is used
            if not column_exists or options['force']:
                if not column_exists:
                    self.stdout.write(self.style.WARNING('⚠️ pdf_url column NOT found!'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️ pdf_url column exists but force flag is used!'))
                
                self.stdout.write('📝 Adding pdf_url column...')
                
                try:
                    if db_engine == 'postgresql':
                        # PostgreSQL syntax
                        cursor.execute(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN pdf_url varchar(200) NULL
                        """)
                    else:
                        # SQLite syntax
                        cursor.execute(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN pdf_url varchar(200) NULL
                        """)
                    
                    self.stdout.write(self.style.SUCCESS('✅ pdf_url column added successfully!'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error adding column: {e}'))
                    
                    # Try alternative column type
                    try:
                        self.stdout.write('🔄 Trying alternative column type...')
                        if db_engine == 'postgresql':
                            cursor.execute(f"""
                                ALTER TABLE {table_name} 
                                ADD COLUMN pdf_url text NULL
                            """)
                        else:
                            cursor.execute(f"""
                                ALTER TABLE {table_name} 
                                ADD COLUMN pdf_url text NULL
                            """)
                        self.stdout.write(self.style.SUCCESS('✅ pdf_url column added as TEXT!'))
                    except Exception as e2:
                        self.stdout.write(self.style.ERROR(f'❌ Still failed: {e2}'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ pdf_url column already exists!'))
            
            # Verify the column now exists
            if db_engine == 'postgresql':
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name=%s AND column_name=%s
                """, [table_name, 'pdf_url'])
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS(f'✅ Verified: {result[0]} ({result[1]})'))
            else:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                for col in columns:
                    if col[1] == 'pdf_url':
                        self.stdout.write(self.style.SUCCESS(f'✅ Verified: {col[1]} (type: {col[2]})'))
                        break
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('COMMAND COMPLETED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
