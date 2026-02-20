from django.db import models
from cloudinary.models import CloudinaryField


# =====================================================
# FACULTY MODEL (expanded with all fields used in views)
# =====================================================

class Faculty(models.Model):
    # Personal Information
    staff_name = models.CharField(max_length=200, blank=True, null=True)  # used in many places
    name = models.CharField(max_length=200, blank=True, null=True)  # fallback
    employee_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)  # used in some places
    dob = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    jntuh_id = models.CharField(max_length=50, blank=True, null=True)
    aicte_id = models.CharField(max_length=50, blank=True, null=True)

    # Educational Qualifications
    ug_degree = models.CharField(max_length=100, blank=True, null=True)
    ug_year = models.IntegerField(blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)
    ug_college = models.CharField(max_length=200, blank=True, null=True)
    ug_spec = models.CharField(max_length=200, blank=True, null=True)

    pg_degree = models.CharField(max_length=100, blank=True, null=True)
    pg_year = models.IntegerField(blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)
    pg_college = models.CharField(max_length=200, blank=True, null=True)
    pg_spec = models.CharField(max_length=200, blank=True, null=True)

    phd_degree = models.CharField(
        max_length=50,
        choices=[
            ('Completed', 'Completed'),
            ('Pursuing', 'Pursuing'),
            ('Not Applicable', 'Not Applicable'),
        ],
        default='Not Applicable',
        blank=True,
        null=True
    )
    phd_year = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=200, blank=True, null=True)
    phd_spec = models.CharField(max_length=200, blank=True, null=True)

    # School Education (if used)
    ssc_year = models.IntegerField(blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_school = models.CharField(max_length=200, blank=True, null=True)

    inter_year = models.IntegerField(blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_college = models.CharField(max_length=200, blank=True, null=True)

    # Experience
    total_experience = models.CharField(max_length=50, blank=True, null=True)  # stored as string
    exp_anurag = models.CharField(max_length=50, blank=True, null=True)
    exp_other = models.CharField(max_length=50, blank=True, null=True)

    # Subjects, Research, etc.
    subjects_dealt = models.TextField(blank=True, null=True)
    about_yourself = models.TextField(blank=True, null=True)

    # Files and Cloudinary
    photo = models.FileField(upload_to='faculty_photos/', blank=True, null=True)
    pdf_document = models.FileField(upload_to='faculty_pdfs/', blank=True, null=True)
    cloudinary_pdf_url = models.URLField(blank=True, null=True)
    cloudinary_photo_url = models.URLField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.staff_name or self.name or self.employee_code or "Faculty"


# =====================================================
# STUDENT MODEL
# =====================================================

class Student(models.Model):

    # ================= BASIC INFO =================
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
    apaar_id = models.CharField(max_length=30, blank=True, null=True)

    address = models.TextField()
    parent_phone = models.CharField(max_length=15)
    student_phone = models.CharField(max_length=15)
    email = models.EmailField()

    # ================= ACADEMIC =================
    task_registered = models.CharField(max_length=10, blank=True, null=True)
    task_username = models.CharField(max_length=100, blank=True, null=True)
    csi_registered = models.CharField(max_length=10, blank=True, null=True)
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)

    admission_type = models.CharField(max_length=100)
    other_admission_details = models.CharField(max_length=200, blank=True, null=True)
    eamcet_rank = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    sem = models.IntegerField(blank=True, null=True)
    ssc_marks = models.FloatField(blank=True, null=True)
    inter_marks = models.FloatField(blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)

    # ================= PROJECTS =================
    rtrp_project_title = models.CharField(max_length=300, blank=True, null=True)
    intern_title = models.CharField(max_length=300, blank=True, null=True)
    final_project_title = models.CharField(max_length=300, blank=True, null=True)
    other_training = models.TextField(blank=True, null=True)

    # ================= FILES =================

    # Photo → Image type
    photo = CloudinaryField("image", blank=True, null=True)

    # Certificates → RAW type (PDF, Images etc)
    cert_achieve = CloudinaryField("raw", blank=True, null=True)
    cert_intern = CloudinaryField("raw", blank=True, null=True)
    cert_courses = CloudinaryField("raw", blank=True, null=True)
    cert_sdp = CloudinaryField("raw", blank=True, null=True)
    cert_extra = CloudinaryField("raw", blank=True, null=True)
    cert_placement = CloudinaryField("raw", blank=True, null=True)
    cert_national = CloudinaryField("raw", blank=True, null=True)

    # Final Generated PDF
    pdf_file = CloudinaryField("raw", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} ({self.ht_no})"


# =====================================================
# ADDITIONAL MODELS REQUIRED BY VIEWS
# =====================================================

class Certificate(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=100)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    cloudinary_url = models.URLField(blank=True, null=True)
    issued_by = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.staff_name}"


class FacultyLog(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    performed_by = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.created_at}"


class CloudinaryUpload(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True, related_name='cloudinary_uploads')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='cloudinary_uploads')
    upload_type = models.CharField(max_length=50)  # e.g., 'pdf', 'photo', 'certificate'
    cloudinary_url = models.URLField()
    public_id = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50, default='raw')
    uploaded_by = models.CharField(max_length=150)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.upload_type} - {self.public_id}"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    faculty = models.ManyToManyField(Faculty, related_name='subjects', blank=True)

    def __str__(self):
        return self.name