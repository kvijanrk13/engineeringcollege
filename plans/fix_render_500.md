# Plan: Fix Render 500 on /dashboard/dashboard

1. Reproduce locally using production-like settings (DEBUG=False, use PostgreSQL if possible).
2. Verify `dashboard/views.py` for missing `dashboard` view and ensure URL names align.
3. Update `dashboard/urls.py` to point `/dashboard/dashboard/` to `admin_dashboard` if no separate view is required.
4. Add robust logging around `admin_dashboard` to log DB connectivity, query results, and exceptions.
5. Confirm `admin_dashboard.html` renders with provided context keys (e.g., `faculty`, `departments`).
6. Run `python -m py_compile dashboard/views.py` plus `manage.py check` to catch syntax/config issues.
7. Deploy to Render, watch live logs while hitting `/dashboard/dashboard/` to catch runtime errors.
8. If PostgreSQL errors appear (e.g., missing tables), run migrations against Render DB.
9. Confirm https://engineeringcollege.onrender.com loads login (public) and `/dashboard/dashboard/` after admin login.
