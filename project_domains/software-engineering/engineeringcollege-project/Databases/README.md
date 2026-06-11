# EngineeringCollege DBMS Notes

This folder documents the database layer for the EngineeringCollege Department Management System. It covers only the department-management database objects used for faculty, student, certificate, research, FDP, subject, project-guidance, profile, and audit-log workflows.

## Database Configuration

The application is a Django project, so database tables are created from Django models through migrations. PostgreSQL is recommended for deployment, while SQLite may be used for isolated local development or demonstrations.

Example local `.env` shape:

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

## Included Documentation

- `SCHEMA_NOTES.md` - DBMS schema description and sample queries
- UML ER diagrams are available in `../UML Diagrams/`

Do not store production credentials, private database URLs, or exported personal data in this folder.
