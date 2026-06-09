# Local Run Guide

Use these steps after extracting the EngineeringCollege Software Engineering ZIP.

```powershell
cd "Project Source"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/dashboard/`
- `http://127.0.0.1:8000/car-price/`

## Notes

- Add a local `.env` before running if database or third-party credentials are required.
- Do not commit real secrets or production credentials.
- Run migrations before opening admin, dashboard, student, faculty, or project pages.
