# dashboard/models.py

from django.db import models
from cloudinary.models import CloudinaryField
from datetime import date


# =====================================================
# FACULTY MODEL
# =====================================================

class Faculty(models.Model):
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

    # Additional fields
    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    scm = models.CharField(max_length=100, blank=True, null=True)

    # Educational qualifications
    ug_degree = models.CharField(max_length=200, blank=True, null=True)
    ug_year = models.IntegerField(blank=True, null=True)
    ug_college = models.CharField(max_length=300, blank=True, null=True)
    ug_spec = models.CharField(max_length=200, blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)

    pg_degree = models.CharField(max_length=200, blank=True, null=True)
    pg_year = models.IntegerField(blank=True, null=True)
    pg_college = models.CharField(max_length=300, blank=True, null=True)
    pg_spec = models.CharField(max_length=200, blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)

    phd_degree = models.CharField(max_length=200, blank=True, null=True)
    phd_year = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=300, blank=True, null=True)
    phd_spec = models.CharField(max_length=200, blank=True, null=True)

    # Other fields
    subjects_dealt = models.TextField(blank=True, null=True)
    about_yourself = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)

    # SSC and Intermediate
    ssc_year = models.IntegerField(blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_school = models.CharField(max_length=300, blank=True, null=True)

    inter_year = models.IntegerField(blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_college = models.CharField(max_length=300, blank=True, null=True)

    # IDs
    jntuh_id = models.CharField(max_length=100, blank=True, null=True)
    aicte_id = models.CharField(max_length=100, blank=True, null=True)
    orcid_id = models.CharField(max_length=100, blank=True, null=True)

    # Photo
    photo = CloudinaryField("image", blank=True, null=True)

    # Cloudinary URLs (for tracking uploaded files)
    cloudinary_photo_url = models.URLField(max_length=500, blank=True, null=True)
    cloudinary_pdf_url = models.URLField(max_length=500, blank=True, null=True)

    # Documents (PDF / raw)
    pdf_document = CloudinaryField("raw", blank=True, null=True)
    aadhar_file = CloudinaryField("raw", blank=True, null=True)
    pan_file = CloudinaryField("raw", blank=True, null=True)
    apaar_file = CloudinaryField("raw", blank=True, null=True)
    scm_file = CloudinaryField("raw", blank=True, null=True)

    # Certificates (Images)
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
# CLOUDINARY UPLOAD MODEL
# =====================================================

class CloudinaryUpload(models.Model):
    """Track uploads to Cloudinary"""
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='cloudinary_uploads')
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='cloudinary_uploads')
    upload_type = models.CharField(max_length=50)  # 'photo', 'pdf', 'certificate', etc.
    cloudinary_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)  # 'image', 'raw', etc.
    uploaded_by = models.CharField(max_length=150)
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
        null=True,
        blank=True
    )

    batch_number = models.CharField(max_length=50, blank=True, null=True)

    # All files stored in Cloudinary
    aadhar_document = CloudinaryField("raw", blank=True, null=True)
    apaar_document = CloudinaryField("raw", blank=True, null=True)
    pan_document = CloudinaryField("raw", blank=True, null=True)
    scm_document = CloudinaryField("raw", blank=True, null=True)

    joining_date = models.DateField(null=True, blank=True)
    experience_at_anurag = models.IntegerField(default=0, editable=False)
    experience_other = models.IntegerField(blank=True, null=True)

    def calculate_experience(self):
        if self.joining_date:
            today = date.today()
            exp = today.year - self.joining_date.year
            if today.month < self.joining_date.month or (
                    today.month == self.joining_date.month and
                    today.day < self.joining_date.day
            ):
                exp -= 1
            return max(0, exp)
        return 0

    def save(self, *args, **kwargs):
        if self.joining_date:
            self.experience_at_anurag = self.calculate_experience()
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
        null=True,
        blank=True
    )

    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPE_CHOICES)
    title_of_project = models.CharField(max_length=500)

    # Additional fields
    marks_awarded = models.CharField(max_length=100, blank=True, null=True)
    doi = models.CharField(max_length=200, blank=True, null=True)
    volume = models.CharField(max_length=100, blank=True, null=True)
    issn_number = models.CharField(max_length=100, blank=True, null=True)
    journal_name = models.CharField(max_length=300, blank=True, null=True)
    publisher_name = models.CharField(max_length=300, blank=True, null=True)

    # PDF upload
    upload_pdf = CloudinaryField("raw", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_research_type_display()} - {self.title_of_project[:50]}"


# =====================================================
# STUDENT MODEL
# =====================================================

class Student(models.Model):
    # Basic Info
    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=20)
    dob = models.CharField(max_length=20)
    age = models.IntegerField()

    nationality = models.CharField(max_length=100, blank=True, null=True, default="Indian")
    category = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhar = models.CharField(max_length=20)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)

    address = models.TextField()
    parent_phone = models.CharField(max_length=15)
    student_phone = models.CharField(max_length=15)
    email = models.EmailField()

    # Academic Info
    task_registered = models.CharField(max_length=10, blank=True, null=True)
    task_username = models.CharField(max_length=100, blank=True, null=True)
    csi_registered = models.CharField(max_length=10, blank=True, null=True)
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)
    admission_type = models.CharField(max_length=50, blank=True, null=True)
    other_admission_details = models.TextField(blank=True, null=True)
    eamcet_rank = models.IntegerField(blank=True, null=True)

    year = models.IntegerField(blank=True, null=True)
    sem = models.IntegerField(blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)

    ssc_marks = models.CharField(max_length=50, blank=True, null=True)
    inter_marks = models.CharField(max_length=50, blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)

    # Project Info
    rtrp_project_title = models.CharField(max_length=500, blank=True, null=True)
    intern_title = models.CharField(max_length=500, blank=True, null=True)
    final_project_title = models.CharField(max_length=500, blank=True, null=True)
    other_training = models.TextField(blank=True, null=True)

    # ================= FILES =================

    # Photo (Image)
    photo = CloudinaryField("image", blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)  # For Cloudinary URL

    # Certificates (Images)
    cert_achieve = CloudinaryField("image", blank=True, null=True)
    cert_intern = CloudinaryField("image", blank=True, null=True)
    cert_courses = CloudinaryField("image", blank=True, null=True)
    cert_sdp = CloudinaryField("image", blank=True, null=True)
    cert_extra = CloudinaryField("image", blank=True, null=True)
    cert_placement = CloudinaryField("image", blank=True, null=True)
    cert_national = CloudinaryField("image", blank=True, null=True)

    # Final Generated PDF URL
    pdf_file = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)  # Alias for pdf_file
    pdf_generated = models.BooleanField(default=False)
    pdf_generation_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} ({self.ht_no})"


# =====================================================
# CERTIFICATE MODEL (FACULTY)
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

    issued_by = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.staff_name}"


# =====================================================
# FACULTY LOG
# =====================================================

class FacultyLog(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    performed_by = models.CharField(max_length=150)
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
    code = models.CharField(max_length=20, blank=True)

    faculty = models.ManyToManyField(
        Faculty,
        related_name='subjects',
        blank=True
    )

    def __str__(self):
        return self.name