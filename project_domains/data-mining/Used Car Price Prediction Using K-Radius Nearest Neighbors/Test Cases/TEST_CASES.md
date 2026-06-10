# Test Cases

## TC-01: Django Server Starts

Steps:

```powershell
cd "Source Code"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Expected result: server starts at `http://127.0.0.1:8000/`.

## TC-02: Registration Page Opens

URL: `http://127.0.0.1:8000/`

Expected result: student registration page is displayed.

## TC-03: Apriori Page Opens

URL: `http://127.0.0.1:8000/apriori/`

Expected result: Apriori association-rule output is displayed.

## TC-04: Train Model Command

```powershell
.\.venv\Scripts\python.exe train_model.py --dataset cardekho-depreciation
```

Expected result: model metrics and artifacts are generated.

## TC-05: Prediction Command

```powershell
.\.venv\Scripts\python.exe predict_price.py --year 2018 --mileage 45000 --fuel Petrol --transmission Manual --make Honda --model City --engine-size 1.5
```

Expected result: predicted price is printed in the terminal.
