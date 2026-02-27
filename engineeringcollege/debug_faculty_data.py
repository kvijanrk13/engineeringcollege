# debug_faculty_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty


def debug_faculty_complete(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))

        print(f"\n{'=' * 60}")
        print(f"COMPLETE FACULTY DATA FOR: {faculty.staff_name} (Code: {faculty.employee_code})")
        print(f"{'=' * 60}\n")

        # Get all fields that have values
        print("POPULATED FIELDS:")
        print("-" * 40)

        for field in Faculty._meta.fields:
            value = getattr(faculty, field.name)
            if value not in [None, '', 'Not Specified', 'Not Applicable']:
                # Handle special cases
                if hasattr(value, 'strftime'):  # Date fields
                    print(f"{field.name}: {value.strftime('%d-%m-%Y')}")
                elif hasattr(value, 'url'):  # File fields
                    print(f"{field.name}: {value.url}")
                else:
                    print(f"{field.name}: {value}")

        # Specifically check for education fields
        print("\nEDUCATION DETAILS:")
        print("-" * 40)
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
        print(f"UG Spec: {faculty.ug_spec}")
        print(f"PG Degree: {faculty.pg_degree}")
        print(f"PG Year: {faculty.pg_year}")
        print(f"PG Percentage: {faculty.pg_percentage}")
        print(f"PG College: {faculty.pg_college}")
        print(f"PG Spec: {faculty.pg_spec}")
        print(f"PhD Degree: {faculty.phd_degree}")
        print(f"PhD Year: {faculty.phd_year}")
        print(f"PhD University: {faculty.phd_university}")
        print(f"PhD Spec: {faculty.phd_spec}")

        # Check for document files
        print("\nDOCUMENT FILES:")
        print("-" * 40)
        print(f"Aadhar File: {faculty.aadhar_file.url if faculty.aadhar_file else 'Not uploaded'}")
        print(f"PAN File: {faculty.pan_file.url if faculty.pan_file else 'Not uploaded'}")
        print(f"APAAR File: {faculty.apaar_file.url if faculty.apaar_file else 'Not uploaded'}")
        print(f"SCM File: {faculty.scm_file.url if faculty.scm_file else 'Not uploaded'}")

    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")


if __name__ == "__main__":
    debug_faculty_complete(7001)