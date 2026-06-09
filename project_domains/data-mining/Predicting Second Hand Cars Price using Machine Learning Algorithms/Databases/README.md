# Databases

This folder documents the database layer used by the standalone Data Mining car-pricing project.

## Local Database

The standalone `Source Code` Django project uses SQLite by default:

```text
Source Code/db.sqlite3
```

Students can regenerate it locally by running:

```powershell
cd "Source Code"
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

## Tables Created by Migrations

- `car_price_app_studentregistration`
- `car_price_app_executionlog`
- Django auth/session/admin tables

## What to Store Here

- database schema notes
- ER diagram exports
- migration screenshots
- sample SQL queries
- database backup notes

Do not store personal credentials, production database URLs, or private student information in this folder.
