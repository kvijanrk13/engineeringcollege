# Generated manually to add missing nationality column

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_fdp_certificate_url_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name = 'dashboard_faculty'
                               AND column_name = 'nationality') THEN
                    ALTER TABLE dashboard_faculty ADD COLUMN nationality VARCHAR(100) DEFAULT 'Indian';
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE dashboard_faculty DROP COLUMN nationality;
            """
        ),
    ]