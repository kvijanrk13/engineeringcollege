# EngineeringCollege Local Run Guide

Use these steps when a student downloads or clones the full EngineeringCollege Django project.

## Windows PowerShell

```powershell
cd "F:\IT DEPT DJANGO PROJECT\engineeringcollege"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Useful car-price URLs:

- `http://127.0.0.1:8000/car-price/`
- `http://127.0.0.1:8000/car-price/maruti-prices/`
- `http://127.0.0.1:8000/car-price/apriori/`
- `http://127.0.0.1:8000/car-price/research-paper/`

## Notes

- The full EngineeringCollege project uses the root `requirements.txt`.
- For local SQLite development, provide a local `.env` with a valid `DATABASE_URL` or use the existing configured development database.
- The standalone Data Mining car-pricing student project is in:
  `project_domains/data-mining/Predicting Second Hand Cars Price using Machine Learning Algorithms/Source Code/`
