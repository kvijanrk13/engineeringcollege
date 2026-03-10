#!/usr/bin/env bash
echo "🚀 Starting build process..."

set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --no-input

# DIRECT FIX: Add the column using PostgreSQL
echo "🔄 Attempting direct SQL fix for pdf_url column..."
python manage.py dbshell << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='dashboard_student'
        AND column_name='pdf_url'
    ) THEN
        ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;
        RAISE NOTICE 'Added pdf_url column via direct SQL';
    ELSE
        RAISE NOTICE 'pdf_url column already exists';
    END IF;
END \$\$;
EOF

echo "✅ Build completed successfully!"