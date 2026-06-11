#!/usr/bin/env bash
set -e

echo "Starting build process..."
echo "========================================"

echo "Git commit:"
git rev-parse HEAD || true
git rev-parse --short HEAD || true

export DJANGO_SETTINGS_MODULE=engineeringcollege.settings
export PYTHONUNBUFFERED=1

echo "Upgrading pip..."
pip install --upgrade pip

if [[ "$ON_RENDER" == "True" ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing system dependencies for WeasyPrint..."
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
        && echo "System dependencies installed"
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p staticfiles media

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell << 'EOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

if not all((username, email, password)):
    print("Superuser environment variables are not set; skipping creation.")
elif not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")
EOF

echo "========================================"
echo "Build completed successfully!"
echo "========================================"
