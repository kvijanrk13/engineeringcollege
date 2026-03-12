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

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --no-input

# ===== CRITICAL FIX =====
echo "========================================"
echo "🔧 FORCE ADDING PDF_URL COLUMN"
echo "========================================"

# Try multiple approaches
python manage.py fix_pdf_url || echo "Fix command not found, trying direct SQL..."

# If fix_pdf_url doesn't exist, use direct SQL
python manage.py dbshell << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='dashboard_student' AND column_name='pdf_url'
    ) THEN
        ALTER TABLE dashboard_student ADD COLUMN pdf_url varchar(200) NULL;
        RAISE NOTICE '✅ pdf_url column added via direct SQL';
    ELSE
        RAISE NOTICE '✅ pdf_url column already exists';
    END IF;
END \$\$;
EOF

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"