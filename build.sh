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

# Show current migrations
echo "📋 Current migrations:"
python manage.py showmigrations

# Apply all migrations including 0013
echo "🔄 Applying all migrations..."
python manage.py migrate --no-input

# If migration 0013 still didn't run, add column directly
echo "========================================"
echo "🔧 ENSURING PDF_URL COLUMN EXISTS"
echo "========================================"

python manage.py shell << EOF
from django.db import connection
with connection.cursor() as cursor:
    # Check if column exists
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='dashboard_student' AND column_name='pdf_url'
    """)
    if not cursor.fetchone():
        print("⚠️ pdf_url column missing! Adding now...")
        cursor.execute("ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;")
        print("✅ pdf_url column added!")
    else:
        print("✅ pdf_url column already exists!")
EOF

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"