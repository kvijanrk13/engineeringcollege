# simple_pdf_test.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty
from django.template.loader import render_to_string
from datetime import datetime

def simple_test(faculty_id=7001):
    faculty = Faculty.objects.get(employee_code=str(faculty_id))
    
    print("Rendering template with faculty data...")
    
    context = {
        'faculty': faculty,
        'current_date': datetime.now(),
    }
    
    html = render_to_string('dashboard/faculty_pdf.html', context)
    
    # Save HTML to file
    output_file = f"simple_test_{faculty.employee_code}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML saved to: {output_file}")
    print(f"Open this file in a browser to see what data is being passed")

if __name__ == "__main__":
    simple_test(7001)