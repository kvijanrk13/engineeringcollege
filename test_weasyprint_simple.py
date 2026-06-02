#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty
from django.template.loader import render_to_string
from datetime import datetime, date
from weasyprint import HTML
import traceback

def test_faculty_pdf(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        print(f"Faculty found: {faculty.staff_name}")
        
        # Calculate experience
        experience = "N/A"
        if faculty.joining_date:
            today = date.today()
            joining = faculty.joining_date
            years = today.year - joining.year
            months = today.month - joining.month
            days = today.day - joining.day
            if days < 0:
                months -= 1
                if today.month == 1:
                    prev_month = 12
                    prev_year = today.year - 1
                else:
                    prev_month = today.month - 1
                    prev_year = today.year
                if prev_month in [4, 6, 9, 11]:
                    days_in_prev_month = 30
                elif prev_month == 2:
                    if (prev_year % 4 == 0 and prev_year % 100 != 0) or (prev_year % 400 == 0):
                        days_in_prev_month = 29
                    else:
                        days_in_prev_month = 28
                else:
                    days_in_prev_month = 31
                days += days_in_prev_month
            if months < 0:
                years -= 1
                months += 12
            experience = f"{years} Years {months} Months {days} Days"

        # Get related data
        certificates = faculty.certificate_set.all() if hasattr(faculty, 'certificate_set') else []
        research_projects = faculty.researchproject_set.all() if hasattr(faculty, 'researchproject_set') else []
        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
        except:
            profile = None

        subjects_list = [s.strip() for s in (faculty.subjects_dealt or '').split(',') if s.strip()]

        # Build context - minimal
        
        # Add photo URL (use Cloudinary URL if available)
        photo_url = faculty.cloudinary_photo_url if faculty.cloudinary_photo_url else ''
        
        context = {
            'faculty': faculty,
            'profile': profile,
            'photo_url': photo_url,
            'research_projects': research_projects,
            'certificates': certificates,
            'subjects_list': subjects_list,
            'experience': experience,
            'current_date': datetime.now(),
            'local_photo_path': None,
        }

        # Render HTML
        html_string = render_to_string('dashboard/faculty_pdf.html', context)
        print("HTML rendered successfully")
        
        # Save HTML for inspection
        with open('test_faculty_output.html', 'w', encoding='utf-8') as f:
            f.write(html_string)
        print("HTML saved to test_faculty_output.html")

        # Generate PDF with WeasyPrint
        print("Generating PDF with WeasyPrint...")
        base_url = os.path.abspath('.')
        pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()
        
        # Save PDF
        output_file = f"test_faculty_{faculty.employee_code}.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        print(f"SUCCESS: PDF saved to {output_file} ({len(pdf_bytes)} bytes)")
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_faculty_pdf(7001)
    input("\nPress Enter to exit...")
