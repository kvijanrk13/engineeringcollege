from django.conf import settings
from django.contrib import admin
from django.core.mail import EmailMessage
from django.utils import timezone
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
        'delivered_at', 'download_count', 'created_at',
    )
    list_filter = ('payment_method', 'status', 'domain_slug', 'project_slug', 'created_at', 'verified_at', 'delivered_at')
    search_fields = (
        'merchant_order_id', 'phonepe_order_id', 'session_key',
        'receipt_student_name', 'receipt_student_email', 'receipt_student_phone',
    )
    readonly_fields = (
        'merchant_order_id', 'session_key', 'amount_paise',
        'phonepe_order_id', 'payment_url', 'gateway_response',
        'download_count', 'created_at', 'updated_at', 'receipt_uploaded_at', 'delivered_at',
    )
    fields = (
        'merchant_order_id', 'session_key', 'domain_slug', 'project_slug',
        'amount_paise', 'payment_method', 'status', 'verified_at', 'admin_note',
        'receipt_student_name', 'receipt_student_email', 'receipt_student_phone',
        'receipt_filename', 'receipt_message', 'receipt_uploaded_at',
        'delivery_drive_link', 'delivered_at',
        'phonepe_order_id', 'payment_url', 'gateway_response',
        'download_count', 'created_at', 'updated_at',
    )
    actions = ('mark_receipts_completed', 'send_drive_links_to_students')

    @admin.action(description='Confirm selected receipt requests and unlock ZIP')
    def mark_receipts_completed(self, request, queryset):
        updated = queryset.filter(payment_method='RECEIPT').update(
            status='COMPLETED',
            verified_at=timezone.now(),
            updated_at=timezone.now(),
        )
        self.message_user(request, f'{updated} receipt request(s) confirmed.')

    @admin.action(description='Email Google Drive project folder links to students')
    def send_drive_links_to_students(self, request, queryset):
        sent = 0
        skipped = 0
        for payment in queryset.filter(payment_method='RECEIPT', status='COMPLETED'):
            if not payment.receipt_student_email or not payment.delivery_drive_link:
                skipped += 1
                continue
            message = EmailMessage(
                subject='Your project folder download link',
                body=(
                    f"Dear {payment.receipt_student_name or 'Student'},\n\n"
                    "Your payment acknowledgement has been verified.\n"
                    "Use the Google Drive link below to access the complete project folder:\n\n"
                    f"{payment.delivery_drive_link}\n\n"
                    f"Request ID: {payment.merchant_order_id}\n\n"
                    "For execution doubts, reply to this email or contact ecprj2026@gmail.com.\n\n"
                    "Regards,\nEngineering College Projects"
                ),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                to=[payment.receipt_student_email],
            )
            try:
                message.send(fail_silently=False)
            except Exception:
                skipped += 1
                continue
            payment.delivered_at = timezone.now()
            payment.save(update_fields=['delivered_at', 'updated_at'])
            sent += 1
        self.message_user(request, f'{sent} Drive link email(s) sent. {skipped} skipped.')
