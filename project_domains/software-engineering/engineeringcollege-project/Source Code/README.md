# EngineeringCollege Source Code

This folder contains the executable Django source code for the EngineeringCollege Department Management System.

## Important Files

- `manage.py`
- `requirements.txt`
- `engineeringcollege/settings.py`
- `engineeringcollege/urls.py`
- `dashboard/models.py`
- `dashboard/views.py`
- `dashboard/forms.py`
- `dashboard/urls.py`
- `dashboard/templates/`
- `templates/`
- `static/`

## Local Run Command Summary

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/dashboard/`
- `http://127.0.0.1:8000/faculty/`
- `http://127.0.0.1:8000/students/`
- `http://127.0.0.1:8000/syllabus/`
- `http://127.0.0.1:8000/gallery/`
