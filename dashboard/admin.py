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
        'merchant_order_id', 'status', 'amount_paise', 'verified_at',
        'download_count', 'created_at',
    )
    list_filter = ('status', 'created_at', 'verified_at')
    search_fields = ('merchant_order_id', 'phonepe_order_id', 'session_key')
    readonly_fields = (
        'merchant_order_id', 'session_key', 'amount_paise', 'status',
        'phonepe_order_id', 'payment_url', 'gateway_response', 'verified_at',
        'download_count', 'created_at', 'updated_at',
    )
