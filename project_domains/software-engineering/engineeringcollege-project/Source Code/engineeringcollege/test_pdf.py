# test_pdf.py
import os
import django
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty
from dashboard.views import generate_faculty_pdf


def test_pdf_generation(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        print(f"Testing PDF generation for: {faculty.staff_name}")

        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        # Generate PDF
        response = generate_faculty_pdf(request, faculty.id)

        if response.status_code == 200:
            print(f"✓ PDF generated successfully!")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response['Content-Type']}")
            print(f"  Filename: {response['Content-Disposition']}")

            # Save a copy for inspection
            output_file = f"test_output_{faculty.employee_code}.pdf"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"  Saved to: {output_file}")
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
    test_pdf_generation(7001)