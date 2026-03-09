#!/usr/bin/env bash
# build.sh - Render build script

echo "🚀 Starting build process..."

# Exit on error
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

# Apply database migrations
echo "🗄️ Applying database migrations..."
python manage.py migrate

# Create superuser if needed (optional - uncomment if you want auto-create)
# echo "👤 Creating superuser..."
# python manage.py createsuperuser --no-input --username admin --email admin@example.com || true

echo "✅ Build completed successfully!"