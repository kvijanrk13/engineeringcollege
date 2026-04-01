#!/usr/bin/env bash

echo "🚀 Starting build process..."
echo "========================================"

set -o errexit

# Ensure Django settings loaded
export DJANGO_SETTINGS_MODULE=engineeringcollege.settings

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files (SAFE)
echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input || echo "⚠️ Skipping collectstatic"

# Show migrations
echo "📋 Current migrations:"
python manage.py showmigrations

# Apply migrations
echo "🔄 Applying migrations..."
python manage.py migrate --no-input

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"