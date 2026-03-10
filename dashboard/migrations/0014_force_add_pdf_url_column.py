# dashboard/migrations/0014_force_add_pdf_url_column.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0013_student_pdf_url'),  # Depends on the previous migration
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Check if column exists and add it if not
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name='dashboard_student' 
                    AND column_name='pdf_url'
                ) THEN
                    ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;
                    RAISE NOTICE 'Added pdf_url column';
                ELSE
                    RAISE NOTICE 'pdf_url column already exists';
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE dashboard_student DROP COLUMN IF EXISTS pdf_url;
            """,
        ),
    ]