from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# =====================================================
# DEPARTMENT MODEL
# =====================================================

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"


# =====================================================
# SUBJECT MODEL
# =====================================================

class Subject(models.Model):
    name = models.CharField(max_length=150)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


# =====================================================
# FACULTY MODEL (FIXED)
# =====================================================

class Faculty(models.Model):
    employee_code = models.CharField(max_length=20, unique=True)
    staff_name = models.CharField(max_length=100)

    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )

    state = models.CharField(max_length=50, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    sub_caste = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    department = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # ✅ REQUIRED BY DASHBOARD
    phd_degree = models.CharField(
        max_length=20,
        choices=[
            ('Completed', 'Completed'),
            ('Pursuing', 'Pursuing'),
            ('Not Started', 'Not Started'),
            ('None', 'None'),
        ],
        default='Not Started'
    )

    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    pdf_document = models.FileField(upload_to='faculty_pdfs/', blank=True, null=True)

    cloudinary_photo_url = models.URLField(max_length=500, blank=True, null=True)
    cloudinary_pdf_url = models.URLField(max_length=500, blank=True, null=True)
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    pdf_url = models.URLField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_code} - {self.staff_name}"

    class Meta:
        ordering = ["employee_code"]
        verbose_name = "Faculty"
        verbose_name_plural = "Faculty"


# =====================================================
# STUDENT MODEL (TEMPLATE SAFE)
# =====================================================

class Student(models.Model):
    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=200)
    roll_number = models.CharField(max_length=20, blank=True, null=True)

    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        blank=True,
        null=True
    )

    dob = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=50, default="Indian")
    category = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)

    aadhar = models.CharField(max_length=20, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    student_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    admission_type = models.CharField(max_length=50, blank=True, null=True)
    other_admission_details = models.CharField(max_length=200, blank=True, null=True)
    eamcet_rank = models.IntegerField(blank=True, null=True)

    year = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        blank=True,
        null=True
    )
    sem = models.IntegerField(blank=True, null=True)
    branch = models.CharField(max_length=50, blank=True, null=True)

    ssc_marks = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    inter_marks = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    # ---- Academic / Training ----
    csi_registered = models.BooleanField(default=False)
    csi_membership_id = models.CharField(max_length=50, blank=True, null=True)

    final_project_title = models.CharField(max_length=255, blank=True, null=True)
    intern_title = models.CharField(max_length=255, blank=True, null=True)
    rtrp_project_title = models.CharField(max_length=255, blank=True, null=True)  # ✅ FIXED: rttp_title → rtrp_project_title
    other_training = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)

    pdf_generated = models.BooleanField(default=False)
    pdf_generation_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ REQUIRED BY TEMPLATE
    @property
    def full_name(self):
        return self.student_name

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Student"
        verbose_name_plural = "Students"


# =====================================================
# FACULTY LOG MODEL
# =====================================================

class FacultyLog(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="logs",
        blank=True,
        null=True
    )
    action = models.CharField(max_length=100)
    details = models.TextField()
    performed_by = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} - {self.faculty.staff_name if self.faculty else 'System'}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Faculty Log"
        verbose_name_plural = "Faculty Logs"


# =====================================================
# CERTIFICATE MODEL
# =====================================================

class Certificate(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    certificate_type = models.CharField(max_length=100)
    certificate_file = models.FileField(
        upload_to="faculty_certificates/",
        blank=True,
        null=True
    )

    issued_by = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    cloudinary_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.employee_code}"

    class Meta:
        ordering = ["-issue_date"]
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"


# =====================================================
# CLOUDINARY UPLOAD MODEL
# =====================================================

class CloudinaryUpload(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="cloudinary_uploads",
        blank=True,
        null=True
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="cloudinary_uploads",
        blank=True,
        null=True
    )

    upload_type = models.CharField(max_length=50)
    cloudinary_url = models.URLField()
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)

    uploaded_by = models.CharField(max_length=100, blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.student:
            return f"{self.upload_type} - {self.student.ht_no}"
        return self.upload_type

    class Meta:
        ordering = ["-upload_date"]
        verbose_name = "Cloudinary Upload"
        verbose_name_plural = "Cloudinary Uploads"