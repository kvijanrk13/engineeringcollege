# faculty/dashboard/urls.py
from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

app_name = 'faculty'

urlpatterns = [
    # ==================== HOME & AUTHENTICATION ====================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==================== DASHBOARD ====================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ==================== FACULTY MANAGEMENT ====================
    # Faculty list and details
    path('faculty/', views.faculty_list, name='faculty_list'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    path('faculty/<int:faculty_id>/edit/', views.edit_faculty, name='edit_faculty'),
    path('faculty/<int:faculty_id>/delete/', views.delete_faculty, name='delete_faculty'),

    # Faculty data processing
    path('save-faculty-details/', views.save_faculty_details, name='save_faculty_details'),
    path('process-faculty-pdf/', views.process_faculty_pdf, name='process_faculty_pdf'),

    # ==================== PDF GENERATION & HANDLING ====================
    # PDF Generation
    path('generate-faculty-pdf/<int:faculty_id>/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('generate-pdf-with-data/', views.generate_pdf_with_data, name='generate_pdf_with_data'),

    # PDF Preview
    path('preview-faculty-pdf/<int:faculty_id>/', views.preview_faculty_pdf, name='preview_faculty_pdf'),
    path('preview-pdf-template/', views.preview_pdf_template, name='preview_pdf_template'),

    # PDF Download
    path('download-faculty-pdf/<int:faculty_id>/', views.download_faculty_pdf, name='download_faculty_pdf'),
    path('download-merged-pdf/<int:faculty_id>/', views.download_merged_pdf, name='download_merged_pdf'),

    # ==================== CLOUDINARY INTEGRATION ====================
    # Upload to Cloudinary
    path('upload-faculty-to-cloudinary/<int:faculty_id>/', views.upload_faculty_to_cloudinary,
         name='upload_faculty_to_cloudinary'),
    path('upload-faculty-photo/', views.upload_faculty_photo, name='upload_faculty_photo'),
    path('upload-faculty-pdf/', views.upload_faculty_pdf, name='upload_faculty_pdf'),

    # Cloudinary Management
    path('cloudinary-status/', views.cloudinary_status, name='cloudinary_status'),
    path('sync-to-cloudinary/<int:faculty_id>/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('get-cloudinary-url/<int:faculty_id>/', views.get_cloudinary_url, name='get_cloudinary_url'),

    # ==================== CERTIFICATE MANAGEMENT ====================
    # Certificate Upload
    path('upload-certificate/<int:faculty_id>/', views.upload_certificate, name='upload_certificate'),
    path('upload-certificates-bulk/', views.upload_certificates_bulk, name='upload_certificates_bulk'),

    # Certificate Management
    path('certificates/<int:faculty_id>/', views.view_certificates, name='view_certificates'),
    path('certificate/<int:certificate_id>/delete/', views.delete_certificate, name='delete_certificate'),
    path('certificate/<int:certificate_id>/edit/', views.edit_certificate, name='edit_certificate'),

    # Certificate Merging
    path('merge-certificates/<int:faculty_id>/', views.merge_certificates, name='merge_certificates'),
    path('merge-certificates-with-pdf/<int:faculty_id>/', views.merge_certificates_with_pdf,
         name='merge_certificates_with_pdf'),
    path('preview-merged-pdf/<int:faculty_id>/', views.preview_merged_pdf, name='preview_merged_pdf'),

    # ==================== EXAM BRANCH ====================
    # Original pattern without hyphen
    path('exambranch/', views.exam_branch, name='exam_branch'),
    # Add hyphenated version for compatibility
    path('exam-branch/', views.exam_branch, name='exam_branch_hyphen'),
    path('exambranch/faculty-list/', views.exam_branch_faculty_list, name='exam_branch_faculty_list'),
    path('exambranch/download-all-pdfs/', views.download_all_pdfs, name='download_all_pdfs'),
    path('exambranch/generate-report/', views.generate_exam_branch_report, name='generate_exam_branch_report'),

    # ==================== REPORTS & ANALYTICS ====================
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/faculty-summary/', views.faculty_summary_report, name='faculty_summary_report'),
    path('reports/department-wise/', views.department_wise_report, name='department_wise_report'),
    path('reports/qualification-wise/', views.qualification_wise_report, name='qualification_wise_report'),
    path('reports/experience-wise/', views.experience_wise_report, name='experience_wise_report'),

    # ==================== API ENDPOINTS ====================
    # Faculty API
    path('api/faculty/', views.api_faculty_list, name='api_faculty_list'),
    path('api/faculty/<int:faculty_id>/', views.api_faculty_detail, name='api_faculty_detail'),
    path('api/faculty/<str:employee_code>/', views.api_faculty_by_code, name='api_faculty_by_code'),

    # PDF Generation API
    path('api/generate-pdf/', views.api_generate_pdf, name='api_generate_pdf'),
    path('api/upload-pdf-to-cloudinary/', views.api_upload_pdf_to_cloudinary, name='api_upload_pdf_to_cloudinary'),

    # Status API
    path('api/status/', views.api_status, name='api_status'),
    path('api/stats/', views.api_stats, name='api_stats'),

    # ==================== UTILITY ROUTES ====================
    # Data Import/Export
    path('import-faculty-data/', views.import_faculty_data, name='import_faculty_data'),
    path('export-faculty-data/', views.export_faculty_data, name='export_faculty_data'),
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),

    # Backup & Restore
    path('backup-data/', views.backup_data, name='backup_data'),
    path('restore-data/', views.restore_data, name='restore_data'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('settings/cloudinary/', views.cloudinary_settings, name='cloudinary_settings'),
    path('settings/pdf/', views.pdf_settings, name='pdf_settings'),

    # ==================== AJAX ENDPOINTS ====================
    # Faculty Data
    path('ajax/get-faculty-data/', views.ajax_get_faculty_data, name='ajax_get_faculty_data'),
    path('ajax/check-faculty-code/', views.ajax_check_faculty_code, name='ajax_check_faculty_code'),
    path('ajax/search-faculty/', views.ajax_search_faculty, name='ajax_search_faculty'),

    # PDF Operations
    path('ajax/generate-pdf-ajax/', views.ajax_generate_pdf, name='ajax_generate_pdf'),
    path('ajax/upload-pdf-ajax/', views.ajax_upload_pdf, name='ajax_upload_pdf'),
    path('ajax/check-pdf-status/<int:faculty_id>/', views.ajax_check_pdf_status, name='ajax_check_pdf_status'),

    # Certificate Operations
    path('ajax/upload-certificate-ajax/', views.ajax_upload_certificate, name='ajax_upload_certificate'),
    path('ajax/merge-certificates-ajax/', views.ajax_merge_certificates, name='ajax_merge_certificates'),

    # ==================== TEMPLATE VIEWS ====================
    # Documentation
    path('help/', TemplateView.as_view(template_name='faculty/help.html'), name='help'),
    path('guide/', TemplateView.as_view(template_name='faculty/guide.html'), name='guide'),
    path('faq/', TemplateView.as_view(template_name='faculty/faq.html'), name='faq'),

    # PDF Templates
    path('pdf-template/', views.pdf_template_view, name='pdf_template'),
    path('pdf-template-preview/', views.pdf_template_preview, name='pdf_template_preview'),

    # ==================== ERROR PAGES ====================
    path('error/404/', views.error_404, name='error_404'),
    path('error/500/', views.error_500, name='error_500'),

    # ==================== ADMIN SPECIFIC ====================
    path('admin/faculty-bulk-upload/', views.admin_faculty_bulk_upload, name='admin_faculty_bulk_upload'),
    path('admin/cleanup-data/', views.admin_cleanup_data, name='admin_cleanup_data'),
    path('admin/system-logs/', views.admin_system_logs, name='admin_system_logs'),
    path('admin/audit-trail/', views.admin_audit_trail, name='admin_audit_trail'),

    # ==================== CUSTOM DOWNLOAD ROUTES ====================
    # Direct download from Cloudinary with tracking
    re_path(r'^download/(?P<employee_code>[A-Za-z0-9]+)/$', views.download_faculty_pdf_by_code,
            name='download_faculty_pdf_by_code'),
    re_path(r'^download/cloudinary/(?P<public_id>[A-Za-z0-9_/-]+)/$', views.download_from_cloudinary,
            name='download_from_cloudinary'),

    # ==================== HEALTH & MONITORING ====================
    path('health/', views.health_check, name='health_check'),
    path('status/', views.system_status, name='system_status'),
    path('logs/', views.view_logs, name='view_logs'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==================== WEBHOOKS ====================
urlpatterns += [
    path('webhook/cloudinary/', views.cloudinary_webhook, name='cloudinary_webhook'),
    path('webhook/pdf-generation/', views.pdf_generation_webhook, name='pdf_generation_webhook'),
]

# ==================== BATCH PROCESSING ====================
urlpatterns += [
    path('batch/generate-all-pdfs/', views.batch_generate_all_pdfs, name='batch_generate_all_pdfs'),
    path('batch/upload-all-to-cloudinary/', views.batch_upload_all_to_cloudinary,
         name='batch_upload_all_to_cloudinary'),
    path('batch/process-pending/', views.batch_process_pending, name='batch_process_pending'),
]

# ==================== EXPORT FORMATS ====================
urlpatterns += [
    path('export/faculty-csv/', views.export_faculty_csv, name='export_faculty_csv'),
    path('export/faculty-json/', views.export_faculty_json, name='export_faculty_json'),
    path('export/faculty-xml/', views.export_faculty_xml, name='export_faculty_xml'),
    path('export/faculty-pdf-bundle/', views.export_faculty_pdf_bundle, name='export_faculty_pdf_bundle'),
]

# ==================== SEARCH & FILTER ====================
urlpatterns += [
    path('search/', views.search_faculty, name='search_faculty'),
    path('filter/', views.filter_faculty, name='filter_faculty'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
]

# ==================== REDIRECTS (if needed) ====================
urlpatterns += [
    # Redirect old URLs to new ones
    path('old-dashboard/', views.redirect_to_dashboard, name='redirect_to_dashboard'),
    # Redirect hyphenated exam branch to non-hyphenated version
    path('exam-branch/download-all-pdfs/', RedirectView.as_view(pattern_name='download_all_pdfs', permanent=True)),
    path('exam-branch/generate-report/', RedirectView.as_view(pattern_name='generate_exam_branch_report', permanent=True)),
]

# ==================== TESTING ROUTES (development only) ====================
if settings.DEBUG:
    urlpatterns += [
        path('test/pdf-generation/', views.test_pdf_generation, name='test_pdf_generation'),
        path('test/cloudinary-upload/', views.test_cloudinary_upload, name='test_cloudinary_upload'),
        path('test/certificate-merge/', views.test_certificate_merge, name='test_certificate_merge'),
    ]