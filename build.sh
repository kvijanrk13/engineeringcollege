#!/usr/bin/env bash
set -o errexit

echo "Using Python:"
python --version

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
