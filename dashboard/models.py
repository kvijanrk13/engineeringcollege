# dashboard/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
import os


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, null=True)
    credits = models.IntegerField(default=3)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Faculty(models.Model):
    # Personal Information
    staff_name = models.CharField(max_length=255, blank=False, null=False, default='')
    employee_code = models.CharField(max_length=50, unique=True, blank=False, null=False, default='')
    father_name = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    sub_caste = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, default='Indian')
    address = models.TextField(blank=True, null=True)

    # Contact Information
    mobile = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Professional Information
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    jntuh_id = models.CharField(max_length=100, blank=True, null=True)
    aicte_id = models.CharField(max_length=100, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    orcid_id = models.CharField(max_length=50, blank=True, null=True)

    # Education - SSC / 10TH
    ssc_year = models.IntegerField(blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_school = models.CharField(max_length=255, blank=True, null=True)

    # Education - Intermediate
    inter_year = models.IntegerField(blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_college = models.CharField(max_length=255, blank=True, null=True)

    # Education - UG
    ug_degree = models.CharField(max_length=100, blank=True, null=True)
    ug_year = models.IntegerField(blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)
    ug_college = models.CharField(max_length=255, blank=True, null=True)
    ug_spec = models.CharField(max_length=100, blank=True, null=True)

    # Education - PG
    pg_degree = models.CharField(max_length=100, blank=True, null=True)
    pg_year = models.IntegerField(blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)
    pg_college = models.CharField(max_length=255, blank=True, null=True)
    pg_spec = models.CharField(max_length=100, blank=True, null=True)

    # Education - PhD
    phd_degree = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('Completed', 'Completed'),
        ('Pursuing', 'Pursuing'),
        ('Not Started', 'Not Started'),
        ('', 'Not Specified')
    ])
    phd_year = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=255, blank=True, null=True)
    phd_spec = models.CharField(max_length=100, blank=True, null=True)

    # Additional Information
    subjects_dealt = models.TextField(blank=True, null=True, help_text="List of subjects handled, separated by commas")
    scm = models.TextField(blank=True, null=True, help_text="Service Cum Merit details")
    about_yourself = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True, help_text="Student results or academic performance")

    # Experience
    exp_anurag = models.CharField(max_length=50, blank=True, null=True,
                                  help_text="Experience at Anurag Engineering College")
    exp_other = models.CharField(max_length=50, blank=True, null=True, help_text="Experience at other institutions")

    # Photo
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)

    # ==================== NEW FIELDS ====================
    # Classes Taken
    classes_taken = models.IntegerField(blank=True, null=True, help_text="Number of classes taken by the faculty")

    # Experience Certificates
    experience_certificates = models.FileField(upload_to='faculty_docs/experience_certs/', blank=True, null=True)

    # Other Documents
    other_documents = models.FileField(upload_to='faculty_docs/other_docs/', blank=True, null=True)

    # Cloudinary URLs for new fields
    experience_certificates_url = models.URLField(blank=True, null=True, max_length=500)
    other_documents_url = models.URLField(blank=True, null=True, max_length=500)
    # ==================== END NEW FIELDS ====================

    # Document Files - Local Storage
    aadhar_file = models.FileField(upload_to='faculty_docs/aadhar/', blank=True, null=True)
    pan_file = models.FileField(upload_to='faculty_docs/pan/', blank=True, null=True)
    apaar_file = models.FileField(upload_to='faculty_docs/apaar/', blank=True, null=True)
    scm_file = models.FileField(upload_to='faculty_docs/scm/', blank=True, null=True)
    jntuh_biodata = models.FileField(upload_to='faculty_docs/biodata/', blank=True, null=True)

    # Education Certificates
    ssc_certificate = models.FileField(upload_to='faculty_docs/ssc/', blank=True, null=True)
    inter_certificate = models.FileField(upload_to='faculty_docs/inter/', blank=True, null=True)
    ug_certificate = models.FileField(upload_to='faculty_docs/ug/', blank=True, null=True)
    pg_certificate = models.FileField(upload_to='faculty_docs/pg/', blank=True, null=True)
    phd_certificate = models.FileField(upload_to='faculty_docs/phd/', blank=True, null=True)

    # Cloudinary URLs for existing documents
    aadhar_url = models.URLField(blank=True, null=True, max_length=500)
    pan_url = models.URLField(blank=True, null=True, max_length=500)
    apaar_url = models.URLField(blank=True, null=True, max_length=500)
    scm_url = models.URLField(blank=True, null=True, max_length=500)
    jntuh_biodata_url = models.URLField(blank=True, null=True, max_length=500)
    ssc_certificate_url = models.URLField(blank=True, null=True, max_length=500)
    inter_certificate_url = models.URLField(blank=True, null=True, max_length=500)
    ug_certificate_url = models.URLField(blank=True, null=True, max_length=500)
    pg_certificate_url = models.URLField(blank=True, null=True, max_length=500)
    phd_certificate_url = models.URLField(blank=True, null=True, max_length=500)

    pdf_document = models.FileField(upload_to='faculty_pdfs/', blank=True, null=True)
    cloudinary_pdf_url = models.URLField(blank=True, null=True, max_length=500)
    cloudinary_photo_url = models.URLField(blank=True, null=True, max_length=500)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return f"{self.staff_name} ({self.employee_code})"

    class Meta:
        ordering = ['staff_name']
        verbose_name_plural = "Faculty"


class FacultyProfile(models.Model):
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE, related_name='profile', blank=False, null=False)
    experience_other = models.CharField(max_length=100, blank=True, null=True)
    experience_at_anurag = models.CharField(max_length=100, blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Profile - {self.faculty.staff_name}"


class Certificate(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=200)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    cloudinary_url = models.URLField(blank=True, null=True, max_length=500)
    issued_by = models.CharField(max_length=200, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.staff_name}"


class FacultyLog(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    performed_by = models.CharField(max_length=150, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class CloudinaryUpload(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True)
    upload_type = models.CharField(max_length=50)
    cloudinary_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)
    uploaded_by = models.CharField(max_length=150, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.upload_type} - {self.public_id}"


class ResearchProject(models.Model):
    RESEARCH_TYPES = [
        ('journal', 'Journal Publication'),
        ('conference', 'Conference Paper'),
        ('book', 'Book/Chapter'),
        ('patent', 'Patent'),
        ('project', 'Research Project'),
        ('award', 'Award/Recognition'),
    ]
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='research_projects')
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPES)
    title_of_project = models.CharField(max_length=500)
    journal_name = models.CharField(max_length=300, blank=True, null=True)
    publisher_name = models.CharField(max_length=300, blank=True, null=True)
    marks_awarded = models.CharField(max_length=50, blank=True, null=True)
    doi = models.CharField(max_length=100, blank=True, null=True)
    issn_number = models.CharField(max_length=20, blank=True, null=True)
    volume = models.CharField(max_length=50, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_research_type_display()}: {self.title_of_project}"


class ResearchPublication(models.Model):
    RESEARCH_TYPES = [
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('book', 'Book Chapter'),
        ('patent', 'Patent'),
        ('project', 'Research Project'),
        ('award', 'Award/Recognition'),
    ]
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('accepted', 'Accepted'),
        ('under_review', 'Under Review'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
    ]
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='research_publications')
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPES)
    title = models.CharField(max_length=500)
    authors = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    doi = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=500, blank=True, null=True)
    journal_name = models.CharField(max_length=300, blank=True, null=True)
    issn = models.CharField(max_length=20, blank=True, null=True)
    volume = models.CharField(max_length=50, blank=True, null=True)
    issue = models.CharField(max_length=50, blank=True, null=True)
    page_numbers = models.CharField(max_length=50, blank=True, null=True)
    conference_name = models.CharField(max_length=300, blank=True, null=True)
    conference_location = models.CharField(max_length=200, blank=True, null=True)
    conference_dates = models.CharField(max_length=100, blank=True, null=True)
    book_title = models.CharField(max_length=300, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    filing_date = models.DateField(blank=True, null=True)
    grant_date = models.DateField(blank=True, null=True)
    project_title = models.CharField(max_length=300, blank=True, null=True)
    funding_agency = models.CharField(max_length=200, blank=True, null=True)
    sanction_amount = models.CharField(max_length=100, blank=True, null=True)
    award_title = models.CharField(max_length=300, blank=True, null=True)
    awarding_body = models.CharField(max_length=200, blank=True, null=True)
    award_date = models.DateField(blank=True, null=True)
    publisher_name = models.CharField(max_length=200, blank=True, null=True)
    proof_document = models.FileField(upload_to='research_proofs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_research_type_display()}: {self.title}"

    class Meta:
        ordering = ['-publication_year']


class FDP(models.Model):
    FDP_TYPES = [
        ('fdp', 'FDP'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('training', 'Training Program'),
    ]
    MODE_CHOICES = [('online', 'Online'), ('offline', 'Offline'), ('hybrid', 'Hybrid')]
    LEVEL_CHOICES = [('institute', 'Institute Level'), ('college', 'College Level'),
                     ('university', 'University Level'), ('state', 'State Level'),
                     ('national', 'National Level'), ('international', 'International Level')]
    ROLE_CHOICES = [('participant', 'Participant'), ('presenter', 'Presenter'),
                    ('resource_person', 'Resource Person'), ('organizer', 'Organizer'),
                    ('coordinator', 'Coordinator')]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='fdps')
    fdp_type = models.CharField(max_length=20, choices=FDP_TYPES)
    title = models.CharField(max_length=300)
    from_date = models.DateField()
    to_date = models.DateField()
    organized_by = models.CharField(max_length=200, blank=True, null=True)
    place = models.CharField(max_length=200, blank=True, null=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    sponsored_by = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    certificate = models.FileField(upload_to='fdp_certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def duration_days(self):
        if self.from_date and self.to_date:
            return (self.to_date - self.from_date).days + 1
        return 0

    def __str__(self):
        return f"{self.get_fdp_type_display()}: {self.title} ({self.faculty.staff_name})"

    class Meta:
        ordering = ['-from_date']
        verbose_name = "FDP/Workshop"
        verbose_name_plural = "FDPs/Workshops"


class BTechProject(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='btech_projects')
    ht_no = models.CharField(max_length=20)
    student_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=20, blank=True, null=True)
    project_title = models.CharField(max_length=500)
    approved = models.BooleanField(default=False)
    marks = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ht_no} - {self.project_title} ({self.faculty.staff_name})"

    class Meta:
        ordering = ['-batch']


class Student(models.Model):
    ht_no = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=100, default='Indian')
    category = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    student_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    sem = models.IntegerField(blank=True, null=True)
    ssc_marks = models.CharField(max_length=20, blank=True, null=True)
    inter_marks = models.CharField(max_length=20, blank=True, null=True)
    cgpa = models.CharField(max_length=10, blank=True, null=True)
    task_registered = models.CharField(max_length=10, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    task_username = models.CharField(max_length=100, blank=True, null=True)
    csi_registered = models.CharField(max_length=10, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)
    admission_type = models.CharField(max_length=50, blank=True, null=True)
    other_admission_details = models.TextField(blank=True, null=True)
    eamcet_rank = models.CharField(max_length=20, blank=True, null=True)
    rtrp_project_title = models.CharField(max_length=500, blank=True, null=True)
    intern_title = models.CharField(max_length=500, blank=True, null=True)
    final_project_title = models.CharField(max_length=500, blank=True, null=True)
    other_training = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True, max_length=500)
    cert_achieve = models.FileField(upload_to='student_certs/achievement/', blank=True, null=True)
    cert_intern = models.FileField(upload_to='student_certs/internship/', blank=True, null=True)
    cert_courses = models.FileField(upload_to='student_certs/courses/', blank=True, null=True)
    cert_sdp = models.FileField(upload_to='student_certs/sdp/', blank=True, null=True)
    cert_extra = models.FileField(upload_to='student_certs/extra/', blank=True, null=True)
    cert_placement = models.FileField(upload_to='student_certs/placement/', blank=True, null=True)
    cert_national = models.FileField(upload_to='student_certs/national/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='student_pdfs/', blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True, max_length=500)
    pdf_generated = models.BooleanField(default=False)
    pdf_generation_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_name} ({self.ht_no})"

    class Meta:
        ordering = ['-created_at']