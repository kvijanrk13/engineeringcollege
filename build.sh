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

# Run the fix command (this will add the column if missing)
echo "🔄 Running pdf_url fix..."
python manage.py fix_pdf_url

echo "✅ Build completed successfully!"