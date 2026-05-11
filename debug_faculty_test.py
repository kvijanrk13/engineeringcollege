import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()
from dashboard.models import Faculty
from dashboard.views import generate_faculty_pdf_bytes

faculty = Faculty.objects.filter(id=1).first()
print('faculty', faculty)
if faculty is None:
    print('Faculty id=1 not found')
else:
    try:
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        print('len', len(pdf_bytes) if pdf_bytes else 'None')
        with open('debug_faculty_1.pdf', 'wb') as f:
            f.write(pdf_bytes or b'')
        print('Wrote debug_faculty_1.pdf')
    except Exception:
        traceback.print_exc()
