from django.contrib import admin
from .models import (
    Department,
    Subject,
    Faculty,
    Student,
    Certificate,
    FacultyLog,
    CloudinaryUpload,
)

# =====================================================
# DEPARTMENT ADMIN
# =====================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


# =====================================================
# SUBJECT ADMIN
# =====================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "department")
    search_fields = ("name",)
    list_filter = ("department",)


# =====================================================
# FACULTY ADMIN
# =====================================================

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "staff_name",
        "department",
        "is_active",
        "created_at",
    )
    search_fields = (
        "employee_code",
        "staff_name",
        "email",
    )
    list_filter = (
        "department",
        "is_active",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


# =====================================================
# STUDENT ADMIN
# =====================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "ht_no",
        "student_name",
        "year",
        "branch",
        "pdf_generated",
        "created_at",
    )
    search_fields = (
        "ht_no",
        "student_name",
        "email",
    )
    list_filter = (
        "year",
        "branch",
        "pdf_generated",
    )
    readonly_fields = (
        "pdf_generated",
        "pdf_generation_time",
        "created_at",
        "updated_at",
    )


# =====================================================
# CERTIFICATE ADMIN
# =====================================================

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "certificate_type",
        "faculty",
        "issue_date",
        "is_verified",
    )
    list_filter = (
        "certificate_type",
        "is_verified",
    )
    search_fields = (
        "certificate_type",
        "issued_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


# =====================================================
# FACULTY LOG ADMIN
# =====================================================

@admin.register(FacultyLog)
class FacultyLogAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "performed_by",
        "created_at",
    )
    search_fields = (
        "action",
        "performed_by",
    )
    readonly_fields = (
        "created_at",
    )


# =====================================================
# CLOUDINARY UPLOAD ADMIN (FIXED)
# =====================================================

@admin.register(CloudinaryUpload)
class CloudinaryUploadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "upload_type",
        "faculty",
        "student",
        "resource_type",
        "uploaded_by",
        "upload_date",
    )
    search_fields = (
        "upload_type",
        "public_id",
        "uploaded_by",
    )
    list_filter = (
        "upload_type",
        "resource_type",
        "upload_date",
    )
    readonly_fields = (
        "id",
        "upload_date",
    )
