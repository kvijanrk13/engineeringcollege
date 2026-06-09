# Source Code

The executable Software Engineering project source is the main Django repository.

In the downloadable ZIP, open:

```text
Project Source/
```

Important files:

- `Project Source/manage.py`
- `Project Source/requirements.txt`
- `Project Source/engineeringcollege/settings.py`
- `Project Source/dashboard/`
- `Project Source/car_price_app/`
- `Project Source/project_domains/`

Local run command summary:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```
