# weasyprint_test.py
import os
import django
from django.template.loader import render_to_string
from datetime import datetime, date
from weasyprint import HTML

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty, Certificate, ResearchProject, FacultyProfile

def generate_pdf_with_weasyprint(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        
        print(f"\n{'='*60}")
        print(f"WEASYPRINT PDF GENERATION FOR: {faculty.staff_name}")
        print(f"{'='*60}\n")
        
        # Calculate experience (same as before)
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

        # Get certificates and research projects
        certificates = Certificate.objects.filter(faculty=faculty)
        research_projects = ResearchProject.objects.filter(faculty=faculty)
        
        # Get faculty profile
        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
        except FacultyProfile.DoesNotExist:
            profile = None

        # Prepare subjects list
        subjects_list = []
        if faculty.subjects_dealt:
            subjects_list = [s.strip() for s in faculty.subjects_dealt.split(',') if s.strip()]

        # Prepare context
        context = {
            'faculty': faculty,
            'profile': profile,
            'research_projects': research_projects,
            'certificates': certificates,
            'subjects_list': subjects_list,
            'experience': experience,
            'current_date': datetime.now(),
            'local_photo_path': None,
            
            # All fields
            'ssc_year': faculty.ssc_year,
            'ssc_percent': faculty.ssc_percent,
            'ssc_school': faculty.ssc_school,
            'inter_year': faculty.inter_year,
            'inter_percent': faculty.inter_percent,
            'inter_college': faculty.inter_college,
            'ug_degree': faculty.ug_degree,
            'ug_year': faculty.ug_year,
            'ug_percentage': faculty.ug_percentage,
            'ug_college': faculty.ug_college,
            'ug_spec': faculty.ug_spec,
            'pg_degree': faculty.pg_degree,
            'pg_year': faculty.pg_year,
            'pg_percentage': faculty.pg_percentage,
            'pg_college': faculty.pg_college,
            'pg_spec': faculty.pg_spec,
            'phd_degree': faculty.phd_degree,
            'phd_year': faculty.phd_year,
            'phd_university': faculty.phd_university,
            'phd_spec': faculty.phd_spec,
            'jntuh_id': faculty.jntuh_id,
            'aicte_id': faculty.aicte_id,
            'pan': faculty.pan,
            'aadhar': faculty.aadhar,
            'apaar_id': faculty.apaar_id,
            'orcid_id': faculty.orcid_id,
            'subjects_dealt': faculty.subjects_dealt,
            'about_yourself': faculty.about_yourself,
            'results': faculty.results,
            'scm': faculty.scm,
            
            # Document flags
            'has_aadhar': bool(faculty.aadhar_file),
            'has_pan': bool(faculty.pan_file),
            'has_apaar': bool(faculty.apaar_file),
            'has_scm': bool(faculty.scm_file),
        }

        # Render HTML
        html_string = render_to_string('dashboard/faculty_pdf.html', context)
        
        # Save HTML for debugging
        html_file = f"weasyprint_test_{faculty.employee_code}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_string)
        print(f"✓ HTML saved to: {html_file}")
        
        # Generate PDF with weasyprint
        print("\nGenerating PDF with weasyprint...")
        pdf_file = f"weasyprint_test_{faculty.employee_code}.pdf"
        HTML(string=html_string).write_pdf(pdf_file)
        print(f"✓ PDF saved to: {pdf_file}")
        
    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_pdf_with_weasyprint(7001)