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

# Run database fix (this will add pdf_url if missing)
echo "🔧 Running database fix..."
python manage.py fix_db || echo "Fix command not found, continuing..."

echo "✅ Build completed successfully!"