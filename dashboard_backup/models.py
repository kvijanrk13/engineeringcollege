# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import os


class Faculty(models.Model):
    # Basic Information
    employee_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    joining_date = models.DateField()

    # Contact Information
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    father_name = models.CharField(max_length=100, blank=True, null=True)

    # Official IDs
    jntuh_id = models.CharField(max_length=50, blank=True, null=True)
    aicte_id = models.CharField(max_length=50, blank=True, null=True)
    pan = models.CharField(max_length=20, blank=True, null=True)
    aadhar = models.CharField(max_length=20, blank=True, null=True)
    orcid_id = models.CharField(max_length=50, blank=True, null=True)
    apaar_id = models.CharField(max_length=50, blank=True, null=True)

    # Personal Details
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()
    state = models.CharField(max_length=50)
    caste = models.CharField(max_length=50, blank=True, null=True)
    sub_caste = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Educational Qualifications - SSC
    ssc_school = models.CharField(max_length=200)
    ssc_year = models.CharField(max_length=4)
    ssc_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Educational Qualifications - Intermediate
    inter_college = models.CharField(max_length=200)
    inter_year = models.CharField(max_length=4)
    inter_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Educational Qualifications - UG
    ug_college = models.CharField(max_length=200)
    ug_year = models.CharField(max_length=4)
    ug_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ug_spec = models.CharField(max_length=100)

    # Educational Qualifications - PG
    pg_college = models.CharField(max_length=200)
    pg_year = models.CharField(max_length=4)
    pg_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pg_spec = models.CharField(max_length=100)

    # Educational Qualifications - PhD
    phd_university = models.CharField(max_length=200, blank=True, null=True)
    phd_year = models.CharField(max_length=4, blank=True, null=True)
    PHD_STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pursuing', 'Pursuing'),
        ('Not Started', 'Not Started'),
    ]
    phd_degree = models.CharField(
        max_length=20,
        choices=PHD_STATUS_CHOICES,
        default='Not Started'
    )
    phd_spec = models.CharField(max_length=100, blank=True, null=True)

    # Experience
    exp_anurag = models.CharField(max_length=20, blank=True, null=True)
    exp_other = models.CharField(max_length=20, blank=True, null=True)

    # Subjects and About
    subjects_dealt = models.TextField(blank=True, null=True)
    about_yourself = models.TextField(blank=True, null=True)

    # File Storage Fields
    photo = models.ImageField(
        upload_to='faculty_photos/',
        blank=True,
        null=True
    )

    # Local PDF Storage (if needed)
    pdf_document = models.FileField(
        upload_to='faculty_pdfs/',
        blank=True,
        null=True
    )

    # Cloudinary URLs
    cloudinary_pdf_url = models.URLField(max_length=500, blank=True, null=True)
    cloudinary_photo_url = models.URLField(max_length=500, blank=True, null=True)

    # Certificate Storage (for merging)
    certificates = models.FileField(
        upload_to='faculty_certificates/',
        blank=True,
        null=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ['name']
        indexes = [
            models.Index(fields=['employee_code']),
            models.Index(fields=['department']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.employee_code} - {self.name}"

    def full_name(self):
        """Return full name in proper format"""
        return self.name.title()

    def get_display_name(self):
        """Return name with title"""
        title = "Dr." if self.phd_degree == "Completed" else "Mr./Ms."
        return f"{title} {self.name}"

    def get_experience_years(self):
        """Calculate total experience in years"""
        try:
            from datetime import date
            if self.joining_date:
                delta = date.today() - self.joining_date
                years = delta.days // 365
                months = (delta.days % 365) // 30
                return f"{years} years {months} months"
        except:
            pass
        return self.exp_anurag or "0 years"

    def get_subjects_list(self):
        """Return subjects as list"""
        if self.subjects_dealt:
            return [s.strip() for s in self.subjects_dealt.split(',')]
        return []

    def has_cloudinary_pdf(self):
        """Check if PDF is available on Cloudinary"""
        return bool(self.cloudinary_pdf_url)

    def get_pdf_filename(self):
        """Generate PDF filename"""
        return f"faculty_{self.employee_code}.pdf"

    def get_photo_filename(self):
        """Generate photo filename"""
        if self.photo:
            return os.path.basename(self.photo.name)
        return f"faculty_{self.employee_code}.jpg"

    def save(self, *args, **kwargs):
        # Ensure email is lowercase
        if self.email:
            self.email = self.email.lower()

        # Ensure employee code is uppercase
        if self.employee_code:
            self.employee_code = self.employee_code.upper()

        # Call the parent save method
        super().save(*args, **kwargs)


class Certificate(models.Model):
    """Model for storing faculty certificates separately"""
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='faculty_certificates'
    )
    certificate_type = models.CharField(max_length=100)
    certificate_file = models.FileField(upload_to='certificates/')
    issued_by = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)

    # Cloudinary URL for certificate
    cloudinary_url = models.URLField(max_length=500, blank=True, null=True)

    # Additional details
    description = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.certificate_type} - {self.faculty.name}"

    def is_valid(self):
        """Check if certificate is still valid"""
        from datetime import date
        if self.expiry_date:
            return date.today() <= self.expiry_date
        return True


class FacultyLog(models.Model):
    """Model for tracking faculty data changes"""
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50)  # Created, Updated, Deleted, PDF Generated, etc.
    details = models.TextField()
    performed_by = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.faculty.employee_code} at {self.created_at}"


class CloudinaryUpload(models.Model):
    """Model for tracking Cloudinary uploads"""
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='cloudinary_uploads'
    )
    upload_type = models.CharField(max_length=50)  # pdf, photo, certificate
    cloudinary_url = models.URLField()
    public_id = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50)
    format = models.CharField(max_length=10)
    bytes = models.IntegerField()

    # Response from Cloudinary
    raw_response = models.JSONField(blank=True, null=True)

    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.upload_type} - {self.faculty.employee_code}"


# Signals for automatic logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import json


@receiver(pre_save, sender=Faculty)
def faculty_pre_save(sender, instance, **kwargs):
    """Track changes before saving"""
    if instance.pk:
        try:
            old_instance = Faculty.objects.get(pk=instance.pk)
            changes = {}

            # Compare fields and track changes
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)

                if old_value != new_value and field_name not in ['updated_at']:
                    changes[field_name] = {
                        'old': str(old_value),
                        'new': str(new_value)
                    }

            # Store changes in instance for post_save
            instance._changes = changes
        except Faculty.DoesNotExist:
            pass


@receiver(post_save, sender=Faculty)
def faculty_post_save(sender, instance, created, **kwargs):
    """Log faculty changes after saving"""
    from django.contrib.auth.models import User
    from django.contrib.admin.models import LogEntry

    action = 'Created' if created else 'Updated'
    details = f"Faculty {action}"

    if hasattr(instance, '_changes') and instance._changes:
        details = f"Faculty Updated. Changes: {json.dumps(instance._changes, indent=2)}"

    # Create log entry
    FacultyLog.objects.create(
        faculty=instance,
        action=action,
        details=details,
        performed_by='System'  # Can be updated to track actual user
    )


# Utility functions for the model
def get_faculty_by_code(employee_code):
    """Helper function to get faculty by employee code"""
    try:
        return Faculty.objects.get(employee_code=employee_code)
    except Faculty.DoesNotExist:
        return None


def get_all_active_faculty():
    """Get all active faculty members"""
    return Faculty.objects.filter(is_active=True)


def search_faculty(query):
    """Search faculty by name, department, or employee code"""
    return Faculty.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(department__icontains=query) |
        models.Q(employee_code__icontains=query)
    )


def get_faculty_by_department(department_name):
    """Get all faculty in a specific department"""
    return Faculty.objects.filter(
        department__iexact=department_name,
        is_active=True
    ).order_by('name')


def get_faculty_stats():
    """Get statistics about faculty"""
    from django.db.models import Count

    stats = {
        'total': Faculty.objects.count(),
        'active': Faculty.objects.filter(is_active=True).count(),
        'by_department': Faculty.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count'),
        'with_phd': Faculty.objects.filter(phd_degree='Completed').count(),
        'with_cloudinary_pdf': Faculty.objects.filter(
            cloudinary_pdf_url__isnull=False
        ).count(),
    }

    return stats