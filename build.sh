#!/usr/bin/env bash
# build.sh - Render build script

echo "🚀 Starting build process..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Exit on error
set -o errexit

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create static directory if it doesn't exist
mkdir -p static

# Collect static files - THIS IS CRITICAL
echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input --verbosity 2

# Apply database migrations
echo "🗄️ Applying database migrations..."
python manage.py migrate --no-input

# Create superuser if needed (optional - uncomment if you want auto-create)
# echo "👤 Creating superuser..."
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')" | python manage.py shell || true

echo "✅ Build completed successfully!"
ls -la staticfiles/  # Show collected static files