# Local Run Guide

This project can be executed in two ways.

## 1. Standalone Student Project

Run this when you download only the Data Mining car-pricing ZIP.

```powershell
cd "Source Code"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## 2. Main EngineeringCollege Project

Run this when you have the full `engineeringcollege` repository.

```powershell
cd "engineeringcollege"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/car-price/`.

## Student Checklist

- Confirm `Source Code/manage.py` exists.
- Run migrations before starting the server.
- Keep datasets in the `datasets/` folder beside `Source Code/`.
- Use `train_model.py` for ML model training.
- Use `apriori_analysis.py` for data-mining association rules.
- Use the Django pages for registration, execution workflow, and Apriori output.
