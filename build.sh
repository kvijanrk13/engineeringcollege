#!/usr/bin/env bash

echo "🚀 Starting build process..."
echo "========================================"

set -o errexit

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input

# Show migrations (debug)
echo "📋 Current migrations:"
python manage.py showmigrations

# Apply migrations
echo "🔄 Applying migrations..."
python manage.py migrate --no-input

# Ensure pdf_url column exists (safe check for PostgreSQL + SQLite)
echo "========================================"
echo "🔧 ENSURING PDF_URL COLUMN EXISTS"
echo "========================================"

python manage.py shell << EOF
from django.db import connection

with connection.cursor() as cursor:
    try:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='dashboard_student' AND column_name='pdf_url'
        """)
        exists = cursor.fetchone()
    except:
        # fallback for sqlite
        cursor.execute("PRAGMA table_info(dashboard_student)")
        exists = any(col[1] == 'pdf_url' for col in cursor.fetchall())

    if not exists:
        print("⚠️ pdf_url column missing! Adding now...")
        try:
            cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
            print("✅ pdf_url column added!")
        except Exception as e:
            print(f"⚠️ Could not add column: {e}")
    else:
        print("✅ pdf_url column already exists!")
EOF

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"