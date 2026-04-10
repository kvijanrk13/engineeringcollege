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

# Create or update the initial Django superuser when env vars are provided.
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ]; then
  echo "👤 Ensuring Django superuser exists..."
  python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); username='${DJANGO_SUPERUSER_USERNAME}'; email='${DJANGO_SUPERUSER_EMAIL}'; password='${DJANGO_SUPERUSER_PASSWORD}'; user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True}); user.email = email; user.is_staff = True; user.is_superuser = True; user.set_password(password); user.save(); print('Superuser created' if created else 'Superuser updated')"
else
  echo "ℹ️ DJANGO_SUPERUSER_* env vars not set; skipping superuser bootstrap."
fi

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
