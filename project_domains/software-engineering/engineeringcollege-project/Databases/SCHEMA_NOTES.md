# Schema Notes

Important Django models include:

- `Faculty`
- `Student`
- `Certificate`
- `ResearchPublication`
- `StudentResearchPublication`
- `FDP`
- `BTechProject`
- `ProjectDownloadPayment`
- `CloudinaryUpload`
- `FacultyLog`

Main app files:

- `Project Source/dashboard/models.py`
- `Project Source/dashboard/migrations/`
- `Project Source/engineeringcollege/settings.py`

Regenerate local tables with:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```
