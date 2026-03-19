# dashboard/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import os


# ==================== FACULTY MODEL ====================

class Faculty(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    PHD_STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pursuing', 'Pursuing'),
        ('Not Applicable', 'Not Applicable'),
    ]

    # Personal Information
    staff_name = models.CharField(max_length=200)
    employee_code = models.CharField(max_length=50, unique=True)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    caste = models.CharField(max_length=100, blank=True, null=True)
    sub_caste = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, default='Indian', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Contact Information
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)

    # Professional IDs
    jntuh_id = models.CharField(max_length=100, blank=True, null=True)
    aicte_id = models.CharField(max_length=100, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    orcid_id = models.CharField(max_length=50, blank=True, null=True)

    # Experience
    joining_date = models.DateField(blank=True, null=True)
    exp_anurag = models.CharField(max_length=100, blank=True, null=True)
    exp_other = models.CharField(max_length=100, blank=True, null=True)

    # Education - SSC
    ssc_year = models.IntegerField(blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_school = models.CharField(max_length=200, blank=True, null=True)

    # Education - Intermediate
    inter_year = models.IntegerField(blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_college = models.CharField(max_length=200, blank=True, null=True)

    # Education - UG
    ug_degree = models.CharField(max_length=100, blank=True, null=True)
    ug_year = models.IntegerField(blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)
    ug_college = models.CharField(max_length=200, blank=True, null=True)
    ug_spec = models.CharField(max_length=100, blank=True, null=True)

    # Education - PG
    pg_degree = models.CharField(max_length=100, blank=True, null=True)
    pg_year = models.IntegerField(blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)
    pg_college = models.CharField(max_length=200, blank=True, null=True)
    pg_spec = models.CharField(max_length=100, blank=True, null=True)

    # Education - PhD
    phd_degree = models.CharField(max_length=50, choices=PHD_STATUS_CHOICES, blank=True, null=True)
    phd_year = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=200, blank=True, null=True)
    phd_spec = models.CharField(max_length=100, blank=True, null=True)

    # Additional Information
    subjects_dealt = models.TextField(blank=True, null=True)
    scm = models.TextField(blank=True, null=True)  # Service/Consultancy/MOU
    about_yourself = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)  # Academic Performance

    # Documents
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    aadhar_file = models.FileField(upload_to='faculty_documents/aadhar/', blank=True, null=True)
    pan_file = models.FileField(upload_to='faculty_documents/pan/', blank=True, null=True)
    apaar_file = models.FileField(upload_to='faculty_documents/apaar/', blank=True, null=True)
    scm_file = models.FileField(upload_to='faculty_documents/scm/', blank=True, null=True)
    jntuh_biodata = models.FileField(upload_to='faculty_documents/jntuh_biodata/', blank=True, null=True)

    # Education Certificates
    ssc_certificate = models.FileField(upload_to='faculty_certificates/ssc/', blank=True, null=True)
    inter_certificate = models.FileField(upload_to='faculty_certificates/inter/', blank=True, null=True)
    ug_certificate = models.FileField(upload_to='faculty_certificates/ug/', blank=True, null=True)
    pg_certificate = models.FileField(upload_to='faculty_certificates/pg/', blank=True, null=True)
    phd_certificate = models.FileField(upload_to='faculty_certificates/phd/', blank=True, null=True)

    # PDF Document
    pdf_document = models.FileField(upload_to='faculty_pdfs/', blank=True, null=True)

    # Cloudinary URLs
    cloudinary_photo_url = models.URLField(blank=True, null=True)
    cloudinary_pdf_url = models.URLField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_name} ({self.employee_code})"

    class Meta:
        verbose_name_plural = "Faculties"
        ordering = ['staff_name']


# ==================== SUBJECT MODEL ====================

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==================== FACULTY PROFILE MODEL ====================

class FacultyProfile(models.Model):
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE, related_name='profile')
    experience_other = models.CharField(max_length=200, blank=True, null=True)
    experience_at_anurag = models.CharField(max_length=200, blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.faculty.staff_name}"


# ==================== CERTIFICATE MODEL ====================

class Certificate(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=200)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    cloudinary_url = models.URLField(blank=True, null=True)
    issued_by = models.CharField(max_length=200, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.staff_name}"


# ==================== RESEARCH PROJECT MODEL (EXISTING) ====================

class ResearchProject(models.Model):
    RESEARCH_TYPE_CHOICES = [
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('book', 'Book'),
        ('book_chapter', 'Book Chapter'),
        ('patent', 'Patent'),
        ('project', 'Research Project / Grant'),
        ('copyright', 'Copyright / IP'),
        ('award', 'Award / Recognition'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='research_projects')
    faculty_profile = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='research_projects',
                                        blank=True, null=True)

    research_type = models.CharField(max_length=50, choices=RESEARCH_TYPE_CHOICES, default='journal')
    title_of_project = models.CharField(max_length=500)
    marks_awarded = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Journal specific
    journal_name = models.CharField(max_length=500, blank=True, null=True)
    issn_number = models.CharField(max_length=50, blank=True, null=True)
    volume = models.CharField(max_length=50, blank=True, null=True)

    # Common fields
    doi = models.CharField(max_length=200, blank=True, null=True)
    publisher_name = models.CharField(max_length=500, blank=True, null=True)

    # File upload
    upload_pdf = models.FileField(upload_to='research_projects/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_research_type_display()} - {self.title_of_project[:50]}"


# ==================== NEW RESEARCH PUBLICATION MODEL ====================

class ResearchPublication(models.Model):
    RESEARCH_TYPE_CHOICES = [
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('book', 'Book'),
        ('book_chapter', 'Book Chapter'),
        ('patent', 'Patent'),
        ('project', 'Research Project / Grant'),
        ('copyright', 'Copyright / IP'),
        ('award', 'Award / Recognition'),
    ]

    STATUS_CHOICES = [
        ('published', 'Published'),
        ('accepted', 'Accepted'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
    ]

    JOURNAL_QUARTILE_CHOICES = [
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ]

    CONFERENCE_TYPE_CHOICES = [
        ('national', 'National'),
        ('international', 'International'),
    ]

    PRESENTATION_TYPE_CHOICES = [
        ('oral', 'Oral'),
        ('poster', 'Poster'),
        ('keynote', 'Keynote'),
    ]

    PATENT_STATUS_CHOICES = [
        ('filed', 'Filed'),
        ('published', 'Published'),
        ('granted', 'Granted'),
    ]

    PATENT_TYPE_CHOICES = [
        ('utility', 'Utility'),
        ('design', 'Design'),
        ('plant', 'Plant'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('minor', 'Minor'),
        ('major', 'Major'),
    ]

    PROJECT_STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    BOOK_TYPE_CHOICES = [
        ('authored', 'Authored'),
        ('edited', 'Edited'),
    ]

    AWARD_LEVEL_CHOICES = [
        ('national', 'National'),
        ('international', 'International'),
        ('institutional', 'Institutional'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='research_publications')

    # Common Fields
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPE_CHOICES)
    title = models.CharField(max_length=500)
    authors = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publisher_name = models.CharField(max_length=300, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    doi = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=500, blank=True, null=True)
    proof_document = models.FileField(upload_to='research_proofs/', blank=True, null=True)

    # Journal Fields
    journal_name = models.CharField(max_length=500, blank=True, null=True)
    issn = models.CharField(max_length=50, blank=True, null=True)
    e_issn = models.CharField(max_length=50, blank=True, null=True)
    volume = models.CharField(max_length=50, blank=True, null=True)
    issue = models.CharField(max_length=50, blank=True, null=True)
    page_numbers = models.CharField(max_length=50, blank=True, null=True)
    impact_factor = models.CharField(max_length=50, blank=True, null=True)
    quartile = models.CharField(max_length=5, choices=JOURNAL_QUARTILE_CHOICES, blank=True, null=True)
    indexed_in = models.CharField(max_length=200, blank=True, null=True)
    ugc_care_listed = models.BooleanField(default=False)
    open_access = models.BooleanField(default=False)

    # Conference Fields
    conference_name = models.CharField(max_length=500, blank=True, null=True)
    conference_type = models.CharField(max_length=20, choices=CONFERENCE_TYPE_CHOICES, blank=True, null=True)
    organizer = models.CharField(max_length=300, blank=True, null=True)
    conference_location = models.CharField(max_length=300, blank=True, null=True)
    conference_dates = models.CharField(max_length=100, blank=True, null=True)
    isbn = models.CharField(max_length=50, blank=True, null=True)
    proceedings_title = models.CharField(max_length=500, blank=True, null=True)
    presentation_type = models.CharField(max_length=20, choices=PRESENTATION_TYPE_CHOICES, blank=True, null=True)
    best_paper_award = models.BooleanField(default=False)

    # Book Fields
    book_title = models.CharField(max_length=500, blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    publication_place = models.CharField(max_length=200, blank=True, null=True)
    number_of_pages = models.IntegerField(blank=True, null=True)
    book_type = models.CharField(max_length=20, choices=BOOK_TYPE_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)

    # Book Chapter Fields
    chapter_title = models.CharField(max_length=500, blank=True, null=True)
    chapter_number = models.CharField(max_length=50, blank=True, null=True)
    editors = models.CharField(max_length=500, blank=True, null=True)

    # Patent Fields
    patent_title = models.CharField(max_length=500, blank=True, null=True)
    inventors = models.TextField(blank=True, null=True)
    applicant_name = models.CharField(max_length=300, blank=True, null=True)
    patent_number = models.CharField(max_length=100, blank=True, null=True)
    application_number = models.CharField(max_length=100, blank=True, null=True)
    filing_date = models.DateField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    grant_date = models.DateField(blank=True, null=True)
    patent_status = models.CharField(max_length=20, choices=PATENT_STATUS_CHOICES, blank=True, null=True)
    patent_office = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    patent_type = models.CharField(max_length=20, choices=PATENT_TYPE_CHOICES, blank=True, null=True)
    commercialized = models.BooleanField(default=False)
    license_details = models.TextField(blank=True, null=True)

    # Project Fields
    project_title = models.CharField(max_length=500, blank=True, null=True)
    principal_investigator = models.CharField(max_length=300, blank=True, null=True)
    co_investigators = models.TextField(blank=True, null=True)
    funding_agency = models.CharField(max_length=300, blank=True, null=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, blank=True, null=True)
    sanction_number = models.CharField(max_length=100, blank=True, null=True)
    sanction_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    fund_received = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, blank=True, null=True)
    outcomes = models.TextField(blank=True, null=True)

    # Copyright Fields
    copyright_registration_number = models.CharField(max_length=100, blank=True, null=True)
    copyright_registration_date = models.DateField(blank=True, null=True)
    copyright_office = models.CharField(max_length=200, blank=True, null=True)
    copyright_description = models.TextField(blank=True, null=True)

    # Award Fields
    award_title = models.CharField(max_length=500, blank=True, null=True)
    awarding_body = models.CharField(max_length=300, blank=True, null=True)
    award_date = models.DateField(blank=True, null=True)
    award_level = models.CharField(max_length=20, choices=AWARD_LEVEL_CHOICES, blank=True, null=True)
    award_description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_research_type_display()} - {self.title[:50]}"

    class Meta:
        ordering = ['-publication_year', '-created_at']


# ==================== FDP / WORKSHOP MODEL ====================

class FDP(models.Model):
    FDP_TYPE_CHOICES = [
        ('fdp', 'Faculty Development Program'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('sttp', 'Short Term Training Program (STTP)'),
        ('webinar', 'Webinar'),
    ]

    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]

    LEVEL_CHOICES = [
        ('national', 'National'),
        ('international', 'International'),
    ]

    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('coordinator', 'Coordinator'),
        ('resource_person', 'Resource Person'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='fdps')

    title = models.CharField(max_length=500)
    fdp_type = models.CharField(max_length=20, choices=FDP_TYPE_CHOICES)

    from_date = models.DateField()
    to_date = models.DateField()

    organized_by = models.CharField(max_length=300)
    place = models.CharField(max_length=200)

    mode = models.CharField(max_length=10, choices=MODE_CHOICES, blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, blank=True, null=True)

    sponsored_by = models.CharField(max_length=200, blank=True, null=True)

    certificate_upload = models.FileField(upload_to='fdp_certificates/', blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def duration_days(self):
        """Calculate duration in days"""
        if self.from_date and self.to_date:
            return (self.to_date - self.from_date).days + 1
        return 0

    def __str__(self):
        return f"{self.get_fdp_type_display()} - {self.title}"

    class Meta:
        verbose_name = "FDP/Workshop"
        verbose_name_plural = "FDPs/Workshops"
        ordering = ['-from_date']


# ==================== B.TECH PROJECT MODEL ====================

class BTechProject(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='btech_projects')

    ht_no = models.CharField(max_length=50)
    student_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=50, blank=True, null=True)
    project_title = models.CharField(max_length=500)
    approved = models.BooleanField(default=False)
    marks = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"

    class Meta:
        verbose_name = "B.Tech Project"
        verbose_name_plural = "B.Tech Projects"
        ordering = ['-batch', 'student_name']


# ==================== FACULTY LOG MODEL ====================

class FacultyLog(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True, null=True)
    performed_by = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


# ==================== CLOUDINARY UPLOAD MODEL ====================

class CloudinaryUpload(models.Model):
    UPLOAD_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('pdf', 'PDF'),
        ('certificate', 'Certificate'),
        ('aadhar', 'Aadhar'),
        ('pan', 'PAN'),
        ('apaar', 'APAAR'),
        ('scm', 'SCM'),
        ('jntuh_biodata', 'JNTUH Bio-Data'),
        ('ssc', 'SSC Certificate'),
        ('inter', 'Inter Certificate'),
        ('ug', 'UG Certificate'),
        ('pg', 'PG Certificate'),
        ('phd', 'PhD Certificate'),
        ('merged', 'Merged PDF'),
        ('merged_certificates', 'Merged Certificates'),
        ('merged_faculty_certs', 'Merged Faculty Certificates'),
        ('research_proof', 'Research Proof'),
        ('fdp_certificate', 'FDP Certificate'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='cloudinary_uploads')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='cloudinary_uploads')
    upload_type = models.CharField(max_length=50, choices=UPLOAD_TYPE_CHOICES)
    cloudinary_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50, default='image')
    uploaded_by = models.CharField(max_length=100, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.upload_type} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-upload_date']


# ==================== STUDENT MODEL ====================

class Student(models.Model):
    YEAR_CHOICES = [
        (1, 'I Year'),
        (2, 'II Year'),
        (3, 'III Year'),
        (4, 'IV Year'),
    ]

    SEM_CHOICES = [
        (1, 'I Semester'),
        (2, 'II Semester'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # Basic Information
    ht_no = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=100, default='Indian', blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)

    # Contact Information
    address = models.TextField(blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    student_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Academic Information
    branch = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    sem = models.IntegerField(choices=SEM_CHOICES, blank=True, null=True)
    admission_type = models.CharField(max_length=100, blank=True, null=True)
    other_admission_details = models.TextField(blank=True, null=True)
    eamcet_rank = models.CharField(max_length=50, blank=True, null=True)

    # TASK/CSI Information
    task_registered = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], blank=True, null=True)
    task_username = models.CharField(max_length=100, blank=True, null=True)
    csi_registered = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], blank=True, null=True)
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)

    # Academic Marks
    ssc_marks = models.CharField(max_length=50, blank=True, null=True)
    inter_marks = models.CharField(max_length=50, blank=True, null=True)
    cgpa = models.CharField(max_length=10, blank=True, null=True)

    # Projects
    rtrp_project_title = models.CharField(max_length=500, blank=True, null=True)
    intern_title = models.CharField(max_length=500, blank=True, null=True)
    final_project_title = models.CharField(max_length=500, blank=True, null=True)
    other_training = models.TextField(blank=True, null=True)

    # Files
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)

    # Certificate Files
    cert_achieve = models.FileField(upload_to='student_certificates/achievement/', blank=True, null=True)
    cert_intern = models.FileField(upload_to='student_certificates/internship/', blank=True, null=True)
    cert_courses = models.FileField(upload_to='student_certificates/courses/', blank=True, null=True)
    cert_sdp = models.FileField(upload_to='student_certificates/sdp/', blank=True, null=True)
    cert_extra = models.FileField(upload_to='student_certificates/extra/', blank=True, null=True)
    cert_placement = models.FileField(upload_to='student_certificates/placement/', blank=True, null=True)
    cert_national = models.FileField(upload_to='student_certificates/national/', blank=True, null=True)

    # PDF Generation
    pdf_file = models.FileField(upload_to='student_pdfs/', blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    pdf_generated = models.BooleanField(default=False)
    pdf_generation_time = models.DateTimeField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"

    class Meta:
        ordering = ['ht_no']