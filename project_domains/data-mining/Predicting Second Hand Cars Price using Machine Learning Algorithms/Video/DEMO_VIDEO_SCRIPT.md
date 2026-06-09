# Demo Video Script

## Scene 1: Project Folder

Show the downloaded project folder containing:

- `Source Code`
- `Modules`
- `Documentation`
- `PPT`
- `Video`
- `Test Cases`
- `UML Diagrams`
- `datasets`

## Scene 2: Setup

Open terminal in `Source Code` and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Scene 3: Migrations and Server

Run:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Scene 4: Browser Demo

Open `http://127.0.0.1:8000/`, show registration, execution pages, and Apriori output.

## Scene 5: Command-Line ML Demo

Run:

```powershell
.\.venv\Scripts\python.exe train_model.py --dataset cardekho-depreciation
.\.venv\Scripts\python.exe predict_price.py --year 2018 --mileage 45000 --fuel Petrol --transmission Manual --make Honda --model City --engine-size 1.5
```

## Scene 6: Conclusion

Explain that the project runs locally and includes documentation, test cases, UML diagrams, and presentation material.
