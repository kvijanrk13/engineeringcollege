# Test Cases

## TC-01: Django System Check

```powershell
cd "Project Source"
.\.venv\Scripts\python.exe manage.py check
```

Expected result: no system check issues.

## TC-02: Database Migration

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Expected result: all migrations apply successfully.

## TC-03: Server Start

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Expected result: local server starts at `http://127.0.0.1:8000/`.

## TC-04: Dashboard Page

Open `http://127.0.0.1:8000/`.

Expected result: homepage/dashboard content loads.

## TC-05: Car Price Module

Open `http://127.0.0.1:8000/car-price/`.

Expected result: car-price registration or execution page loads.

## TC-06: Project ZIP Payment Page

Open the Software Engineering project payment page from the project showcase.

Expected result: project details and download/payment action are visible.
