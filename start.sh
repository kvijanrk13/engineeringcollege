#!/usr/bin/env bash
set -e

echo "🚀 Starting application..."
echo "DATABASE_URL (masked): ${DATABASE_URL%%@*}@*****"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Create superuser (ignore if exists)
echo "👤 Ensuring superuser exists..."
python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || true

# Collect static files (in case they changed)
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Start gunicorn
echo "✅ Starting gunicorn..."
exec gunicorn engineeringcollege.wsgi:application --log-file -
