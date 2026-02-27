# test_pdf_with_debug.py
import os
import sys
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

# Now import Django modules after setup
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from dashboard.models import Faculty
from dashboard.views import generate_faculty_pdf

def test_pdf_with_debug(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        print(f"\n{'='*60}")
        print(f"TESTING PDF GENERATION FOR: {faculty.staff_name}")
        print(f"{'='*60}\n")
        
        # Print all faculty data for verification
        print("FACULTY DATA IN DATABASE:")
        print("-" * 40)
        print(f"Name: {faculty.staff_name}")
        print(f"Father: {faculty.father_name}")
        print(f"Mother: {faculty.mother_name}")
        print(f"DOB: {faculty.dob}")
        print(f"SSC Year: {faculty.ssc_year}")
        print(f"SSC Percent: {faculty.ssc_percent}")
        print(f"SSC School: {faculty.ssc_school}")
        print(f"Inter Year: {faculty.inter_year}")
        print(f"Inter Percent: {faculty.inter_percent}")
        print(f"Inter College: {faculty.inter_college}")
        print(f"UG Degree: {faculty.ug_degree}")
        print(f"UG Year: {faculty.ug_year}")
        print(f"UG Percentage: {faculty.ug_percentage}")
        print(f"UG College: {faculty.ug_college}")
        print(f"PG Degree: {faculty.pg_degree}")
        print(f"PG Year: {faculty.pg_year}")
        print(f"PG Percentage: {faculty.pg_percentage}")
        print(f"PG College: {faculty.pg_college}")
        print(f"PhD Status: {faculty.phd_degree}")
        print(f"PhD University: {faculty.phd_university}")
        print(f"JNTUH ID: {faculty.jntuh_id}")
        print(f"AICTE ID: {faculty.aicte_id}")
        print(f"PAN: {faculty.pan}")
        print(f"Aadhar: {faculty.aadhar}")
        print(f"APAAR: {faculty.apaar_id}")
        print(f"ORCID: {faculty.orcid_id}")
        print(f"Subjects: {faculty.subjects_dealt}")
        print(f"Research: {faculty.about_yourself}")
        print(f"Results: {faculty.results}")
        print(f"SCM: {faculty.scm}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        print("\n" + "="*60)
        print("GENERATING PDF...")
        print("="*60)
        
        # Generate PDF
        response = generate_faculty_pdf(request, faculty.id)
        
        if response.status_code == 200:
            print(f"\n✓ PDF generated successfully!")
            
            # Save the PDF
            output_file = f"faculty_{faculty.employee_code}_test.pdf"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved to: {output_file}")
            print(f"  Full path: {os.path.abspath(output_file)}")
            
            # Also check if debug HTML was created
            debug_html = f"debug_faculty_{faculty.employee_code}.html"
            if os.path.exists(debug_html):
                print(f"✓ Debug HTML saved to: {debug_html}")
                print(f"  Open this file in a browser to check the content before PDF conversion")
            
        else:
            print(f"✗ PDF generation failed: {response.status_code}")
            print(f"  Error: {response.content}")
            
    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_with_debug(7001)