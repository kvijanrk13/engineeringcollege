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

## Scene 2: Local Setup

Open terminal:

```powershell
cd "Project Source"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Scene 3: Database Migration

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

## Scene 4: Run Server

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## Scene 5: Browser Walkthrough

Open homepage, dashboard, faculty/student pages, project showcase, and car-price module.

## Scene 6: Conclusion

Explain modules, database, test cases, and local execution flow.
