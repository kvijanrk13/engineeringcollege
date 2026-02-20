# faculty/admin.py
from django.contrib import admin
from .models import Faculty, Certificate, FacultyLog, CloudinaryUpload


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'name', 'department', 'joining_date', 'is_active')
    list_filter = ('department', 'is_active', 'gender', 'phd_degree')
    search_fields = ('name', 'employee_code', 'email', 'mobile')
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_code', 'name', 'department', 'joining_date', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'mobile', 'father_name', 'address')
        }),
        ('Personal Details', {
            'fields': ('gender', 'dob', 'state', 'caste', 'sub_caste')
        }),
        ('Official IDs', {
            'fields': ('jntuh_id', 'aicte_id', 'pan', 'aadhar', 'orcid_id', 'apaar_id')
        }),
        ('Educational Qualifications', {
            'fields': (
                'ssc_school', 'ssc_year', 'ssc_percent',
                'inter_college', 'inter_year', 'inter_percent',
                'ug_college', 'ug_year', 'ug_percentage', 'ug_spec',
                'pg_college', 'pg_year', 'pg_percentage', 'pg_spec',
                'phd_university', 'phd_year', 'phd_degree', 'phd_spec'
            )
        }),
        ('Experience & Details', {
            'fields': ('exp_anurag', 'exp_other', 'subjects_dealt', 'about_yourself')
        }),
        ('Files & URLs', {
            'fields': ('photo', 'pdf_document', 'cloudinary_pdf_url', 'cloudinary_photo_url', 'certificates')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    actions = ['activate_faculty', 'deactivate_faculty', 'generate_pdfs', 'upload_to_cloudinary']

    def activate_faculty(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} faculty members activated.')

    def deactivate_faculty(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} faculty members deactivated.')

    def generate_pdfs(self, request, queryset):
        from .utils import generate_faculty_pdf_bytes
        for faculty in queryset:
            try:
                pdf_bytes = generate_faculty_pdf_bytes(faculty)
                if pdf_bytes:
                    # Save or process PDF
                    pass
            except Exception as e:
                self.message_user(request, f'Error generating PDF for {faculty.employee_code}: {str(e)}', level='error')
        self.message_user(request, f'PDF generation initiated for {queryset.count()} faculty members.')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'certificate_type', 'issued_by', 'issue_date', 'is_verified')
    list_filter = ('certificate_type', 'is_verified', 'issue_date')
    search_fields = ('faculty__name', 'certificate_type', 'issued_by')
    date_hierarchy = 'issue_date'


@admin.register(FacultyLog)
class FacultyLogAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'action', 'performed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('faculty__name', 'details', 'performed_by')
    readonly_fields = ('faculty', 'action', 'details', 'performed_by', 'ip_address', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(CloudinaryUpload)
class CloudinaryUploadAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'upload_type', 'public_id', 'upload_date')
    list_filter = ('upload_type', 'upload_date')
    search_fields = ('faculty__name', 'public_id', 'cloudinary_url')
    readonly_fields = ('upload_date', 'raw_response')
    date_hierarchy = 'upload_date'