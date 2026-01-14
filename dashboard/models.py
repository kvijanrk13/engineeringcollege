from django.db import models
from cloudinary.models import CloudinaryField


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self):
        return self.name


class Syllabus(models.Model):
    department = models.CharField(max_length=100)
    year = models.IntegerField()
    subject = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.department} - {self.subject}"


class StudentRegistration(models.Model):
    # ================= BASIC INFO =================
    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField()
    nationality = models.CharField(max_length=50, default="Indian")
    category = models.CharField(max_length=50)
    religion = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=10)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    aadhar = models.CharField(max_length=20)
    address = models.TextField()

    # TASK Registration Fields
    task_registered = models.CharField(max_length=3, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    task_username = models.CharField(max_length=50, blank=True, null=True)

    # CSI Registration Fields
    csi_registered = models.CharField(max_length=3, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    csi_membership_id = models.CharField(max_length=50, blank=True, null=True)

    parent_phone = models.CharField(max_length=15)
    student_phone = models.CharField(max_length=15)
    email = models.EmailField()
    admission_type = models.CharField(max_length=50)
    other_admission_details = models.TextField(blank=True, null=True)

    # New field: EAMCET/EAPCET Rank
    eamcet_rank = models.IntegerField(null=True, blank=True)

    year = models.IntegerField()
    sem = models.IntegerField()

    # ================= ACADEMIC =================
    ssc_marks = models.FloatField(null=True, blank=True)
    inter_marks = models.FloatField(null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)
    rtrp_title = models.CharField(max_length=200, blank=True)
    intern_title = models.CharField(max_length=200, blank=True)
    final_project_title = models.CharField(max_length=200, blank=True)
    other_training = models.TextField(blank=True, null=True)

    # ================= MEDIA =================
    photo = CloudinaryField("student_photo", blank=True, null=True)

    # 🔥 CERTIFICATES STORED AS PUBLIC URLs
    cert_achieve = models.URLField(blank=True, null=True)
    cert_intern = models.URLField(blank=True, null=True)
    cert_courses = models.URLField(blank=True, null=True)
    cert_sdp = models.URLField(blank=True, null=True)
    cert_extra = models.URLField(blank=True, null=True)
    cert_placement = models.URLField(blank=True, null=True)
    cert_national = models.URLField(blank=True, null=True)

    # ================= GENERATED PDF =================
    pdf_url = models.URLField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def get_pdf_filename(self):
        safe_name = self.student_name.replace(" ", "_")
        return f"student_{self.ht_no}_{safe_name}.pdf"

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"