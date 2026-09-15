from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
import os
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db.models import Q, F


class TimeTable(models.Model):
    class Semester(models.TextChoices):
        SEM_2_1 = '2-1', '2-1'
        SEM_3_1 = '3-1', '3-1'
        SEM_4_1 = '4-1', '4-1'
    
    semester = models.CharField(max_length=10, choices=Semester.choices)
    year = models.IntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Time Table - {self.get_semester_display()} {self.year}"
    
    class Meta:
        unique_together = ['semester', 'year']
        ordering = ['semester', 'year']


class Period(models.Model):
    TIME_SLOTS = [
        ('9:00-10:00', '9:00 AM - 10:00 AM'),
        ('10:00-11:00', '10:00 AM - 11:00 AM'),
        ('11:00-12:00', '11:00 AM - 12:00 PM'),
        ('12:00-1:00', '12:00 PM - 1:00 PM'),
        ('2:00-3:00', '2:00 PM - 3:00 PM'),
        ('3:00-4:00', '3:00 PM - 4:00 PM'),
        ('4:00-5:00', '4:00 PM - 5:00 PM'),
    ]
    
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    period_order = models.IntegerField()
    
    def __str__(self):
        return f"{self.get_time_slot_display()} (Period {self.period_order})"
    
    class Meta:
        ordering = ['period_order']


class DayOfWeek(models.TextChoices):
    MONDAY = 'MON', 'Monday'
    TUESDAY = 'TUE', 'Tuesday'
    WEDNESDAY = 'WED', 'Wednesday'
    THURSDAY = 'THU', 'Thursday'
    FRIDAY = 'FRI', 'Friday'
    SATURDAY = 'SAT', 'Saturday'


class Faculty(models.Model):
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

    mobile = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    college_experiences = models.JSONField(
        default=list,
        blank=True,
        help_text="College-wise employment history with address and date range",
    )
    tstsabas_entries = models.JSONField(
        default=list,
        blank=True,
        help_text="Repeatable TSTSABAS professional information entries",
    )
    jntuh_id = models.CharField(max_length=100, blank=True, null=True)
    aicte_id = models.CharField(max_length=100, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    orcid_id = models.CharField(max_length=50, blank=True, null=True)

    ssc_year = models.IntegerField(blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_school = models.CharField(max_length=255, blank=True, null=True)

    inter_year = models.IntegerField(blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_college = models.CharField(max_length=255, blank=True, null=True)

    ug_degree = models.CharField(max_length=100, blank=True, null=True)
    ug_year = models.IntegerField(blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)
    ug_college = models.CharField(max_length=255, blank=True, null=True)
    ug_spec = models.CharField(max_length=100, blank=True, null=True)

    pg_degree = models.CharField(max_length=100, blank=True, null=True)
    pg_year = models.IntegerField(blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)
    pg_college = models.CharField(max_length=255, blank=True, null=True)
    pg_spec = models.CharField(max_length=100, blank=True, null=True)

    phd_degree = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('Completed', 'Completed'),
        ('Pursuing', 'Pursuing'),
        ('Not Started', 'Not Started'),
        ('', 'Not Specified')
    ])
    phd_title = models.CharField(max_length=500, blank=True, null=True)
    phd_year = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=255, blank=True, null=True)
    phd_spec = models.CharField(max_length=100, blank=True, null=True)

    subjects_dealt = models.TextField(blank=True, null=True, help_text="List of subjects handled, separated by commas")
    scm = models.TextField(blank=True, null=True, help_text="Service Cum Merit details")
    about_yourself = models.TextField(blank=True, null=True)
    membership_academic_year = models.CharField(max_length=20, blank=True, null=True)
    membership_in = models.CharField(max_length=255, blank=True, null=True)
    membership_id = models.CharField(max_length=100, blank=True, null=True)
    membership_proof = models.FileField(upload_to='faculty_docs/membership_proofs/', blank=True, null=True)
    membership_proof_url = models.URLField(blank=True, null=True, max_length=500)
    is_ratified = models.BooleanField(blank=True, null=True)
    pdf_password = models.CharField(max_length=128, blank=True, null=True)
    results = models.TextField(blank=True, null=True, help_text="Student results or academic performance")

    exp_anurag = models.CharField(max_length=50, blank=True, null=True,
                                  help_text="Experience at Engineering College")
    exp_other = models.CharField(max_length=50, blank=True, null=True, help_text="Experience at other institutions")

    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)

    classes_taken = models.IntegerField(blank=True, null=True, help_text="Number of classes taken by the faculty")

    research_proof = models.FileField(upload_to='faculty_docs/research_proofs/', blank=True, null=True)
    research_proof_url = models.URLField(blank=True, null=True, max_length=500)
    research_proof_academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="Academic year for research proof document")

    fdp_certificate = models.FileField(upload_to='faculty_docs/fdp_certificates/', blank=True, null=True)
    fdp_certificate_url = models.URLField(blank=True, null=True, max_length=500)
    fdp_certificate_academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="Academic year for FDP certificate")

    experience_certificates = models.FileField(upload_to='faculty_docs/experience_certs/', blank=True, null=True)
    experience_certificates_url = models.URLField(blank=True, null=True, max_length=500)
    experience_certificates_academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="Academic year for experience certificates")

    other_documents = models.FileField(upload_to='faculty_docs/other_docs/', blank=True, null=True)
    other_documents_url = models.URLField(blank=True, null=True, max_length=500)
    other_documents_academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="Academic year for other documents")

    aadhar_file = models.FileField(upload_to='faculty_docs/aadhar/', blank=True, null=True)
    pan_file = models.FileField(upload_to='faculty_docs/pan/', blank=True, null=True)
    apaar_file = models.FileField(upload_to='faculty_docs/apaar/', blank=True, null=True)
    scm_file = models.FileField(upload_to='faculty_docs/scm/', blank=True, null=True)
    jntuh_biodata = models.FileField(upload_to='faculty_docs/biodata/', blank=True, null=True)

    ssc_certificate = models.FileField(upload_to='faculty_docs/ssc/', blank=True, null=True)
    inter_certificate = models.FileField(upload_to='faculty_docs/inter/', blank=True, null=True)
    ug_certificate = models.FileField(upload_to='faculty_docs/ug/', blank=True, null=True)
    pg_certificate = models.FileField(upload_to='faculty_docs/pg/', blank=True, null=True)
    phd_certificate = models.FileField(upload_to='faculty_docs/phd/', blank=True, null=True)

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

    subjects = models.ManyToManyField('Subject', blank=True)

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
    academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="Academic year (e.g., 2023-24)")
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
    proof_document_url = models.URLField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_research_type_display()}: {self.title}"

    class Meta:
        ordering = ['-publication_year']


class StudentResearchPublication(models.Model):
    RESEARCH_TYPES = ResearchPublication.RESEARCH_TYPES
    STATUS_CHOICES = ResearchPublication.STATUS_CHOICES

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='research_publications')
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPES, blank=True, null=True)
    title = models.CharField(max_length=500)
    authors = models.TextField(blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    journal_name = models.CharField(max_length=300, blank=True, null=True)
    conference_name = models.CharField(max_length=300, blank=True, null=True)
    issn = models.CharField(max_length=20, blank=True, null=True)
    doi = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    proof_document = models.FileField(upload_to='student_research_proofs/', blank=True, null=True, max_length=500)
    proof_document_url = models.URLField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.ht_no} - {self.title}"

    class Meta:
        ordering = ['-publication_year', '-id']


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
    academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="Academic year (e.g., 2023-24)")
    organized_by = models.CharField(max_length=200, blank=True, null=True)
    place = models.CharField(max_length=200, blank=True, null=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    sponsored_by = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    certificate = models.FileField(upload_to='fdp_certificates/', blank=True, null=True)
    certificate_url = models.URLField(blank=True, null=True, max_length=500)
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


class ProjectDownloadPayment(models.Model):
    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('PHONEPE', 'PhonePe Gateway'),
        ('RECEIPT', 'Manual Receipt'),
    ]

    merchant_order_id = models.CharField(max_length=64, unique=True)
    session_key = models.CharField(max_length=64, db_index=True)
    domain_slug = models.SlugField(default='software-engineering', max_length=80)
    project_slug = models.SlugField(default='engineeringcollege-project', max_length=120)
    amount_paise = models.PositiveIntegerField(default=100000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='PHONEPE')
    phonepe_order_id = models.CharField(max_length=128, blank=True)
    payment_url = models.URLField(max_length=1000, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    receipt_student_name = models.CharField(max_length=160, blank=True)
    receipt_student_email = models.EmailField(blank=True)
    receipt_student_phone = models.CharField(max_length=30, blank=True)
    receipt_filename = models.CharField(max_length=255, blank=True)
    receipt_message = models.TextField(blank=True)
    receipt_uploaded_at = models.DateTimeField(blank=True, null=True)
    delivery_drive_link = models.URLField(max_length=1000, blank=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    admin_note = models.TextField(blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.merchant_order_id} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class KavachSecureFile(models.Model):
    transfer_id = models.CharField(max_length=24, unique=True, db_index=True)
    sender_name = models.CharField(max_length=120, blank=True)
    sender_email = models.EmailField(blank=True, db_index=True)
    receiver_name = models.CharField(max_length=120, blank=True)
    receiver_email = models.EmailField(blank=True, db_index=True)
    original_filename = models.CharField(max_length=255)
    encrypted_file = models.FileField(upload_to='kavach/encrypted/')
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)
    aes_key = models.CharField(max_length=64, blank=True)
    aes_nonce = models.CharField(max_length=32)
    encrypted_aes_key = models.TextField(blank=True)
    receiver_public_key = models.TextField(blank=True)
    access_code_hash = models.CharField(max_length=64, db_index=True)
    file_sha256_hash = models.CharField(max_length=64, blank=True, db_index=True)
    uploader_public_key = models.TextField(blank=True)
    digital_signature = models.TextField(blank=True)
    signature_algorithm = models.CharField(max_length=40, default='Ed25519-SHA256')
    encryption_algorithm = models.CharField(max_length=20, default='AES-GCM')
    expires_at = models.DateTimeField(blank=True, null=True, db_index=True)
    is_revoked = models.BooleanField(default=False, db_index=True)
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transfer_id} - {self.original_filename}"

    @property
    def file_extension(self):
        return Path(self.original_filename or '').suffix.lower().lstrip('.') or 'unknown'

    @property
    def file_category(self):
        extension = self.file_extension
        content_type = (self.content_type or '').lower()
        if extension in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tif', 'tiff', 'svg'} or content_type.startswith('image/'):
            return 'Image'
        if extension in {'doc', 'docx', 'odt', 'rtf'}:
            return 'Document'
        if extension in {'xls', 'xlsx', 'ods', 'csv'}:
            return 'Spreadsheet'
        if extension in {'ppt', 'pptx', 'odp'}:
            return 'Presentation'
        if extension == 'pdf' or content_type == 'application/pdf':
            return 'PDF'
        if extension in {'mp3', 'wav', 'aac', 'ogg', 'm4a', 'flac'} or content_type.startswith('audio/'):
            return 'Audio'
        if extension in {'mp4', 'mov', 'avi', 'mkv', 'webm', 'wmv'} or content_type.startswith('video/'):
            return 'Video'
        if extension in {'zip', 'rar', '7z', 'tar', 'gz'}:
            return 'Archive'
        return 'Other'

    @property
    def display_file_size(self):
        size = self.file_size or 0
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024 or unit == 'GB':
                return f"{size:.1f} {unit}" if unit != 'bytes' else f"{size} bytes"
            size /= 1024

    class Meta:
        ordering = ['-created_at']


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
    department = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    sem = models.IntegerField(blank=True, null=True)
    ssc_year = models.CharField(max_length=20, blank=True, null=True)
    ssc_school_name = models.CharField(max_length=255, blank=True, null=True)
    ssc_marks = models.CharField(max_length=20, blank=True, null=True)
    inter_year = models.CharField(max_length=20, blank=True, null=True)
    inter_college_name = models.CharField(max_length=255, blank=True, null=True)
    inter_marks = models.CharField(max_length=20, blank=True, null=True)
    btech_year = models.CharField(max_length=20, blank=True, null=True)
    ug_college_name = models.CharField(max_length=255, blank=True, null=True)
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
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True, max_length=500)
    photo_url = models.URLField(blank=True, null=True, max_length=500)
    cert_achieve = models.FileField(upload_to='student_certs/achievement/', blank=True, null=True, max_length=500)
    cert_intern = models.FileField(upload_to='student_certs/internship/', blank=True, null=True, max_length=500)
    cert_courses = models.FileField(upload_to='student_certs/courses/', blank=True, null=True, max_length=500)
    cert_sdp = models.FileField(upload_to='student_certs/sdp/', blank=True, null=True, max_length=500)
    cert_extra = models.FileField(upload_to='student_certs/extra/', blank=True, null=True, max_length=500)
    cert_placement = models.FileField(upload_to='student_certs/placement/', blank=True, null=True, max_length=500)
    cert_national = models.FileField(upload_to='student_certs/national/', blank=True, null=True, max_length=500)
    cert_achieve_additional = models.FileField(upload_to='student_certs/achievement/', blank=True, null=True, max_length=500)
    cert_intern_additional = models.FileField(upload_to='student_certs/internship/', blank=True, null=True, max_length=500)
    cert_courses_additional = models.FileField(upload_to='student_certs/courses/', blank=True, null=True, max_length=500)
    cert_sdp_additional = models.FileField(upload_to='student_certs/sdp/', blank=True, null=True, max_length=500)
    cert_extra_additional = models.FileField(upload_to='student_certs/extra/', blank=True, null=True, max_length=500)
    cert_placement_additional = models.FileField(upload_to='student_certs/placement/', blank=True, null=True, max_length=500)
    cert_national_additional = models.FileField(upload_to='student_certs/national/', blank=True, null=True, max_length=500)
    cert_achieve_url = models.URLField(blank=True, null=True, max_length=500)
    cert_intern_url = models.URLField(blank=True, null=True, max_length=500)
    cert_courses_url = models.URLField(blank=True, null=True, max_length=500)
    cert_sdp_url = models.URLField(blank=True, null=True, max_length=500)
    cert_extra_url = models.URLField(blank=True, null=True, max_length=500)
    cert_placement_url = models.URLField(blank=True, null=True, max_length=500)
    cert_national_url = models.URLField(blank=True, null=True, max_length=500)
    cert_achieve_additional_url = models.URLField(blank=True, null=True, max_length=500)
    cert_intern_additional_url = models.URLField(blank=True, null=True, max_length=500)
    cert_courses_additional_url = models.URLField(blank=True, null=True, max_length=500)
    cert_sdp_additional_url = models.URLField(blank=True, null=True, max_length=500)
    cert_extra_additional_url = models.URLField(blank=True, null=True, max_length=500)
    cert_placement_additional_url = models.URLField(blank=True, null=True, max_length=500)
    cert_national_additional_url = models.URLField(blank=True, null=True, max_length=500)
    pdf_file = models.FileField(upload_to='student_pdfs/', blank=True, null=True, max_length=500)
    pdf_url = models.URLField(blank=True, null=True, max_length=500)
    pdf_generated = models.BooleanField(default=False)
    pdf_generation_time = models.DateTimeField(blank=True, null=True)
    pdf_password = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_name} ({self.ht_no})"

    class Meta:
        ordering = ['-created_at']

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, null=True)
    credits = models.IntegerField(default=3)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class AuditLog(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.CharField(max_length=150, blank=True, db_index=True)
    action = models.CharField(max_length=80, db_index=True)
    file = models.CharField(max_length=255, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS, db_index=True)

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} - {self.user or 'anonymous'} - {self.action}"

    class Meta:
        ordering = ['-timestamp']


class SuspiciousActivity(models.Model):
    STATUS_OPEN = 'open'
    STATUS_REVIEWED = 'reviewed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_REVIEWED, 'Reviewed'),
    ]

    user = models.CharField(max_length=150, blank=True, db_index=True)
    activity_type = models.CharField(max_length=80, db_index=True)
    file = models.CharField(max_length=255, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    description = models.TextField(blank=True)
    event_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)
    first_seen_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_seen_at = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return f"{self.activity_type} - {self.user or 'anonymous'} - {self.status}"

    class Meta:
        ordering = ['-last_seen_at']


class ClassSchedule(models.Model):
    TIME_TYPES = [
        ('CLASS', 'Class'),
        ('LAB', 'Lab'),
    ]
    
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE, related_name='class_schedules')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='class_schedules')
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    time_type = models.CharField(max_length=10, choices=TIME_TYPES, default='CLASS')
    room_number = models.CharField(max_length=20, blank=True, null=True)
    lab_room_number = models.CharField(max_length=20, blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_schedules')
    students = models.ManyToManyField(Student, related_name='class_schedules', blank=True)
    semester = models.CharField(max_length=10, blank=True, null=True)
    
    def clean(self):
        self._validate_time_conflict()
    
    def _validate_time_conflict(self):
        conflicts = ClassSchedule.objects.filter(
            Q(day_of_week=self.day_of_week, period=self.period) |
            (Q(day_of_week=self.day_of_week, period=self.period) & 
             Q(lab_room_number=self.lab_room_number) & 
             Q(time_type='LAB') & 
             Q(studios__isnull=False) & 
             Q(pk__isnull=False) &
             ~Q(pk=self.pk)
        ))
        if conflicts.exists():
            conflict = conflicts.first()
            if conflict.time_type == 'LAB' and self.time_type == 'LAB':
                raise ValidationError(
                    f"Lab {self.subject_name} conflicts with {conflict.subject_name} in room {conflict.room_number or conflict.lab_room_number}"
                )
            elif conflict.subject_code == self.subject_code:
                raise ValidationError(
                    f"Subject {self.subject_name} already scheduled for {self.day_of_week} at {self.get_period_time()}"
                )
    
    def __str__(self):
        room = self.lab_room_number or self.room_number
        return f"{self.day_of_week}-{self.get_time_slot_display()} {self.subject_name} ({room})"
    
    class Meta:
        unique_together = ['timetable', 'day_of_week', 'period']
        ordering = ['day_of_week', 'period']
    
    @property
    def get_period_time(self):
        return self.time_slot
    
    @property
    def is_lab(self):
        return self.time_type == 'LAB'


class LabSchedule(models.Model):
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE, related_name='lab_schedules')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='lab_schedules')
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    lab_code = models.CharField(max_length=50)
    lab_name = models.CharField(max_length=200)
    lab_room = models.CharField(max_length=20, blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_schedules')
    students = models.ManyToManyField(Student, related_name='lab_schedules', blank=True)
    semester = models.CharField(max_length=10, blank=True, null=True)
    
    def clean(self):
        self._validate_time_conflict()
    
    def _validate_time_conflict(self):
        conflicts = LabSchedule.objects.filter(
            Q(day_of_week=self.day_of_week, period=self.period) |
            (Q(day_of_week=self.day_of_week, period=self.period) & 
             Q(lab_room=self.lab_room) & 
             Q(pk__isnull=False) &
             ~Q(pk=self.pk)
        ))
        if conflicts.exists():
            raise ValidationError(
                f"Lab {self.lab_name} conflicts with another lab in room {self.lab_room}"
            )
    
    def __str__(self):
        return f"{self.day_of_week}-{self.get_time_slot_display()} {self.lab_name} ({self.lab_room})"
    
    class Meta:
        unique_together = ['timetable', 'day_of_week', 'period', 'lab_room']
        ordering = ['day_of_week', 'period']
    
    @property
    def get_time_slot_display(self):
        return dict(Period.TIME_SLOTS)[self.period.time_slot]


class FacultySchedule(models.Model):
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE, related_name='faculty_schedules')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='faculty_schedules')
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='faculty_schedules')
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    time_type = models.CharField(max_length=10, choices=[('CLASS', 'Class'), ('LAB', 'Lab')], default='CLASS')
    
    def clean(self):
        self._validate_time_conflict()
    
    def _validate_time_conflict(self):
        conflicts = FacultySchedule.objects.filter(
            Q(day_of_week=self.day_of_week, period=self.period) &
            Q(faculty=self.faculty) &
            Q(pk__isnull=False) &
            ~Q(pk=self.pk)
        )
        if conflicts.exists():
            raise ValidationError(
                f"Faculty {self.faculty.staff_name} already scheduled for {self.day_of_week} at this time"
            )
    
    def __str__(self):
        return f"{self.day_of_week}-{self.get_time_slot_display()} {self.faculty.staff_name} ({self.subject_name})"
    
    class Meta:
        unique_together = ['timetable', 'day_of_week', 'period', 'faculty']
        ordering = ['day_of_week', 'period']
    
    @property
    def get_time_slot_display(self):
        return dict(Period.TIME_SLOTS)[self.period.time_slot]


class StudentAttendance(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        PRESENT = 'P', 'Present'
        ABSENT = 'A', 'Absent'
        EXCUSED = 'E', 'Excused'
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='attendance_records')
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='attendance_records', blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES.choices)
    
    def __str__(self):
        return f"{self.student.student_name} - {self.day_of_week}-{self.period.time_slot} {self.subject_name} ({self.get_status_display()})"
    
    class Meta:
        unique_together = ['student', 'date', 'period']
        ordering = ['-date', 'day_of_week', 'period']

    @property
    def is_present(self):
        return self.status == self.STATUS_CHOICES.PRESENT


class LabEnrollment(models.Model):
    lab_schedule = models.ForeignKey(LabSchedule, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lab_enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.student_name} - {self.lab_schedule.lab_name}"
    
    class Meta:
        unique_together = ['lab_schedule', 'student']
        ordering = ['lab_schedule', 'student__student_name']