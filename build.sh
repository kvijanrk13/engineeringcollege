#!/usr/bin/env bash

echo "🚀 Starting build process..."
echo "========================================"

set -o errexit

# Show the exact source revision being built on Render.
echo "🔎 Git commit:"
git rev-parse HEAD || true
git rev-parse --short HEAD || true

# Ensure Django settings loaded
export DJANGO_SETTINGS_MODULE=engineeringcollege.settings
export PYTHONUNBUFFERED=1

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles media

# Run migrations first (critical for PostgreSQL)
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

# Show migration status (debugging)
echo "📋 Migration status:"
python manage.py showmigrations

# Verify which view the deployed root URL resolves to.
echo "🧭 URL resolution check:"
python manage.py shell -c "from django.urls import resolve; m = resolve('/'); print(f'/ -> {m.func.__module__}.{m.func.__name__}')" || true

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"
