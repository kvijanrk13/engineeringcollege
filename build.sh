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

# Force apply all migrations including 0013
echo "🔄 Applying all migrations..."
python manage.py migrate --no-input

# Run the fix command as backup
echo "🔧 Running database fix command..."
python manage.py fix_db || echo "Fix command not found, continuing..."

echo "========================================"
echo "✅ Build completed successfully!"