# dashboard/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main entry point
    path('', views.admin_login, name='index'),

    # Test routes
    path('test/', views.simple_test, name='test'),

    # Health check route
    path('health/', lambda r: HttpResponse(b"OK"), name='health_check'),
    
    # Diagnostic routes
    path('diagnose/weasyprint/', views.diagnose_weasyprint, name='diagnose_weasyprint'),


    # Main dashboard routes
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('mobile-dashboard/', views.mobile_dashboard, name='mobile_dashboard'),
    path('home/', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path(
        'projects/software-engineering/engineeringcollege-project/download/',
        views.download_engineeringcollege_project,
        name='download_engineeringcollege_project',
    ),
    path(
        'projects/software-engineering/engineeringcollege-project/payment/',
        views.project_download_payment,
        name='project_download_payment',
    ),
    path(
        'projects/software-engineering/engineeringcollege-project/payment/start/',
        views.initiate_project_download_payment,
        name='initiate_project_download_payment',
    ),
    path(
        'projects/software-engineering/engineeringcollege-project/payment/return/<str:merchant_order_id>/',
        views.project_payment_return,
        name='project_payment_return',
    ),
    path(
        'payments/phonepe/callback/',
        views.phonepe_payment_callback,
        name='phonepe_payment_callback',
    ),
    path('projects/<slug:domain_slug>/', views.project_domain, name='project_domain'),

    # Authentication routes
    path('login/', views.admin_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    path('google/mobile-complete/', views.google_mobile_complete, name='google_mobile_complete'),
    path('logout/', views.logout_view, name='logout'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('redirect-dashboard/', views.redirect_to_dashboard, name='redirect_to_dashboard'),

    # Dashboard variants
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard_password, name='student_dashboard'),
    path('student-dashboard/view/', views.student_dashboard, name='student_dashboard_view'),

    # Faculty routes (top level)
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('faculty-list/', views.faculty_list, name='faculty-list'),

    # Faculty sub-routes
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/list/', views.faculty_list_password, name='faculty_list'),
    path('faculty/list/view/', views.faculty_list, name='faculty_list_view'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/edit/<int:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('faculty/edit-complete/<int:faculty_id>/', views.edit_faculty_complete, name='edit_faculty_complete'),
    path('faculty/delete/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    path('faculty/save/<int:faculty_id>/', views.save_faculty, name='save_faculty'),
    path('faculty/profile/<int:faculty_id>/', views.faculty_profile_view, name='faculty_profile_view'),
    path('faculty/assign-subjects/<int:faculty_id>/', views.assign_subjects, name='assign_subjects'),
    path('faculty/analytics/', views.faculty_analytics, name='faculty_analytics'),
    path('faculty/charts/', views.faculty_charts, name='faculty_charts'),

    # Faculty PDF routes
    path('faculty/pdf/<int:faculty_id>/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('faculty/generate-pdf/<int:faculty_id>/', views.generate_faculty_pdf, name='generate_faculty_pdf_alt'),

    path('faculty/pdf-view/<int:faculty_id>/', views.faculty_pdf, name='faculty_pdf'),
    path('faculty/pdf-download/<int:faculty_id>/', views.download_faculty_pdf, name='download_faculty_pdf'),
    path('faculty/pdf-preview/<int:faculty_id>/', views.preview_faculty_pdf, name='preview_faculty_pdf'),
    path('faculty/preview-pdf/<int:faculty_id>/', views.preview_faculty_pdf, name='preview_faculty_pdf_alt'),
    path('faculty/pdf-status/<int:faculty_id>/', views.ajax_check_pdf_status, name='ajax_check_pdf_status'),
    path('faculty/bulk-pdfs/', views.bulk_generate_faculty_pdfs, name='bulk_generate_faculty_pdfs'),

    # Faculty delete routes
    path('faculty/research-project/delete/<int:project_id>/', views.delete_research_project,
         name='delete_research_project'),
    path('faculty/research-publication/delete/<int:publication_id>/', views.delete_research_publication,
         name='delete_research_publication'),
    path('faculty/fdp/delete/<int:fdp_id>/', views.delete_fdp, name='delete_fdp'),
    path('faculty/btech-project/delete/<int:project_id>/', views.delete_btech_project, name='delete_btech_project'),

    # Students routes
    path('students/', views.students_data, name='students'),
    path('students-list/', views.students_data, name='students-list'),
    path('students/data/', views.students_data, name='students_data'),
    path('students/data/password/', views.students_data_password, name='students_data_password'),

    path('student-details/', views.students_data, name='student_details'),
    path('add-student/', views.add_student, name='add_student'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('student/delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # Student PDF routes
    path('student/photo/<int:student_id>/', views.student_photo_redirect, name='student_photo_redirect'),
    path('student/pdf/<int:student_id>/', views.generate_student_pdf_view, name='generate_student_pdf'),
    path('student/pdf-view/<int:student_id>/', views.view_pdf, name='view_student_pdf'),
    path('student/pdf-regenerate/<int:student_id>/', views.regenerate_student_pdf, name='regenerate_student_pdf'),
    path('student/merge-certificates/<int:student_id>/', views.merge_student_certificates, name='merge_student_certificates'),
    path('student/charts/', views.student_charts, name='student_charts'),

    # Students export
    path('export-students-excel/', views.export_students_excel, name='export_students_excel'),

    # Certificates routes
    path('certificates/', views.view_certificates, name='certificates'),
    path('certificate/upload/<int:faculty_id>/', views.upload_certificate, name='upload_certificate'),
    path('certificate/bulk-upload/', views.upload_certificates_bulk, name='upload_certificates_bulk'),
    path('certificate/view/<int:faculty_id>/', views.view_certificates, name='view_certificates'),
    path('certificate/edit/<int:certificate_id>/', views.edit_certificate, name='edit_certificate'),
    path('certificate/delete/<int:certificate_id>/', views.delete_certificate, name='delete_certificate'),
    path('certificate/merge/<int:faculty_id>/', views.merge_certificates, name='merge_certificates'),
    path('certificate/merge-with-pdf/<int:faculty_id>/', views.merge_certificates_with_pdf,
         name='merge_certificates_with_pdf'),
    path('certificate/preview-merged/<int:faculty_id>/', views.preview_merged_pdf, name='preview_merged_pdf'),

    # Cloudinary routes
    path('cloudinary/sync/<int:faculty_id>/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('cloudinary/upload/<int:faculty_id>/', views.upload_to_cloudinary, name='upload_to_cloudinary'),
    path('faculty/upload-to-cloudinary/<int:faculty_id>/', views.upload_to_cloudinary, name='upload_to_cloudinary_faculty_alias'),
    path('cloudinary/upload-faculty/', views.upload_faculty_pdf, name='upload_faculty_pdf'),
    path('cloudinary/upload-photo/', views.upload_faculty_photo, name='upload_faculty_photo'),
    path('cloudinary/status/', views.cloudinary_status, name='cloudinary_status'),
    path('cloudinary/url/<int:faculty_id>/', views.get_cloudinary_url, name='get_cloudinary_url'),
    path('cloudinary/bulk-sync/', views.bulk_sync_to_cloudinary, name='bulk_sync_to_cloudinary'),
    path('cloudinary/sync-all-photos/', views.sync_all_faculty_photos_to_cloudinary, name='sync_all_faculty_photos_to_cloudinary'),

    # Bulk operations
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('bulk-faculty-actions/', views.bulk_faculty_actions, name='bulk_faculty_actions'),
    path('bulk-student-actions/', views.bulk_student_actions, name='bulk_student_actions'),
    path('export-faculty-csv/', views.export_faculty_csv, name='export_faculty_csv'),
    path('export-faculty-excel/', views.export_faculty_excel, name='export_faculty_excel'),

    # Search
    path('search/faculty/', views.search_faculty, name='search_faculty'),
    path('search/students/', views.search_students, name='search_students'),

    # API routes
    path('api/faculty/list/', views.api_faculty_list, name='api_faculty_list'),
    path('api/faculty/detail/<int:faculty_id>/', views.api_faculty_detail, name='api_faculty_detail'),
    path('api/faculty/research/<int:faculty_id>/', views.api_faculty_research, name='api_faculty_research'),
    path('api/faculty/fdps/<int:faculty_id>/', views.api_faculty_fdps, name='api_faculty_fdps'),
    path('api/faculty/projects/<int:faculty_id>/', views.api_faculty_projects, name='api_faculty_projects'),
    path('api/faculty/subjects/<int:faculty_id>/', views.api_faculty_subjects, name='api_faculty_subjects'),
    path('api/faculty/assign-subjects/<int:faculty_id>/', views.api_assign_faculty_subjects,
         name='api_assign_faculty_subjects'),
    path('api/faculty/update-status/<int:faculty_id>/', views.api_update_faculty_status,
         name='api_update_faculty_status'),
    path('api/faculty/bulk-update-status/', views.api_bulk_update_faculty_status,
         name='api_bulk_update_faculty_status'),
    path('api/students/list/', views.api_students_list, name='api_students_list'),
    path('api/student/detail/<int:student_id>/', views.api_student_detail, name='api_student_detail'),
    path('api/student/certificates/<int:student_id>/', views.api_student_certificates, name='api_student_certificates'),
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/department/stats/<str:department>/', views.api_department_stats, name='api_department_stats'),
    path('api/quick-stats/', views.quick_stats, name='quick_stats'),
    path('api/faculty-statistics/<int:faculty_id>/', views.faculty_statistics_api, name='faculty_statistics_api'),

    # Stats & System
    path('stats/recent-activity/', views.recent_activity, name='recent_activity'),
    path('stats/system-status/', views.system_status, name='system_status'),
    path('stats/clear-logs/', views.clear_logs, name='clear_logs'),
    path('stats/backup-database/', views.backup_database, name='backup_database'),

    # Exam
    path('exam-branch/', views.exam_branch, name='exam_branch'),
    path('exam-branch/lesson-plan/download/', views.exam_branch_download_lesson_plan, name='exam_branch_download_lesson_plan'),
    path('exam-branch/report/', views.exam_branch_generate_report, name='exam_branch_generate_report'),
    path('exam-branch/batch-download/', views.exam_branch_batch_download, name='exam_branch_batch_download'),
    path('exam-branch/update-attendance/', views.update_attendance, name='update_attendance'),
    path('exam-branch/save-attendance/', views.save_attendance, name='save_attendance'),
    path('exam-branch/attendance-report/', views.attendance_report, name='attendance_report'),
    path('gallery/', views.gallery, name='gallery'),

    # System routes
    path('system/session-info/', views.session_info, name='session_info'),
    path('system/clear-session/', views.clear_session, name='clear_session'),
    path('system/about/', views.about_system, name='about_system'),
    path('system/help/', views.help_documentation, name='help_documentation'),
    path('system/contact/', views.contact_support, name='contact_support'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('system/profile-settings/', views.profile_settings, name='profile_settings'),
    path('system/application-home/', views.application_home, name='application_home'),

    # Debug routes


    # PDF utilities
    path('pdf/generate-with-data/', views.generate_pdf_with_data, name='generate_pdf_with_data'),
    path('pdf/preview-template/', views.preview_pdf_template, name='preview_pdf_template'),

    # Legacy redirects
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard_redirect'),
    path('syllabus/', views.syllabus_view, name='syllabus'),
]
