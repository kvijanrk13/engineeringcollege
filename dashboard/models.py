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
    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)

    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)

    gender = models.CharField(max_length=10)
    dob = models.DateField(null=True, blank=True)
    age = models.IntegerField(default=0)

    nationality = models.CharField(max_length=50, default="Indian")
    category = models.CharField(max_length=50)
    religion = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=10)

    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    aadhar = models.CharField(max_length=20)

    address = models.TextField()

    parent_phone = models.CharField(max_length=15)
    student_phone = models.CharField(max_length=15)
    email = models.EmailField()

    admission_type = models.CharField(max_length=50)
    other_admission_details = models.TextField(blank=True, null=True)

    year = models.IntegerField()
    sem = models.IntegerField()

    ssc_marks = models.FloatField(null=True, blank=True)
    inter_marks = models.FloatField(null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)

    rtrp_title = models.CharField(max_length=255, blank=True)
    intern_title = models.CharField(max_length=255, blank=True)
    final_project_title = models.CharField(max_length=255, blank=True)

    # ✅ CLOUDINARY IMAGE
    photo = CloudinaryField("image", blank=True, null=True)

    # Certificates (optional – can be Cloudinary later)
    cert_achieve = models.FileField(upload_to="certificates/", blank=True, null=True)
    cert_intern = models.FileField(upload_to="certificates/", blank=True, null=True)
    cert_courses = models.FileField(upload_to="certificates/", blank=True, null=True)
    cert_sdp = models.FileField(upload_to="certificates/", blank=True, null=True)
    cert_extra = models.FileField(upload_to="certificates/", blank=True, null=True)
    cert_placement = models.FileField(upload_to="certificates/", blank=True, null=True)
    cert_national = models.FileField(upload_to="certificates/", blank=True, null=True)

    other_training = models.TextField(blank=True, null=True)

    # ✅ CLOUDINARY PDF URL
    pdf_url = models.URLField(blank=True, null=True)

    registration_date = models.DateTimeField(auto_now_add=True)

    def get_pdf_filename(self):
        return f"student_{self.ht_no}_{self.student_name.replace(' ', '_')}.pdf"

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"