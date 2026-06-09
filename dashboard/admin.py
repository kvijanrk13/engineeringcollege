from django.contrib import admin
from .models import ProjectDownloadPayment, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'ht_no',
        'student_name',
        'gender',
        'year',
        'sem',
        'student_phone',
        'cgpa',
    )

    list_filter = (
        'gender',
        'year',
        'sem',
    )

    search_fields = (
        'ht_no',
        'student_name',
        'student_phone',
        'email',
    )

    ordering = ('ht_no',)


@admin.register(ProjectDownloadPayment)
class ProjectDownloadPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'merchant_order_id', 'payment_method', 'status', 'domain_slug', 'project_slug', 'amount_paise', 'verified_at',
        'download_count', 'created_at',
    )
    list_filter = ('payment_method', 'status', 'domain_slug', 'project_slug', 'created_at', 'verified_at')
    search_fields = (
        'merchant_order_id', 'phonepe_order_id', 'session_key',
        'receipt_student_name', 'receipt_student_email', 'receipt_student_phone',
    )
    readonly_fields = (
        'merchant_order_id', 'session_key', 'amount_paise',
        'phonepe_order_id', 'payment_url', 'gateway_response',
        'download_count', 'created_at', 'updated_at', 'receipt_uploaded_at',
    )
    fields = (
        'merchant_order_id', 'session_key', 'domain_slug', 'project_slug',
        'amount_paise', 'payment_method', 'status', 'verified_at', 'admin_note',
        'receipt_student_name', 'receipt_student_email', 'receipt_student_phone',
        'receipt_filename', 'receipt_message', 'receipt_uploaded_at',
        'phonepe_order_id', 'payment_url', 'gateway_response',
        'download_count', 'created_at', 'updated_at',
    )
    actions = ('mark_receipts_completed',)

    @admin.action(description='Confirm selected receipt requests and unlock ZIP')
    def mark_receipts_completed(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(payment_method='RECEIPT').update(
            status='COMPLETED',
            verified_at=timezone.now(),
            updated_at=timezone.now(),
        )
        self.message_user(request, f'{updated} receipt request(s) confirmed.')
