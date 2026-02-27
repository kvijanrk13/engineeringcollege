# debug_complete.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty, FacultyProfile, Certificate, ResearchProject

def debug_complete(faculty_id=7001):
    try:
        # Check Faculty model
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        
        print(f"\n{'='*60}")
        print(f"FACULTY MODEL DATA: {faculty.staff_name}")
        print(f"{'='*60}")
        
        # Important fields from Faculty model
        print("\n--- BASIC INFO ---")
        print(f"ID: {faculty.id}")
        print(f"Employee Code: {faculty.employee_code}")
        print(f"Name: {faculty.staff_name}")
        print(f"Father: {faculty.father_name}")
        print(f"Mother: {faculty.mother_name}")
        print(f"DOB: {faculty.dob}")
        print(f"Gender: {faculty.gender}")
        print(f"Email: {faculty.email}")
        print(f"Mobile: {faculty.mobile}")
        print(f"Department: {faculty.department}")
        print(f"Designation: {faculty.designation}")
        print(f"Joining Date: {faculty.joining_date}")
        
        print("\n--- EDUCATION (Faculty Model) ---")
        print(f"SSC Year: {faculty.ssc_year}")
        print(f"SSC Percent: {faculty.ssc_percent}")
        print(f"SSC School: {faculty.ssc_school}")
        print(f"Inter Year: {faculty.inter_year}")
        print(f"Inter Percent: {faculty.inter_percent}")
        print(f"UG Degree: {faculty.ug_degree}")
        print(f"UG Year: {faculty.ug_year}")
        print(f"UG Percentage: {faculty.ug_percentage}")
        print(f"PG Degree: {faculty.pg_degree}")
        print(f"PG Year: {faculty.pg_year}")
        print(f"PG Percentage: {faculty.pg_percentage}")
        print(f"PhD: {faculty.phd_degree}")
        
        print("\n--- PROFESSIONAL IDs ---")
        print(f"JNTUH: {faculty.jntuh_id}")
        print(f"AICTE: {faculty.aicte_id}")
        print(f"PAN: {faculty.pan}")
        print(f"Aadhar: {faculty.aadhar}")
        print(f"APAAR: {faculty.apaar_id}")
        
        # Check FacultyProfile model
        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
            print(f"\n{'='*60}")
            print(f"FACULTY PROFILE MODEL DATA")
            print(f"{'='*60}")
            print(f"Batch Number: {profile.batch_number}")
            print(f"Student Name: {profile.student_name}")
            print(f"Joining Date: {profile.joining_date}")
            print(f"Experience: {profile.experience_at_anurag}")
            print(f"SSC Year: {profile.ssc_year}")
            print(f"SSC Percentage: {profile.ssc_percentage}")
            print(f"Projects Done: {profile.projects_done}")
            print(f"Aadhar Doc: {profile.aadhar_document}")
            print(f"APAAR Doc: {profile.apaar_document}")
            print(f"PAN Doc: {profile.pan_document}")
            print(f"SCM Doc: {profile.scm_document}")
        except FacultyProfile.DoesNotExist:
            print("\n⚠ No FacultyProfile record found")
        
        # Check Research Projects
        projects = ResearchProject.objects.filter(faculty=faculty)
        print(f"\n{'='*60}")
        print(f"RESEARCH PROJECTS: {projects.count()}")
        print(f"{'='*60}")
        for project in projects:
            print(f"\n--- Project {project.id} ---")
            print(f"Type: {project.research_type}")
            print(f"Title: {project.title_of_project}")
            print(f"Journal: {project.journal_name}")
            print(f"Publisher: {project.publisher_name}")
            print(f"DOI: {project.doi}")
            print(f"ISSN: {project.issn_number}")
            print(f"Volume: {project.volume}")
            print(f"Marks: {project.marks_awarded}")
            print(f"PDF: {project.upload_pdf}")
        
        # Check Certificates
        certs = Certificate.objects.filter(faculty=faculty)
        print(f"\n{'='*60}")
        print(f"CERTIFICATES: {certs.count()}")
        print(f"{'='*60}")
        for cert in certs:
            print(f"\n--- Certificate {cert.id} ---")
            print(f"Type: {cert.certificate_type}")
            print(f"Issued By: {cert.issued_by}")
            print(f"Date: {cert.issue_date}")
            print(f"File: {cert.certificate_file}")
            print(f"Cloudinary: {cert.cloudinary_url}")
            
    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")

if __name__ == "__main__":
    debug_complete(7001)