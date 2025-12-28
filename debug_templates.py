import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()


def check_template_config():
    print("=== Django Template Configuration Check ===")
    print(f"BASE_DIR: {settings.BASE_DIR}")
    print(f"TEMPLATE DIRS: {settings.TEMPLATES[0]['DIRS']}")

    templates_dir = settings.BASE_DIR / 'templates'
    print(f"\\nExpected templates path: {templates_dir}")
    print(f"Templates directory exists: {templates_dir.exists()}")

    if templates_dir.exists():
        files = list(templates_dir.iterdir())
        print(f"Number of template files: {len(files)}")
        print("Template files:")
        for file in files:
            print(f"  - {file.name}")

        login_exists = (templates_dir / 'login.html').exists()
        print(f"\\nlogin.html exists: {login_exists}")
    else:
        print("ERROR: Templates directory does not exist!")

    print("\\n=== TEMPLATES setting ===")
    for key, value in settings.TEMPLATES[0].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    check_template_config()