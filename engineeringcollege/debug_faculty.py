# debug_faculty.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty, Certificate, ResearchProject, FacultyProfile


def debug_faculty(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        print(f"\n{'=' * 50}")
        print(f"FACULTY: {faculty.staff_name} (ID: {faculty.id}, Code: {faculty.employee_code})")
        print(f"{'=' * 50}")

        # Check all faculty fields
        print("\n--- FACULTY FIELDS ---")
        for field in Faculty._meta.fields:
            value = getattr(faculty, field.name)
            if value:
                print(f"{field.name}: {value}")

        # Check certificates
        print(f"\n--- CERTIFICATES ({faculty.certificates.count()}) ---")
        for cert in faculty.certificates.all():
            print(f"ID: {cert.id}, Type: {cert.certificate_type}")
            print(f"  File: {cert.certificate_file}")
            print(f"  Cloudinary URL: {cert.cloudinary_url}")

        # Check research projects
        print(f"\n--- RESEARCH PROJECTS ({faculty.research_projects.count()}) ---")
        for project in faculty.research_projects.all():
            print(f"ID: {project.id}, Type: {project.research_type}")
            print(f"  Title: {project.title_of_project}")
            print(f"  Journal: {project.journal_name}")
            print(f"  PDF: {project.upload_pdf}")

        # Check faculty profile
        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
            print(f"\n--- FACULTY PROFILE ---")
            print(f"Batch: {profile.batch_number}")
            print(f"Projects: {profile.projects_done}")
            print(f"SSC Year: {profile.ssc_year}, Percentage: {profile.ssc_percentage}")
        except FacultyProfile.DoesNotExist:
            print("\n--- No Faculty Profile ---")

    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")


if __name__ == "__main__":
    debug_faculty(7001)