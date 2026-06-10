# Schema Notes

## StudentRegistration

Purpose: stores local student registration details for the standalone project demo.

Fields:

- `full_name`
- `roll_number`
- `email`
- `department`
- `college`
- `created_at`

## ExecutionLog

Purpose: stores simple execution history for data-mining or model-running steps.

Fields:

- `algorithm`
- `dataset`
- `rows_executed`
- `created_at`

## Migration Files

The migration source files are stored in:

```text
Source Code/car_price_app/migrations/
```

The database can be recreated on any student laptop with:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```
