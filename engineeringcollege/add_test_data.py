# add_test_data.py
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty, Certificate, ResearchProject, FacultyProfile


def add_test_data(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))

        # Create or update faculty profile
        profile, created = FacultyProfile.objects.get_or_create(faculty=faculty)
        profile.batch_number = "B2024-001"
        profile.student_name = "Research Scholar"  # if applicable
        profile.joining_date = date(2020, 6, 1)
        profile.ssc_year = 2000
        profile.ssc_percentage = 85.5
        profile.projects_done = "AI Research Project, Data Analytics Project, Cloud Computing Implementation"
        profile.save()
        print(f"✓ Profile {'created' if created else 'updated'}")

        # Add research projects
        projects = [
            {
                'research_type': 'journal',
                'title_of_project': 'Machine Learning in Healthcare',
                'journal_name': 'International Journal of Computer Science',
                'publisher_name': 'Springer',
                'volume': '15',
                'issn_number': '1234-5678',
                'doi': '10.1234/ijcs.2024.001',
                'marks_awarded': 85
            },
            {
                'research_type': 'conference',
                'title_of_project': 'Cloud Computing Security Challenges',
                'journal_name': 'IEEE Cloud Conference 2024',
                'publisher_name': 'IEEE',
                'volume': '5',
                'doi': '10.5678/ieee.2024.002',
                'marks_awarded': 90
            }
        ]

        for proj_data in projects:
            project, created = ResearchProject.objects.get_or_create(
                faculty=faculty,
                title_of_project=proj_data['title_of_project'],
                defaults=proj_data
            )
            print(f"✓ Research project: {project.title_of_project} ({'created' if created else 'exists'})")

        # Add a test certificate
        cert, created = Certificate.objects.get_or_create(
            faculty=faculty,
            certificate_type="Faculty Development Program",
            defaults={
                'issued_by': "AICTE",
                'issue_date': date(2024, 1, 15),
                'description': "One week FDP on AI/ML"
            }
        )
        print(f"✓ Certificate: {cert.certificate_type} ({'created' if created else 'exists'})")

        print("\n✓ Test data added successfully!")

    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")


if __name__ == "__main__":
    add_test_data(7001)