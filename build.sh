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

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --no-input

# ===== CRITICAL FIX =====
echo "========================================"
echo "🔧 ADDING PDF_URL COLUMN IF MISSING"
echo "========================================"
python manage.py force_add_pdf_url
echo "========================================"

echo "✅ Build completed successfully!"