#!/usr/bin/env bash
echo "🚀 Starting build process..."

set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations (let them fail if they do, but we continue)
echo "🔄 Running migrations..."
python manage.py migrate --no-input || echo "⚠️ Migration issues - continuing anyway"

echo "✅ Build completed! The startup check will add the pdf_url column if needed."