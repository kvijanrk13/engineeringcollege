from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    # ================= AUTHENTICATION =================
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('logout/', views.logout_view, name='logout'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # ================= HOME / DASHBOARD =================
    path('', views.redirect_to_dashboard, name='redirect'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    # ================= FACULTY =================
    # 🔥 Supports BOTH names (prevents NoReverseMatch)
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    path('faculty/analytics/', views.faculty_analytics, name='faculty_analytics'),
    path('faculty/list/', views.faculty_list, name='faculty_list'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/<int:faculty_id>/edit/', views.edit_faculty, name='edit_faculty'),
    path('faculty/<int:faculty_id>/delete/', views.delete_faculty, name='delete_faculty'),
    path('faculty/<int:faculty_id>/assign-subjects/', views.assign_subjects, name='assign_subjects'),

    # ================= FACULTY PDF =================
    path('faculty/<int:faculty_id>/pdf/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('faculty/<int:faculty_id>/preview-pdf/', views.preview_faculty_pdf, name='preview_faculty_pdf'),
    path('faculty/<int:faculty_id>/download-pdf/', views.download_faculty_pdf, name='download_faculty_pdf'),
    path('faculty/pdf-preview/', views.preview_pdf_template, name='preview_pdf_template'),

    # ================= BULK FACULTY =================
    path('faculty/bulk-generate-pdfs/', views.bulk_generate_faculty_pdfs, name='bulk_generate_faculty_pdfs'),
    path('faculty/bulk-actions/', views.bulk_faculty_actions, name='bulk_faculty_actions'),
    path('faculty/bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('faculty/export-csv/', views.export_faculty_csv, name='export_faculty_csv'),

    # ================= CLOUDINARY =================
    path('faculty/<int:faculty_id>/sync-cloudinary/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('faculty/<int:faculty_id>/upload-cloudinary/', views.upload_faculty_to_cloudinary, name='upload_faculty_to_cloudinary'),
    path('faculty/<int:faculty_id>/get-cloudinary-url/', views.get_cloudinary_url, name='get_cloudinary_url'),
    path('faculty/bulk-sync-cloudinary/', views.bulk_sync_to_cloudinary, name='bulk_sync_to_cloudinary'),
    path('cloudinary/status/', views.cloudinary_status, name='cloudinary_status'),
    path('upload-faculty-photo/', views.upload_faculty_photo, name='upload_faculty_photo'),
    path('upload-faculty-pdf/', views.upload_faculty_pdf, name='upload_faculty_pdf'),

    # ================= CERTIFICATES =================
    path('faculty/<int:faculty_id>/upload-certificate/', views.upload_certificate, name='upload_certificate'),
    path('faculty/<int:faculty_id>/upload-certificates-bulk/', views.upload_certificates_bulk, name='upload_certificates_bulk'),
    path('faculty/<int:faculty_id>/view-certificates/', views.view_certificates, name='view_certificates'),
    path('certificate/<int:certificate_id>/edit/', views.edit_certificate, name='edit_certificate'),
    path('certificate/<int:certificate_id>/delete/', views.delete_certificate, name='delete_certificate'),
    path('faculty/<int:faculty_id>/merge-certificates/', views.merge_certificates, name='merge_certificates'),
    path('faculty/<int:faculty_id>/merge-certificates-with-pdf/', views.merge_certificates_with_pdf, name='merge_certificates_with_pdf'),
    path('faculty/<int:faculty_id>/preview-merged-pdf/', views.preview_merged_pdf, name='preview_merged_pdf'),

    # ================= STUDENTS =================
    path('students/', views.students, name='students'),
    path('students-data/', views.students_data, name='students_data'),
    path('student/add/', views.add_student, name='add_student'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('student/<int:student_id>/generate-pdf/', views.generate_student_pdf_file, name='generate_student_pdf'),
    path('student/<int:student_id>/view-pdf/', views.view_pdf, name='view_pdf'),
    path('student/<int:student_id>/download-pdf/', views.download_pdf, name='download_pdf'),
    path('export-students-csv/', views.export_students_csv, name='export_students_csv'),

    # ================= APIs =================
    path('api/faculty-list/', views.api_faculty_list, name='api_faculty_list'),
    path('api/faculty/<int:faculty_id>/', views.api_faculty_detail, name='api_faculty_detail'),
    path('api/faculty/<int:faculty_id>/update-status/', views.api_update_faculty_status, name='api_update_faculty_status'),
    path('api/student-list/', views.api_student_list, name='api_student_list'),
    path('api/student/<int:student_id>/', views.api_student_detail, name='api_student_detail'),
    path('api/faculty-statistics/<int:faculty_id>/', views.faculty_statistics_api, name='faculty_statistics_api'),
    path('api/quick-stats/', views.quick_stats, name='quick_stats'),

    # ================= CHARTS =================
    path('faculty-charts/', views.faculty_charts, name='faculty_charts'),
    path('student-charts/', views.student_charts, name='student_charts'),

    # ================= SEARCH =================
    path('search/faculty/', views.search_faculty, name='search_faculty'),
    path('search/students/', views.search_students, name='search_students'),

    # ================= SYSTEM =================
    path('system-status/', views.system_status, name='system_status'),
    path('clear-logs/', views.clear_logs, name='clear_logs'),
    path('backup-database/', views.backup_database, name='backup_database'),
    path('recent-activity/', views.recent_activity, name='recent_activity'),
    path('session-info/', views.session_info, name='session_info'),
    path('clear-session/', views.clear_session, name='clear_session'),

    # ================= MAIN APP PAGES =================
    path('app-home/', views.application_home, name='application_home'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('about/', views.about_system, name='about_system'),
    path('help/', views.help_documentation, name='help_documentation'),
    path('contact/', views.contact_support, name='contact_support'),
]