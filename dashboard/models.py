from django.db import models


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
    # Personal Information
    ht_no = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    dob = models.DateField()
    age = models.IntegerField()
    nationality = models.CharField(max_length=50, default='Indian')
    category = models.CharField(max_length=20)
    religion = models.CharField(max_length=50, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    aadhar = models.CharField(max_length=20)
    address = models.TextField()

    # Contact & Academic
    parent_phone = models.CharField(max_length=15)
    student_phone = models.CharField(max_length=15)
    email = models.EmailField()
    admission_type = models.CharField(max_length=50)
    other_admission_details = models.CharField(max_length=100, blank=True)
    year = models.IntegerField()
    sem = models.IntegerField()

    # Academic Performance
    ssc_marks = models.FloatField(null=True, blank=True)
    inter_marks = models.FloatField(null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)
    rtrp_title = models.CharField(max_length=200, blank=True)
    intern_title = models.CharField(max_length=200, blank=True)
    final_project_title = models.CharField(max_length=200, blank=True)

    # File uploads
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    cert_achieve = models.FileField(upload_to='certificates/achievements/', blank=True, null=True)
    cert_intern = models.FileField(upload_to='certificates/internships/', blank=True, null=True)
    cert_courses = models.FileField(upload_to='certificates/courses/', blank=True, null=True)
    cert_sdp = models.FileField(upload_to='certificates/sdp/', blank=True, null=True)
    cert_extra = models.FileField(upload_to='certificates/extracurricular/', blank=True, null=True)
    cert_placement = models.FileField(upload_to='certificates/placements/', blank=True, null=True)
    cert_national = models.FileField(upload_to='certificates/national_exams/', blank=True, null=True)
    other_training = models.TextField(blank=True)

    # PDF Storage
    pdf_file = models.FileField(upload_to='student_pdfs/', blank=True, null=True)

    # Metadata
    registration_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.ht_no} - {self.student_name}"

    def get_pdf_filename(self):
        """Generate PDF filename based on HT No"""
        return f"student_{self.ht_no}_{self.student_name.replace(' ', '_')}.pdf"