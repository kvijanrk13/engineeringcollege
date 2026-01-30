# dashboard/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "dashboard"

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==================== DASHBOARD & HOME ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),

    # ==================== SINGLE PAGE FACULTY DASHBOARD ====================
    # SINGLE PAGE FACULTY DASHBOARD - REPLACED ALL OLD FACULTY PAGES
    path('faculty/', views.faculty_dashboard, name='faculty'),

    # ==================== PDF GENERATION ====================
    path(
        'faculty/<int:faculty_id>/generate-pdf/',
        views.generate_faculty_pdf,
        name='generate_faculty_pdf'
    ),
    path(
        'faculty/<int:faculty_id>/download-pdf/',
        views.download_faculty_pdf,
        name='download_faculty_pdf'
    ),
    path(
        'faculty/<int:faculty_id>/preview-pdf/',
        views.preview_faculty_pdf,
        name='preview_faculty_pdf'
    ),
    path(
        'generate-pdf/',
        views.generate_pdf_with_data,
        name='generate_pdf_with_data'
    ),
    path(
        'preview-pdf-template/',
        views.preview_pdf_template,
        name='preview_pdf_template'
    ),
    path(
        'faculty/<int:faculty_id>/download-merged-pdf/',
        views.download_merged_pdf,
        name='download_merged_pdf'
    ),

    # ==================== CLOUDINARY ====================
    path(
        'faculty/<int:faculty_id>/upload-cloudinary/',
        views.upload_faculty_to_cloudinary,
        name='upload_faculty_to_cloudinary'
    ),
    path('cloudinary/status/', views.cloudinary_status, name='cloudinary_status'),
    path(
        'download/cloudinary/<str:public_id>/',
        views.download_from_cloudinary,
        name='download_from_cloudinary'
    ),
    path(
        'download/code/<str:employee_code>/',
        views.download_faculty_pdf_by_code,
        name='download_faculty_pdf_by_code'
    ),
    path(
        'faculty/<int:faculty_id>/sync-to-cloudinary/',
        views.sync_to_cloudinary,
        name='sync_to_cloudinary'
    ),
    path(
        'faculty/<int:faculty_id>/get-cloudinary-url/',
        views.get_cloudinary_url,
        name='get_cloudinary_url'
    ),
    path(
        'upload-faculty-photo/',
        views.upload_faculty_photo,
        name='upload_faculty_photo'
    ),
    path(
        'upload-faculty-pdf/',
        views.upload_faculty_pdf,
        name='upload_faculty_pdf'
    ),

    # ==================== CERTIFICATES ====================
    path(
        'faculty/<int:faculty_id>/certificates/',
        views.view_certificates,
        name='view_certificates'
    ),
    path(
        'faculty/<int:faculty_id>/certificates/upload/',
        views.upload_certificate,
        name='upload_certificate'
    ),
    path(
        'certificates/bulk-upload/',
        views.upload_certificates_bulk,
        name='upload_certificates_bulk'
    ),
    path(
        'certificates/<int:certificate_id>/delete/',
        views.delete_certificate,
        name='delete_certificate'
    ),
    path(
        'certificates/<int:certificate_id>/edit/',
        views.edit_certificate,
        name='edit_certificate'
    ),
    path(
        'faculty/<int:faculty_id>/merge-certificates/',
        views.merge_certificates,
        name='merge_certificates'
    ),
    path(
        'faculty/<int:faculty_id>/merge-certificates-with-pdf/',
        views.merge_certificates_with_pdf,
        name='merge_certificates_with_pdf'
    ),
    path(
        'faculty/<int:faculty_id>/preview-merged-pdf/',
        views.preview_merged_pdf,
        name='preview_merged_pdf'
    ),

    # ==================== EXAM BRANCH ====================
    path('exambranch/', views.exam_branch, name='exam_branch'),
    path(
        'exambranch/faculty-list/',
        views.exam_branch_faculty_list,
        name='exam_branch_faculty_list'
    ),
    path(
        'exambranch/download-all-pdfs/',
        views.download_all_pdfs,
        name='download_all_pdfs'
    ),
    path(
        'exambranch/report/',
        views.generate_exam_branch_report,
        name='generate_exam_branch_report'
    ),

    # ==================== REPORTS ====================
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path(
        'reports/faculty-summary/',
        views.faculty_summary_report,
        name='faculty_summary_report'
    ),
    path(
        'reports/department-wise/',
        views.department_wise_report,
        name='department_wise_report'
    ),
    path(
        'reports/qualification-wise/',
        views.qualification_wise_report,
        name='qualification_wise_report'
    ),
    path(
        'reports/experience-wise/',
        views.experience_wise_report,
        name='experience_wise_report'
    ),

    # ==================== SETTINGS & UTILITIES ====================
    path('settings/', views.settings_view, name='settings'),
    path('settings/cloudinary/', views.cloudinary_settings, name='cloudinary_settings'),
    path('settings/pdf/', views.pdf_settings, name='pdf_settings'),
    path('backup/', views.backup_data, name='backup_data'),
    path('export/', views.export_faculty_data, name='export_faculty_data'),
    path('export/excel/', views.export_to_excel, name='export_to_excel'),
    path('export/json/', views.export_faculty_json, name='export_faculty_json'),
    path('export/xml/', views.export_faculty_xml, name='export_faculty_xml'),
    path('import/', views.import_faculty_data, name='import_faculty_data'),
    path('restore/', views.restore_data, name='restore_data'),

    # ==================== API ====================
    path('api/faculty/', views.api_faculty_list, name='api_faculty_list'),
    path('api/faculty/<int:faculty_id>/', views.api_faculty_detail, name='api_faculty_detail'),
    path('api/faculty/code/<str:employee_code>/', views.api_faculty_by_code, name='api_faculty_by_code'),
    path('api/generate-pdf/', views.api_generate_pdf, name='api_generate_pdf'),
    path('api/upload-pdf-to-cloudinary/', views.api_upload_pdf_to_cloudinary, name='api_upload_pdf_to_cloudinary'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/stats/', views.api_stats, name='api_stats'),

    # ==================== AJAX ENDPOINTS ====================
    path('ajax/get-faculty-data/', views.ajax_get_faculty_data, name='ajax_get_faculty_data'),
    path('ajax/check-faculty-code/', views.ajax_check_faculty_code, name='ajax_check_faculty_code'),
    path('ajax/search-faculty/', views.ajax_search_faculty, name='ajax_search_faculty'),
    path('ajax/generate-pdf/', views.ajax_generate_pdf, name='ajax_generate_pdf'),
    path('ajax/upload-pdf/', views.ajax_upload_pdf, name='ajax_upload_pdf'),
    path('ajax/check-pdf-status/<int:faculty_id>/', views.ajax_check_pdf_status, name='ajax_check_pdf_status'),
    path('ajax/upload-certificate/', views.ajax_upload_certificate, name='ajax_upload_certificate'),
    path('ajax/merge-certificates/', views.ajax_merge_certificates, name='ajax_merge_certificates'),

    # ==================== HEALTH ====================
    path('health/', views.health_check, name='health_check'),
    path('system/status/', views.system_status, name='system_status'),
    path('logs/', views.view_logs, name='view_logs'),

    # ==================== PROCESSING ROUTES ====================
    # REMOVED: path('process-faculty-pdf/', views.process_faculty_pdf, name='process_faculty_pdf'),


    # ==================== TEMPLATE VIEWS ====================
    path('pdf-template/', views.pdf_template_view, name='pdf_template'),
    path('pdf-template-preview/', views.pdf_template_preview, name='pdf_template_preview'),

    # ==================== ADMIN ====================
    path('admin/bulk-upload/', views.admin_faculty_bulk_upload, name='admin_faculty_bulk_upload'),
    path('admin/cleanup/', views.admin_cleanup_data, name='admin_cleanup_data'),
    path('admin/logs/', views.admin_system_logs, name='admin_system_logs'),
    path('admin/audit-trail/', views.admin_audit_trail, name='admin_audit_trail'),

    # ==================== BATCH PROCESSING ====================
    path('batch/generate-all-pdfs/', views.batch_generate_all_pdfs, name='batch_generate_all_pdfs'),
    path('batch/upload-all-to-cloudinary/', views.batch_upload_all_to_cloudinary,
         name='batch_upload_all_to_cloudinary'),
    path('batch/process-pending/', views.batch_process_pending, name='batch_process_pending'),
    path('batch/actions/', views.faculty_bulk_actions, name='faculty_bulk_actions'),

    # ==================== SEARCH & FILTER ====================
    path('search/', views.search_faculty, name='search_faculty'),
    path('filter/', views.filter_faculty, name='filter_faculty'),
    path('search/advanced/', views.advanced_search, name='advanced_search'),
    path('api/search/advanced/', views.faculty_search_advanced_api, name='faculty_search_advanced_api'),

    # ==================== WEBHOOKS ====================
    path('webhook/cloudinary/', views.cloudinary_webhook, name='cloudinary_webhook'),
    path('webhook/pdf-generation/', views.pdf_generation_webhook, name='pdf_generation_webhook'),
    path('webhook/faculty-api/', views.faculty_api_webhook, name='faculty_api_webhook'),

    # ==================== ANALYTICS ====================
    path('analytics/', views.faculty_analytics, name='faculty_analytics'),

    # ==================== FACILITY FUNCTIONS ====================
    path('faculty/<int:faculty_id>/timeline/', views.faculty_timeline, name='faculty_timeline'),
    path('faculty/comparison/', views.faculty_comparison, name='faculty_comparison'),
    path('faculty/quick-view/', views.faculty_quick_view, name='faculty_quick_view'),
    path('faculty/<int:faculty_id>/export-package/', views.faculty_export_package, name='faculty_export_package'),
    path('faculty/reminders/', views.faculty_reminders, name='faculty_reminders'),
    path('faculty/<int:faculty_id>/qrcode/', views.faculty_qrcode, name='faculty_qrcode'),
    path('faculty/<int:faculty_id>/print/', views.faculty_print_view, name='faculty_print_view'),

    # ==================== STUDENTS ROUTES ====================
    path("students/", views.students, name="students"),
    path("students-data/", views.students_data, name="students_data"),
    path("pdf/view/<int:student_id>/", views.view_pdf, name="view_pdf"),
    path("pdf/download/<int:student_id>/", views.download_pdf, name="download_pdf"),

    # ==================== REDIRECTS ====================
    path('redirect/dashboard/', views.redirect_to_dashboard, name='redirect_to_dashboard'),
]

# ==================== STATIC & MEDIA (DEV ONLY) ====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # ==================== TEST ROUTES (development only) ====================
    urlpatterns += [
        path('test/pdf-generation/', views.test_pdf_generation, name='test_pdf_generation'),
        path('test/cloudinary-upload/', views.test_cloudinary_upload, name='test_cloudinary_upload'),
        path('test/certificate-merge/', views.test_certificate_merge, name='test_certificate_merge'),
    ]