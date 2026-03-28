# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ==================== Home & Dashboard ====================
    path('', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('redirect/', views.redirect_to_dashboard, name='redirect_to_dashboard'),

    # ==================== Authentication ====================
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('student-logout/', views.student_logout, name='student_logout'),

    # ==================== Student Management ====================
    path('students/', views.students, name='students'),
    path('students-data/', views.students_data, name='students_data'),
    path('add-student/', views.add_student, name='add_student'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('student/<int:student_id>/pdf/', views.generate_student_pdf_file, name='generate_student_pdf'),
    path('student/<int:student_id>/view-pdf/', views.view_pdf, name='view_pdf'),
    path('student/<int:student_id>/download-pdf/', views.download_pdf, name='download_pdf'),
    path('student/<int:student_id>/regenerate-pdf/', views.regenerate_student_pdf, name='regenerate_student_pdf'),

    # ==================== Faculty Management ====================
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('faculty/list/', views.faculty_list, name='faculty_list'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/<int:faculty_id>/', views.faculty_dashboard, name='faculty_detail'),
    path('faculty/<int:faculty_id>/edit/', views.edit_faculty, name='edit_faculty'),
    path('faculty/<int:faculty_id>/edit-complete/', views.edit_faculty_complete, name='edit_faculty_complete'),
    path('faculty/<int:faculty_id>/delete/', views.delete_faculty, name='delete_faculty'),
    path('faculty/<int:faculty_id>/save/', views.save_faculty, name='save_faculty'),
    path('faculty/<int:faculty_id>/profile/', views.faculty_profile_view, name='faculty_profile_view'),
    path('faculty/<int:faculty_id>/assign-subjects/', views.assign_subjects, name='assign_subjects'),
    path('faculty/<int:faculty_id>/pdf/', views.faculty_pdf, name='faculty_pdf'),
    path('faculty/<int:faculty_id>/generate-pdf/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('faculty/<int:faculty_id>/generate-pdf-clean/', views.generate_faculty_pdf_clean,
         name='generate_faculty_pdf_clean'),
    path('faculty/<int:faculty_id>/download-pdf/', views.download_faculty_pdf, name='download_faculty_pdf'),
    path('faculty/<int:faculty_id>/preview-pdf/', views.preview_faculty_pdf, name='preview_faculty_pdf'),
    path('faculty/<int:faculty_id>/check-pdf-status/', views.ajax_check_pdf_status, name='ajax_check_pdf_status'),
    path('faculty/<int:faculty_id>/debug/', views.debug_faculty_data, name='debug_faculty_data'),

    # ==================== Faculty Dashboard (named alias) ====================
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    # ==================== Research Publications, FDP, Projects (Delete URLs) ====================
    path('research-project/<int:project_id>/delete/', views.delete_research_project, name='delete_research_project'),
    path('research-publication/<int:publication_id>/delete/', views.delete_research_publication,
         name='delete_research_publication'),
    path('fdp/<int:fdp_id>/delete/', views.delete_fdp, name='delete_fdp'),
    path('btech-project/<int:project_id>/delete/', views.delete_btech_project, name='delete_btech_project'),

    # ==================== Analytics ====================
    path('faculty-analytics/', views.faculty_analytics, name='faculty_analytics'),
    path('faculty-charts/', views.faculty_charts, name='faculty_charts'),
    path('student-charts/', views.student_charts, name='student_charts'),

    # ==================== Certificate Management ====================
    path('faculty/<int:faculty_id>/certificates/', views.view_certificates, name='view_certificates'),
    path('faculty/<int:faculty_id>/certificates/upload/', views.upload_certificate, name='upload_certificate'),
    path('certificates/bulk-upload/', views.upload_certificates_bulk, name='upload_certificates_bulk'),
    path('certificates/<int:certificate_id>/edit/', views.edit_certificate, name='edit_certificate'),
    path('certificates/<int:certificate_id>/delete/', views.delete_certificate, name='delete_certificate'),
    path('faculty/<int:faculty_id>/certificates/merge/', views.merge_certificates, name='merge_certificates'),
    path('faculty/<int:faculty_id>/certificates/merge-with-pdf/', views.merge_certificates_with_pdf,
         name='merge_certificates_with_pdf'),
    path('faculty/<int:faculty_id>/certificates/preview-merged/', views.preview_merged_pdf, name='preview_merged_pdf'),

    # ==================== Cloudinary Integration ====================
    path('cloudinary/status/', views.cloudinary_status, name='cloudinary_status'),
    path('faculty/<int:faculty_id>/sync-cloudinary/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('faculty/<int:faculty_id>/upload-cloudinary/', views.upload_to_cloudinary, name='upload_to_cloudinary'),
    path('faculty/<int:faculty_id>/cloudinary-url/', views.get_cloudinary_url, name='get_cloudinary_url'),
    path('faculty/bulk-sync-cloudinary/', views.bulk_sync_to_cloudinary, name='bulk_sync_to_cloudinary'),
    path('upload-faculty-photo/', views.upload_faculty_photo, name='upload_faculty_photo'),
    path('upload-faculty-pdf/', views.upload_faculty_pdf, name='upload_faculty_pdf'),
    path('faculty/<int:faculty_id>/upload-to-cloudinary/', views.upload_faculty_to_cloudinary,
         name='upload_faculty_to_cloudinary'),

    # ==================== Bulk Operations ====================
    path('faculty/bulk-actions/', views.bulk_faculty_actions, name='bulk_faculty_actions'),
    path('faculty/bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('faculty/bulk-generate-pdfs/', views.bulk_generate_faculty_pdfs, name='bulk_generate_faculty_pdfs'),
    path('export/students/csv/', views.export_students_csv, name='export_students_csv'),
    path('export/faculty/csv/', views.export_faculty_csv, name='export_faculty_csv'),
    path('export/faculty/excel/', views.export_faculty_excel, name='export_faculty_excel'),
    path('export/students/excel/', views.export_students_excel, name='export_students_excel'),

    # ==================== API Endpoints ====================
    # Faculty APIs
    path('api/faculty/', views.api_faculty_list, name='api_faculty_list'),
    path('api/faculty/<int:faculty_id>/', views.api_faculty_detail, name='api_faculty_detail'),
    path('api/faculty/<int:faculty_id>/update-status/', views.api_update_faculty_status,
         name='api_update_faculty_status'),
    path('api/faculty/bulk-update-status/', views.api_bulk_update_faculty_status,
         name='api_bulk_update_faculty_status'),
    path('api/faculty/<int:faculty_id>/subjects/', views.api_faculty_subjects, name='api_faculty_subjects'),
    path('api/faculty/<int:faculty_id>/assign-subjects/', views.api_assign_faculty_subjects,
         name='api_assign_faculty_subjects'),
    path('api/faculty/<int:faculty_id>/research/', views.api_faculty_research, name='api_faculty_research'),
    path('api/faculty/<int:faculty_id>/fdps/', views.api_faculty_fdps, name='api_faculty_fdps'),
    path('api/faculty/<int:faculty_id>/projects/', views.api_faculty_projects, name='api_faculty_projects'),
    path('api/faculty/<int:faculty_id>/statistics/', views.faculty_statistics_api, name='faculty_statistics_api'),

    # Student APIs
    path('api/students/', views.api_students_list, name='api_students_list'),
    path('api/students/<int:student_id>/', views.api_student_detail, name='api_student_detail'),
    path('api/students/<int:student_id>/certificates/', views.api_student_certificates,
         name='api_student_certificates'),

    # Department APIs
    path('api/department/<str:department>/stats/', views.api_department_stats, name='api_department_stats'),

    # Dashboard APIs
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/quick-stats/', views.quick_stats, name='quick_stats'),

    # Search APIs
    path('api/search/faculty/', views.search_faculty, name='search_faculty'),
    path('api/search/students/', views.search_students, name='search_students'),

    # ==================== System & Utilities ====================
    path('system-status/', views.system_status, name='system_status'),
    path('recent-activity/', views.recent_activity, name='recent_activity'),
    path('clear-logs/', views.clear_logs, name='clear_logs'),
    path('backup-database/', views.backup_database, name='backup_database'),
    path('session-info/', views.session_info, name='session_info'),
    path('clear-session/', views.clear_session, name='clear_session'),

    # ==================== Application Pages ====================
    path('syllabus/', views.syllabus_view, name='syllabus'),
    path('laboratory/', views.laboratory, name='laboratory'),
    path('gallery/', views.gallery, name='gallery'),
    path('application-home/', views.application_home, name='application_home'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('about/', views.about_system, name='about_system'),
    path('help/', views.help_documentation, name='help_documentation'),
    path('contact/', views.contact_support, name='contact_support'),

    # ==================== Exam Branch URLs ====================
    path('exambranch/', views.exam_branch, name='exam_branch'),
    path('exambranch/generate-report/', views.exam_branch_generate_report, name='exam_branch_generate_report'),
    path('exambranch/batch-download/', views.exam_branch_batch_download, name='exam_branch_batch_download'),

    # ==================== PDF Generation ====================
    path('generate-pdf/', views.generate_pdf_with_data, name='generate_pdf_with_data'),
    path('preview-pdf/', views.preview_pdf_template, name='preview_pdf_template'),

    # ==================== Debug / Test ====================
    path('test/', views.test_template, name='test_template'),
    path('test-session/', views.test_session, name='test_session'),
    path('debug-cloudinary/', views.debug_cloudinary, name='debug_cloudinary'),
    path('debug-login/', views.debug_login, name='debug_login'),
]

# ==================== Error Handlers ====================
handler400 = 'dashboard.views.handler400'
handler403 = 'dashboard.views.handler403'
handler404 = 'dashboard.views.handler404'
handler500 = 'dashboard.views.handler500'