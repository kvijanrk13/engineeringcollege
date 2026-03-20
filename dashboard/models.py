# dashboard/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from datetime import date
import datetime
import os


# =====================================================
# FACULTY MODEL
# =====================================================

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
    staff_name = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    employee_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    # Personal Information
    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    caste = models.CharField(max_length=100, blank=True, null=True)
    sub_caste = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True, default='Indian')

    # Identity Numbers
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    jntuh_id = models.CharField(max_length=100, blank=True, null=True)
    aicte_id = models.CharField(max_length=100, blank=True, null=True)
    orcid_id = models.CharField(max_length=100, blank=True, null=True)

    # Experience
    exp_anurag = models.CharField(max_length=100, blank=True, null=True)
    exp_other = models.CharField(max_length=100, blank=True, null=True)

    # Educational Qualifications — SSC
    ssc_year = models.IntegerField(blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_school = models.CharField(max_length=300, blank=True, null=True)

    # Educational Qualifications — Intermediate
    inter_year = models.IntegerField(blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_college = models.CharField(max_length=300, blank=True, null=True)

    # Educational Qualifications — UG
    ug_degree = models.CharField(max_length=200, blank=True, null=True)
    ug_year = models.IntegerField(blank=True, null=True)
    ug_college = models.CharField(max_length=300, blank=True, null=True)
    ug_spec = models.CharField(max_length=200, blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)

    # Educational Qualifications — PG
    pg_degree = models.CharField(max_length=200, blank=True, null=True)
    pg_year = models.IntegerField(blank=True, null=True)
    pg_college = models.CharField(max_length=300, blank=True, null=True)
    pg_spec = models.CharField(max_length=200, blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)

    # Educational Qualifications — PhD
    phd_degree = models.CharField(max_length=200, blank=True, null=True)
    phd_year = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=300, blank=True, null=True)
    phd_spec = models.CharField(max_length=200, blank=True, null=True)

    # Additional Information
    scm = models.CharField(max_length=100, blank=True, null=True)
    subjects_dealt = models.TextField(blank=True, null=True)
    about_yourself = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)

    # Photo
    photo = CloudinaryField("image", blank=True, null=True)

    # Cloudinary URL tracking
    cloudinary_photo_url = models.URLField(max_length=500, blank=True, null=True)
    cloudinary_pdf_url = models.URLField(max_length=500, blank=True, null=True)

    # Documents (PDF / raw)
    pdf_document = CloudinaryField("raw", blank=True, null=True)
    aadhar_file = CloudinaryField("raw", blank=True, null=True)
    pan_file = CloudinaryField("raw", blank=True, null=True)
    apaar_file = CloudinaryField("raw", blank=True, null=True)
    scm_file = CloudinaryField("raw", blank=True, null=True)
    jntuh_biodata = CloudinaryField("raw", blank=True, null=True)

    # Education Certificates (Images)
    ssc_certificate = CloudinaryField("image", blank=True, null=True)
    inter_certificate = CloudinaryField("image", blank=True, null=True)
    ug_certificate = CloudinaryField("image", blank=True, null=True)
    pg_certificate = CloudinaryField("image", blank=True, null=True)
    phd_certificate = CloudinaryField("image", blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.staff_name or self.employee_code or "Faculty"


# =====================================================
# CLOUDINARY UPLOAD MODEL (FIXED - WITH DEFAULTS)
# =====================================================

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

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cloudinary_uploads'
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cloudinary_uploads'
    )
    upload_type = models.CharField(max_length=50)  # 'photo', 'pdf', 'certificate', etc.
    cloudinary_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)  # 'image', 'raw', etc.
    uploaded_by = models.CharField(max_length=150, default='System')  # ← FIXED: Added default
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']
        app_label = 'dashboard'

    def __str__(self):
        return f"{self.upload_type} - {self.public_id}"


# =====================================================
# FACULTY PROFILE
# =====================================================

class FacultyProfile(models.Model):
    faculty = models.OneToOneField(
        Faculty,
        on_delete=models.CASCADE,
        related_name='profile',
        null=True, blank=True
    )

    batch_number = models.CharField(max_length=50, blank=True, null=True)
    experience_other = models.CharField(max_length=200, blank=True, null=True)
    experience_at_anurag = models.CharField(max_length=200, blank=True, null=True)

    # Documents (stored in Cloudinary)
    aadhar_document = CloudinaryField("raw", blank=True, null=True)
    apaar_document = CloudinaryField("raw", blank=True, null=True)
    pan_document = CloudinaryField("raw", blank=True, null=True)
    scm_document = CloudinaryField("raw", blank=True, null=True)

    joining_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_experience(self):
        if self.joining_date:
            today = date.today()
            exp = today.year - self.joining_date.year
            if (today.month < self.joining_date.month or
                    (today.month == self.joining_date.month and
                     today.day < self.joining_date.day)):
                exp -= 1
            return max(0, exp)
        return 0

    def save(self, *args, **kwargs):
        if self.joining_date and not self.experience_at_anurag:
            self.experience_at_anurag = str(self.calculate_experience()) + " Years"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.faculty.staff_name if self.faculty else 'Faculty'} Profile"


# =====================================================
# RESEARCH PROJECT
# =====================================================

class ResearchProject(models.Model):
    RESEARCH_TYPE_CHOICES = [
        ('patent', 'Patent'),
        ('conference', 'Conference'),
        ('book_chapter', 'Book Chapter'),
        ('journal', 'Journal'),
        ('book', 'Book'),
        ('project', 'Research Project / Grant'),
        ('copyright', 'Copyright / IP'),
        ('award', 'Award / Recognition'),
    ]

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='research_projects'
    )
    faculty_profile = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='research_projects',
        null=True, blank=True
    )

    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPE_CHOICES)
    title_of_project = models.CharField(max_length=500)

    # Publication details
    marks_awarded = models.CharField(max_length=100, blank=True, null=True)
    doi = models.CharField(max_length=200, blank=True, null=True)
    volume = models.CharField(max_length=100, blank=True, null=True)
    issn_number = models.CharField(max_length=100, blank=True, null=True)
    journal_name = models.CharField(max_length=300, blank=True, null=True)
    publisher_name = models.CharField(max_length=300, blank=True, null=True)

    # PDF upload
    upload_pdf = CloudinaryField("raw", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_research_type_display()} - {self.title_of_project[:50]}"


# =====================================================
# NEW RESEARCH PUBLICATION MODEL
# =====================================================

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
    proof_document = CloudinaryField("raw", blank=True, null=True)

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


# =====================================================
# FDP / WORKSHOP MODEL
# =====================================================

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

    certificate_upload = CloudinaryField("raw", blank=True, null=True)

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


# =====================================================
# B.TECH PROJECT MODEL
# =====================================================

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


# =====================================================
# STUDENT MODEL (UPDATED - SAFE FOR MIGRATIONS)
# =====================================================

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

    # ================= BASIC INFO =================

    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='Male'
    )

    dob = models.CharField(max_length=20)
    age = models.IntegerField(default=18)

    nationality = models.CharField(
        max_length=100,
        default="Indian"
    )

    category = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)

    aadhar = models.CharField(max_length=20)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)

    address = models.TextField()

    # FIXED FIELDS (WITH DEFAULTS)

    parent_phone = models.CharField(
        max_length=15,
        default="0000000000"
    )

    student_phone = models.CharField(
        max_length=15,
        default="0000000000"
    )

    email = models.EmailField(
        default="noemail@example.com"
    )

    # ================= ACADEMIC INFO =================

    task_registered = models.CharField(max_length=10, blank=True, null=True)
    task_username = models.CharField(max_length=100, blank=True, null=True)

    csi_registered = models.CharField(max_length=10, blank=True, null=True)
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)

    admission_type = models.CharField(max_length=50, blank=True, null=True)
    other_admission_details = models.TextField(blank=True, null=True)

    eamcet_rank = models.IntegerField(blank=True, null=True)

    year = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    sem = models.IntegerField(choices=SEM_CHOICES, blank=True, null=True)

    branch = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)

    ssc_marks = models.CharField(max_length=50, blank=True, null=True)
    inter_marks = models.CharField(max_length=50, blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)

    # ================= PROJECT INFO =================

    rtrp_project_title = models.CharField(max_length=500, blank=True, null=True)
    intern_title = models.CharField(max_length=500, blank=True, null=True)
    final_project_title = models.CharField(max_length=500, blank=True, null=True)

    other_training = models.TextField(blank=True, null=True)

    # ================= FILES =================

    photo = CloudinaryField("image", blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)

    # Certificates (Images)
    cert_achieve = CloudinaryField("image", blank=True, null=True)
    cert_intern = CloudinaryField("image", blank=True, null=True)
    cert_courses = CloudinaryField("image", blank=True, null=True)
    cert_sdp = CloudinaryField("image", blank=True, null=True)
    cert_extra = CloudinaryField("image", blank=True, null=True)
    cert_placement = CloudinaryField("image", blank=True, null=True)
    cert_national = CloudinaryField("image", blank=True, null=True)

    # ================= PDF =================

    pdf_file = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)

    pdf_generated = models.BooleanField(default=False)
    pdf_generation_time = models.DateTimeField(blank=True, null=True)

    # ================= META =================

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} ({self.ht_no})"


# =====================================================
# CERTIFICATE MODEL (FACULTY) - FIXED WITH DEFAULTS
# =====================================================

class Certificate(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    certificate_type = models.CharField(max_length=100)

    # Stored in Cloudinary
    certificate_file = CloudinaryField("raw", blank=True, null=True)
    cloudinary_url = models.URLField(max_length=500, blank=True, null=True)

    issued_by = models.CharField(max_length=200, blank=True, default='')  # ← FIXED: Added default
    issue_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, default='')  # ← FIXED: Added default

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.staff_name}"


# =====================================================
# FACULTY LOG - FIXED WITH DEFAULTS
# =====================================================

class FacultyLog(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs'
    )
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True, default='')  # ← FIXED: Added default
    performed_by = models.CharField(max_length=150, default='System')  # ← FIXED: Added default
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.created_at}"


# =====================================================
# SUBJECT MODEL
# =====================================================

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)

    faculty = models.ManyToManyField(
        Faculty,
        related_name='subjects',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name