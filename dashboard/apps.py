# dashboard/apps.py

from django.apps import AppConfig
import sys
import traceback
import os
import threading


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        """
        Safe startup initialization (NON-BLOCKING & RUNS ONCE)
        """

        print("=== DASHBOARD APP READY METHOD STARTING ===", file=sys.stderr)

        # -------------------------------------------------
        # ✅ RUN ONLY ON MAIN PROCESS
        # -------------------------------------------------
        if os.environ.get('RUN_MAIN') != 'true':
            print("Skipping startup (not main process)", file=sys.stderr)
            return

        # -------------------------------------------------
        # ✅ SKIP DURING MANAGEMENT COMMANDS
        # -------------------------------------------------
        management_commands = [
            'migrate', 'makemigrations', 'shell', 'collectstatic',
            'flush', 'test', 'createsuperuser', 'changepassword'
        ]

        for cmd in management_commands:
            if cmd in sys.argv:
                print(f"SKIP: Running {cmd}, skipping startup checks", file=sys.stderr)
                return

        # -------------------------------------------------
        # ✅ RUN STARTUP TASK IN BACKGROUND THREAD (FIX)
        # -------------------------------------------------
        def startup_task():
            try:
                print("Importing check_pdf_url_column...", file=sys.stderr)

                from .startup import check_pdf_url_column

                print("Calling check_pdf_url_column...", file=sys.stderr)
                result = check_pdf_url_column()

                print(f"[SUCCESS] check_pdf_url_column returned: {result}", file=sys.stderr)

            except Exception as e:
                print(f"[ERROR] in startup_task: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

            print("=== DASHBOARD STARTUP TASK COMPLETED ===", file=sys.stderr)

        try:
            threading.Thread(target=startup_task, daemon=True).start()
        except Exception as e:
            print(f"[ERROR] starting thread: {e}", file=sys.stderr)

        print("=== DASHBOARD APP READY METHOD COMPLETED ===", file=sys.stderr)