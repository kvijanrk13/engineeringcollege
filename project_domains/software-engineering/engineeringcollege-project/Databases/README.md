# Databases

This folder documents the database layer for the EngineeringCollege Software Engineering project.

## Development Database

The project can run with PostgreSQL through `DATABASE_URL`. For student local execution, configure a local database URL in `.env`.

Example `.env` shape:

```text
SECRET_KEY=local-development-key
DATABASE_URL=sqlite:///db.sqlite3
DEBUG=True
```

## Migration Commands

```powershell
cd "Project Source"
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

## What to Store Here

- schema notes
- migration screenshots
- ER diagrams
- backup/restore notes
- sample SQL queries

Do not store production credentials, private database URLs, or exported personal data.
