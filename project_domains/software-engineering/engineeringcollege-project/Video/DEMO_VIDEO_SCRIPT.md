# Demo Video Script

## Scene 1: Extracted ZIP

Show the folders:

- `Project Source`
- `Source Code`
- `Modules`
- `Documentation`
- `PPT`
- `Video`
- `Test Cases`
- `UML Diagrams`
- `Databases`

## Scene 2: Prerequisites

Confirm the system has:

- Python 3.10+
- pip
- Git or extracted project ZIP
- PostgreSQL for production-style setup, or SQLite for local practice

## Scene 3: Local Setup

Open terminal:

```powershell
cd "Project Source"
python -m venv .venv
.\.venv\Scripts\activate
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Scene 4: Environment Configuration

Create or update `.env` values when needed:

```powershell
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost
```

## Scene 5: Database Migration

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

## Scene 6: Admin User and Static Files

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

## Scene 7: Run Server

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## Scene 8: Browser Walkthrough

Open:

- `http://127.0.0.1:8000/`
- Admin login and dashboard
- Faculty dashboard and faculty profile PDF
- Student dashboard and student certificate/PDF pages
- Project domains and EngineeringCollege project page
- PhonePe receipt workflow
- Data-mining car-price module

## Scene 9: Verification

Verify:

- Login and logout work for each role
- Database records display correctly
- Certificate upload and PDF generation work
- UML diagrams and test cases are present
- Project folder ZIP/download workflow is ready

## Scene 10: Conclusion

Explain modules, database, test cases, UML diagrams, deployment, and complete local execution flow.
