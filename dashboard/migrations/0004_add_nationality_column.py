# Generated manually to add missing nationality column

from django.db import migrations, connection


def add_nationality_column(apps, schema_editor):
    db_backend = connection.vendor
    if db_backend == 'postgresql':
        # PostgreSQL specific
        schema_editor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name = 'dashboard_faculty'
                               AND column_name = 'nationality') THEN
                    ALTER TABLE dashboard_faculty ADD COLUMN nationality VARCHAR(100) DEFAULT 'Indian';
                END IF;
            END $$;
        """)
    elif db_backend == 'sqlite':
        # SQLite: Check if column exists
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(dashboard_faculty);")
        columns = [row[1] for row in cursor.fetchall()]
        if 'nationality' not in columns:
            schema_editor.execute("ALTER TABLE dashboard_faculty ADD COLUMN nationality VARCHAR(100) DEFAULT 'Indian';")


def remove_nationality_column(apps, schema_editor):
    db_backend = connection.vendor
    if db_backend in ['postgresql', 'sqlite']:
        schema_editor.execute("ALTER TABLE dashboard_faculty DROP COLUMN nationality;")


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_fdp_certificate_url_and_more'),
    ]

    operations = [
        migrations.RunPython(add_nationality_column, remove_nationality_column),
    ]