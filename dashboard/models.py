from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# =========================
# STUDENT MODEL
# =========================

class Student(models.Model):
    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=50, default='Indian')
    category = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    student_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    task_registered = models.CharField(max_length=10, blank=True, null=True)
    task_username = models.CharField(max_length=100, blank=True, null=True)
    csi_registered = models.CharField(max_length=10, blank=True, null=True)
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)
    admission_type = models.CharField(max_length=50, blank=True, null=True)
    other_admission_details = models.CharField(max_length=200, blank=True, null=True)
    eamcet_rank = models.IntegerField(blank=True, null=True)

    year = models.IntegerField()
    sem = models.IntegerField()

    ssc_marks = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    inter_marks = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    rtrp_title = models.CharField(max_length=300, blank=True, null=True)
    intern_title = models.CharField(max_length=300, blank=True, null=True)
    final_project_title = models.CharField(max_length=300, blank=True, null=True)
    other_training = models.TextField(blank=True, null=True)

    photo = models.CharField(max_length=255, blank=True, null=True)  # Cloudinary public_id
    pdf_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"

    class Meta:
        ordering = ['-created_at']


# =========================
# FACULTY MODEL
# =========================

class Faculty(models.Model):
    employee_code = models.CharField(max_length=20, unique=True)
    staff_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        blank=True,
        null=True
    )

    dob = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    state = models.CharField(max_length=50, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    sub_caste = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # =========================
    # CLOUDINARY FIELDS (NEW)
    # =========================
    cloudinary_pdf_url = models.URLField(blank=True, null=True)
    cloudinary_photo_url = models.URLField(blank=True, null=True)

    # =========================
    # SSC
    # =========================
    ssc_school = models.CharField(max_length=200, blank=True, null=True)
    ssc_year = models.CharField(max_length=4, blank=True, null=True)
    ssc_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # =========================
    # INTER
    # =========================
    inter_college = models.CharField(max_length=200, blank=True, null=True)
    inter_year = models.CharField(max_length=4, blank=True, null=True)
    inter_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # =========================
    # UG
    # =========================
    ug_college = models.CharField(max_length=200, blank=True, null=True)
    ug_year = models.CharField(max_length=4, blank=True, null=True)
    ug_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ug_spec = models.CharField(max_length=100, blank=True, null=True)

    # =========================
    # PG
    # =========================
    pg_college = models.CharField(max_length=200, blank=True, null=True)
    pg_year = models.CharField(max_length=4, blank=True, null=True)
    pg_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pg_spec = models.CharField(max_length=100, blank=True, null=True)

    # =========================
    # PhD
    # =========================
    phd_university = models.CharField(max_length=200, blank=True, null=True)
    phd_year = models.CharField(max_length=4, blank=True, null=True)
    phd_degree = models.CharField(
        max_length=20,
        choices=[
            ('Completed', 'Completed'),
            ('Pursuing', 'Pursuing'),
            ('Not Started', 'Not Started'),
        ],
        default='Not Started'
    )
    phd_spec = models.CharField(max_length=100, blank=True, null=True)

    subjects_dealt = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['staff_name']

    def __str__(self):
        return f"{self.employee_code} - {self.staff_name}"


# =========================
# CERTIFICATE MODEL
# =========================

class Certificate(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    certificate_type = models.CharField(max_length=100, blank=True, null=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    issued_by = models.CharField(max_length=200, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.employee_code}"


# =========================
# FACULTY LOG MODEL
# =========================

class FacultyLog(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    action = models.CharField(max_length=50)
    details = models.TextField()
    performed_by = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.action} - {self.faculty.employee_code}"


# =========================
# CLOUDINARY UPLOAD MODEL
# =========================

class CloudinaryUpload(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='cloudinary_uploads'
    )

    upload_type = models.CharField(max_length=50)
    cloudinary_url = models.URLField()
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)
    format = models.CharField(max_length=10, blank=True, null=True)
    bytes = models.IntegerField(blank=True, null=True)

    upload_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.upload_type} - {self.faculty.employee_code}"