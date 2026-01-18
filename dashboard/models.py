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

    # TASK Registration Fields - UPDATED to match requirements
    task_registered = models.CharField(max_length=10, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    task_username = models.CharField(max_length=100, blank=True, null=True)

    # CSI Registration Fields - UPDATED to match requirements
    csi_registered = models.CharField(max_length=10, blank=True, null=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    csi_membership_id = models.CharField(max_length=100, blank=True, null=True)

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


# NEW MODEL FOR FACULTY REGISTRATION
class FacultyRegistration(models.Model):
    # ================= BASIC INFORMATION =================
    employee_code = models.CharField(max_length=20, unique=True)
    staff_name = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100)
    date_of_joining = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    # ================= PERSONAL DETAILS =================
    father_name = models.CharField(max_length=100, blank=True, null=True)
    jntuh_id = models.CharField(max_length=50, blank=True, null=True)
    aicte_id = models.CharField(max_length=50, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    sub_caste = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # ================= ACADEMIC DETAILS =================
    admission_type = models.CharField(max_length=50, blank=True, null=True)
    other_admission_details = models.TextField(blank=True, null=True)
    eamcet_rank = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    sem = models.IntegerField(null=True, blank=True)

    # ================= EDUCATIONAL QUALIFICATIONS =================
    ssc_school = models.CharField(max_length=200, blank=True, null=True)
    ssc_year = models.CharField(max_length=10, blank=True, null=True)
    ssc_percent = models.FloatField(blank=True, null=True)
    ssc_marks = models.FloatField(null=True, blank=True)

    inter_college = models.CharField(max_length=200, blank=True, null=True)
    inter_year = models.CharField(max_length=10, blank=True, null=True)
    inter_percent = models.FloatField(blank=True, null=True)
    inter_marks = models.FloatField(null=True, blank=True)

    ug_college = models.CharField(max_length=200, blank=True, null=True)
    ug_year = models.CharField(max_length=10, blank=True, null=True)
    ug_percentage = models.FloatField(blank=True, null=True)
    ug_spec = models.CharField(max_length=100, blank=True, null=True)

    pg_college = models.CharField(max_length=200, blank=True, null=True)
    pg_year = models.CharField(max_length=10, blank=True, null=True)
    pg_percentage = models.FloatField(blank=True, null=True)
    pg_spec = models.CharField(max_length=100, blank=True, null=True)

    phd_university = models.CharField(max_length=200, blank=True, null=True)
    phd_year = models.CharField(max_length=10, blank=True, null=True)
    phd_degree = models.CharField(max_length=50, blank=True, null=True)
    phd_spec = models.CharField(max_length=100, blank=True, null=True)

    # ================= EXPERIENCE =================
    exp_anurag = models.CharField(max_length=50, blank=True, null=True)
    exp_other = models.CharField(max_length=50, blank=True, null=True)

    # ================= SUBJECTS DEALT =================
    subjects_dealt = models.TextField(blank=True, null=True, help_text="Store subjects as comma-separated values")

    # ================= ADDITIONAL ACADEMIC FIELDS =================
    cgpa = models.FloatField(null=True, blank=True)
    rtrp_title = models.CharField(max_length=200, blank=True, null=True)
    intern_title = models.CharField(max_length=200, blank=True, null=True)
    final_project_title = models.CharField(max_length=200, blank=True, null=True)
    other_training = models.TextField(blank=True, null=True)

    # ================= PHOTO =================
    photo = CloudinaryField("faculty_photo", blank=True, null=True)

    # ================= GENERATED PDF =================
    pdf_url = models.URLField(blank=True, null=True)
    pdf_public_id = models.CharField(max_length=255, blank=True, null=True)

    # ================= TIMESTAMPS =================
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ================= ADDITIONAL FIELDS =================
    about_yourself = models.TextField(blank=True, null=True)
    faculty_achievements = models.TextField(blank=True, null=True)
    publications = models.TextField(blank=True, null=True)

    def get_subjects_list(self):
        """Parse subjects_dealt string into a list"""
        if not self.subjects_dealt:
            return []
        return [subject.strip() for subject in self.subjects_dealt.split(',') if subject.strip()]

    def get_photo_url(self):
        """Get the Cloudinary URL for the faculty photo"""
        if self.photo:
            try:
                import cloudinary.utils
                return cloudinary.utils.cloudinary_url(self.photo, secure=True)[0]
            except:
                return None
        return None

    def get_pdf_filename(self):
        safe_name = self.name.replace(" ", "_")
        return f"faculty_{self.employee_code}_{safe_name}.pdf"

    def __str__(self):
        return f"{self.employee_code} - {self.name}"