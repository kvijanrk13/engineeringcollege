#!/usr/bin/env bash

echo "🚀 Starting build process..."
echo "========================================"

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

# Install system dependencies for WeasyPrint (on Linux/Render)
if [[ "$ON_RENDER" == "True" ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Installing system dependencies for WeasyPrint..."
    apt-get update && apt-get install -y \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        libxml2 \
        libxslt1.1 \
        shared-mime-info \
        libpangoft2-1.0-0 \
        fonts-dejavu-core \
        && echo "✅ System dependencies installed"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles media

# Run migrations with retry logic (critical for PostgreSQL)
echo "🔄 Applying database migrations..."
max_retries=5
retry_count=0
until python manage.py migrate --noinput 2>/dev/null || [ $retry_count -eq $max_retries ]; do
    retry_count=$((retry_count + 1))
    echo "⚠️ Migration attempt $retry_count failed, retrying in 5 seconds..."
    sleep 5
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Database migration failed after $max_retries attempts"
    echo "This may be due to database connection issues. Check DATABASE_URL."
    exit 1
fi

# Create or update the initial Django superuser when env vars are provided.
python manage.py createsuperuser --noinput \
  --username $DJANGO_SUPERUSER_USERNAME \
  --email $DJANGO_SUPERUSER_EMAIL || true
echo "Superuser created or already exists."

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"
