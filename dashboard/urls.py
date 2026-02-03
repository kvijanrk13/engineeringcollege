# dashboard/urls.py

from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'dashboard'

urlpatterns = [
    # =========================
    # ROOT → DASHBOARD REDIRECT
    # =========================
    path('', lambda request: redirect('dashboard:dashboard'), name='root'),

    # Home & Authentication
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # =========================
    # STUDENT AUTHENTICATION - ADDED LOGOUT PATH
    # =========================
    path('student-login/', views.student_login, name='student_login'),
    path('student-logout/', views.student_logout, name='student_logout'),

    # =========================
    # DASHBOARD
    # =========================
    path('dashboard/', views.dashboard, name='dashboard'),

    # =========================
    # FACULTY MANAGEMENT
    # =========================
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('faculty/<int:faculty_id>/', views.faculty_dashboard, name='faculty_detail'),
    path('generate-faculty-pdf/<int:faculty_id>/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('preview-faculty-pdf/<int:faculty_id>/', views.preview_faculty_pdf, name='preview_faculty_pdf'),
    path('download-faculty-pdf/<int:faculty_id>/', views.download_faculty_pdf, name='download_faculty_pdf'),
    path('download-merged-pdf/<int:faculty_id>/', views.download_merged_pdf, name='download_merged_pdf'),

    # =========================
    # CLOUDINARY
    # =========================
    path('upload-faculty-to-cloudinary/<int:faculty_id>/', views.upload_faculty_to_cloudinary,
         name='upload_faculty_to_cloudinary'),
    path('upload-faculty-photo/', views.upload_faculty_photo, name='upload_faculty_photo'),
    path('upload-faculty-pdf/', views.upload_faculty_pdf, name='upload_faculty_pdf'),
    path('cloudinary-status/', views.cloudinary_status, name='cloudinary_status'),
    path('sync-to-cloudinary/<int:faculty_id>/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('get-cloudinary-url/<int:faculty_id>/', views.get_cloudinary_url, name='get_cloudinary_url'),

    # =========================
    # CERTIFICATES
    # =========================
    path('upload-certificate/<int:faculty_id>/', views.upload_certificate, name='upload_certificate'),
    path('upload-certificates-bulk/', views.upload_certificates_bulk, name='upload_certificates_bulk'),
    path('view-certificates/<int:faculty_id>/', views.view_certificates, name='view_certificates'),
    path('delete-certificate/<int:certificate_id>/', views.delete_certificate, name='delete_certificate'),
    path('edit-certificate/<int:certificate_id>/', views.edit_certificate, name='edit_certificate'),
    path('merge-certificates/<int:faculty_id>/', views.merge_certificates, name='merge_certificates'),
    path('merge-certificates-with-pdf/<int:faculty_id>/', views.merge_certificates_with_pdf,
         name='merge_certificates_with_pdf'),
    path('preview-merged-pdf/<int:faculty_id>/', views.preview_merged_pdf, name='preview_merged_pdf'),

    # =========================
    # EXAM BRANCH
    # =========================
    path('exam-branch/', views.exam_branch, name='exam_branch'),
    path('exam-branch-faculty-list/', views.exam_branch_faculty_list, name='exam_branch_faculty_list'),
    path('download-all-pdfs/', views.download_all_pdfs, name='download_all_pdfs'),
    path('generate-exam-branch-report/', views.generate_exam_branch_report,
         name='generate_exam_branch_report'),

    # =========================
    # REPORTS
    # =========================
    path('reports/', views.reports_dashboard, name='reports_dashboard'),

    # =========================
    # STUDENT MANAGEMENT - UPDATED WITH NEW ROUTES
    # =========================
    path('students/', views.students, name='students'),
    path('students-data/', views.students_data, name='students_data'),
    path('generate-student-pdf/<int:student_id>/', views.generate_student_pdf,
         name='generate_student_pdf'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('view-pdf/<int:student_id>/', views.view_pdf, name='view_pdf'),
    path('download-pdf/<int:student_id>/', views.download_pdf, name='download_pdf'),

    # =========================
    # SETTINGS
    # =========================
    path('settings/', views.settings_view, name='settings'),

    # =========================
    # HEALTH / DEBUG
    # =========================
    path('health-check/', views.health_check, name='health_check'),

    # =========================
    # ADDED NEW FUNCTIONALITIES
    # =========================
    path('faculty-analytics/', views.faculty_analytics, name='faculty_analytics'),
    path('faculty-timeline/<int:faculty_id>/', views.faculty_timeline, name='faculty_timeline'),
    path('faculty-comparison/', views.faculty_comparison, name='faculty_comparison'),
    path('faculty-bulk-actions/', views.faculty_bulk_actions, name='faculty_bulk_actions'),
    path('faculty-quick-view/', views.faculty_quick_view, name='faculty_quick_view'),
    path('faculty-export-package/<int:faculty_id>/', views.faculty_export_package, name='faculty_export_package'),
    path('faculty-reminders/', views.faculty_reminders, name='faculty_reminders'),
    path('faculty-qrcode/<int:faculty_id>/', views.faculty_qrcode, name='faculty_qrcode'),
    path('faculty-print-view/<int:faculty_id>/', views.faculty_print_view, name='faculty_print_view'),
    path('faculty-search-advanced-api/', views.faculty_search_advanced_api, name='faculty_search_advanced_api'),

    # =========================
    # REPORTS & ANALYTICS
    # =========================
    path('reports/faculty-summary/', views.faculty_summary_report, name='faculty_summary_report'),
    path('reports/department-wise/', views.department_wise_report, name='department_wise_report'),
    path('reports/qualification-wise/', views.qualification_wise_report, name='qualification_wise_report'),
    path('reports/experience-wise/', views.experience_wise_report, name='experience_wise_report'),

    # =========================
    # UTILITIES
    # =========================
    path('import-faculty-data/', views.import_faculty_data, name='import_faculty_data'),
    path('export-faculty-data/', views.export_faculty_data, name='export_faculty_data'),
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),
    path('backup-data/', views.backup_data, name='backup_data'),
    path('restore-data/', views.restore_data, name='restore_data'),
    path('settings/cloudinary/', views.cloudinary_settings, name='cloudinary_settings'),
    path('settings/pdf/', views.pdf_settings, name='pdf_settings'),

    # =========================
    # ADMIN SPECIFIC
    # =========================
    path('admin/faculty-bulk-upload/', views.admin_faculty_bulk_upload, name='admin_faculty_bulk_upload'),
    path('admin/cleanup-data/', views.admin_cleanup_data, name='admin_cleanup_data'),
    path('admin/system-logs/', views.admin_system_logs, name='admin_system_logs'),
    path('admin/audit-trail/', views.admin_audit_trail, name='admin_audit_trail'),

    # =========================
    # CUSTOM DOWNLOAD ROUTES
    # =========================
    path('download-faculty-pdf-by-code/<str:employee_code>/', views.download_faculty_pdf_by_code, name='download_faculty_pdf_by_code'),
    path('download-from-cloudinary/<str:public_id>/', views.download_from_cloudinary, name='download_from_cloudinary'),

    # =========================
    # SYSTEM MONITORING
    # =========================
    path('system-status/', views.system_status, name='system_status'),
    path('view-logs/', views.view_logs, name='view_logs'),

    # =========================
    # WEBHOOKS
    # =========================
    path('webhooks/cloudinary/', views.cloudinary_webhook, name='cloudinary_webhook'),
    path('webhooks/pdf-generation/', views.pdf_generation_webhook, name='pdf_generation_webhook'),
    path('webhooks/faculty-api/', views.faculty_api_webhook, name='faculty_api_webhook'),

    # =========================
    # BATCH PROCESSING
    # =========================
    path('batch/generate-all-pdfs/', views.batch_generate_all_pdfs, name='batch_generate_all_pdfs'),
    path('batch/upload-all-to-cloudinary/', views.batch_upload_all_to_cloudinary, name='batch_upload_all_to_cloudinary'),
    path('batch/process-pending/', views.batch_process_pending, name='batch_process_pending'),

    # =========================
    # EXPORT FORMATS
    # =========================
    path('export/faculty-csv/', views.export_faculty_csv, name='export_faculty_csv'),
    path('export/faculty-json/', views.export_faculty_json, name='export_faculty_json'),
    path('export/faculty-xml/', views.export_faculty_xml, name='export_faculty_xml'),
    path('export/faculty-pdf-bundle/', views.export_faculty_pdf_bundle, name='export_faculty_pdf_bundle'),

    # =========================
    # SEARCH & FILTER
    # =========================
    path('search/faculty/', views.search_faculty, name='search_faculty'),
    path('filter/faculty/', views.filter_faculty, name='filter_faculty'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),

    # =========================
    # API ENDPOINTS
    # =========================
    path('api/faculty-list/', views.api_faculty_list, name='api_faculty_list'),
    path('api/faculty-detail/<int:faculty_id>/', views.api_faculty_detail, name='api_faculty_detail'),
    path('api/faculty-by-code/<str:employee_code>/', views.api_faculty_by_code, name='api_faculty_by_code'),
    path('api/generate-pdf/', views.api_generate_pdf, name='api_generate_pdf'),
    path('api/upload-pdf-to-cloudinary/', views.api_upload_pdf_to_cloudinary, name='api_upload_pdf_to_cloudinary'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('ajax/get-faculty-data/', views.ajax_get_faculty_data, name='ajax_get_faculty_data'),
    path('ajax/check-faculty-code/', views.ajax_check_faculty_code, name='ajax_check_faculty_code'),
    path('ajax/search-faculty/', views.ajax_search_faculty, name='ajax_search_faculty'),
    path('ajax/generate-pdf/', views.ajax_generate_pdf, name='ajax_generate_pdf'),
    path('ajax/upload-pdf/', views.ajax_upload_pdf, name='ajax_upload_pdf'),
    path('ajax/check-pdf-status/<int:faculty_id>/', views.ajax_check_pdf_status, name='ajax_check_pdf_status'),
    path('ajax/upload-certificate/', views.ajax_upload_certificate, name='ajax_upload_certificate'),
    path('ajax/merge-certificates/', views.ajax_merge_certificates, name='ajax_merge_certificates'),

    # =========================
    # TEMPLATE VIEWS
    # =========================
    path('pdf-template/', views.pdf_template_view, name='pdf_template'),
    path('pdf-template-preview/', views.pdf_template_preview, name='pdf_template_preview'),
    path('generate-pdf-with-data/', views.generate_pdf_with_data, name='generate_pdf_with_data'),

    # =========================
    # ERROR PAGES
    # =========================
    path('404/', views.error_404, name='custom_404'),
    path('500/', views.error_500, name='custom_500'),
]

# Custom error handlers
handler404 = 'dashboard.views.custom_404'
handler500 = 'dashboard.views.custom_500'
handler403 = 'dashboard.views.custom_403'
handler400 = 'dashboard.views.custom_400'