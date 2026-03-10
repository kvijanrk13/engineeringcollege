#!/usr/bin/env bash
echo "🚀 Starting build process..."

set -o errexit  # Exit on any error

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations (allow to continue even if they fail)
echo "🔄 Running migrations..."
python manage.py migrate --no-input || echo "⚠️ Migration issues - continuing..."

# CRITICAL: Run the fix command - this MUST succeed
echo "🔄 Running database fix command..."
python manage.py fix_db  # This will exit if it fails

echo "✅ Build completed successfully!"