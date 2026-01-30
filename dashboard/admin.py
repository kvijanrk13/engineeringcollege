from django.contrib import admin
from .models import Faculty, Certificate, FacultyLog, CloudinaryUpload


# =========================
# FACULTY ADMIN
# =========================

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        'employee_code',
        'staff_name',
        'department',
        'email',
        'mobile',
        'is_active',
    )

    list_filter = (
        'department',
        'is_active',
        'gender',
    )

    search_fields = (
        'employee_code',
        'staff_name',
        'email',
        'mobile',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('department', 'staff_name')


# =========================
# CERTIFICATE ADMIN
# =========================

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        'faculty',
        'certificate_type',
        'issued_by',
        'issue_date',
        'is_verified',
    )

    list_filter = (
        'certificate_type',
        'is_verified',
        'issue_date',
    )

    search_fields = (
        'faculty__employee_code',
        'faculty__staff_name',
        'certificate_type',
        'issued_by',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = ('-issue_date',)


# =========================
# FACULTY LOG ADMIN
# =========================

@admin.register(FacultyLog)
class FacultyLogAdmin(admin.ModelAdmin):
    list_display = (
        'faculty',
        'action',
        'performed_by',
        'created_at',
    )

    list_filter = (
        'action',
        'performed_by',
        'created_at',
    )

    search_fields = (
        'faculty__employee_code',
        'faculty__staff_name',
        'action',
        'performed_by',
    )

    readonly_fields = (
        'faculty',
        'action',
        'details',
        'performed_by',
        'created_at',
    )

    ordering = ('-created_at',)


# =========================
# CLOUDINARY UPLOAD ADMIN
# =========================

@admin.register(CloudinaryUpload)
class CloudinaryUploadAdmin(admin.ModelAdmin):
    list_display = (
        'faculty',
        'upload_type',
        'resource_type',
        'upload_date',
    )

    list_filter = (
        'upload_type',
        'resource_type',
        'upload_date',
    )

    search_fields = (
        'faculty__employee_code',
        'faculty__staff_name',
        'public_id',
    )

    readonly_fields = (
        'faculty',
        'upload_type',
        'cloudinary_url',
        'public_id',
        'resource_type',
        'format',
        'bytes',
        'upload_date',
    )

    ordering = ('-upload_date',)
