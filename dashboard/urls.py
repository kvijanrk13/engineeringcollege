# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    # ==================== ✅ FIXED ROOT (NO LOOP) ====================
    path('', views.dashboard, name='dashboard'),  # MAIN HOME
    path('home/', views.home, name='home'),

    # ==================== Dashboard ====================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

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

    # ✅ PDF
    path('faculty/<int:faculty_id>/pdf/', views.faculty_pdf, name='faculty_pdf'),
    path('faculty/<int:faculty_id>/generate-pdf/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('faculty/<int:faculty_id>/generate-pdf-clean/', views.generate_faculty_pdf_clean,
         name='generate_faculty_pdf_clean'),
    path('faculty/<int:faculty_id>/download-pdf/', views.download_faculty_pdf, name='download_faculty_pdf'),
    path('faculty/<int:faculty_id>/preview-pdf/', views.preview_faculty_pdf, name='preview_faculty_pdf'),

    # ==================== Faculty Dashboard Alias ====================
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    # ==================== Delete ====================
    path('research-project/<int:project_id>/delete/', views.delete_research_project, name='delete_research_project'),
    path('research-publication/<int:publication_id>/delete/', views.delete_research_publication,
         name='delete_research_publication'),
    path('fdp/<int:fdp_id>/delete/', views.delete_fdp, name='delete_fdp'),
    path('btech-project/<int:project_id>/delete/', views.delete_btech_project, name='delete_btech_project'),

    # ==================== Analytics ====================
    path('faculty-analytics/', views.faculty_analytics, name='faculty_analytics'),
    path('faculty-charts/', views.faculty_charts, name='faculty_charts'),
    path('student-charts/', views.student_charts, name='student_charts'),

    # ==================== Certificates ====================
    path('faculty/<int:faculty_id>/certificates/', views.view_certificates, name='view_certificates'),
    path('faculty/<int:faculty_id>/certificates/upload/', views.upload_certificate, name='upload_certificate'),
    path('certificates/<int:certificate_id>/delete/', views.delete_certificate, name='delete_certificate'),

    # ==================== Cloudinary ====================
    path('cloudinary/status/', views.cloudinary_status, name='cloudinary_status'),

    # ==================== APIs ====================
    path('api/faculty/', views.api_faculty_list, name='api_faculty_list'),
    path('api/students/', views.api_students_list, name='api_students_list'),

    # ==================== Utilities ====================
    path('system-status/', views.system_status, name='system_status'),

    # ==================== Pages ====================
    path('syllabus/', views.syllabus_view, name='syllabus'),
    path('gallery/', views.gallery, name='gallery'),

    # ==================== Exam Branch ====================
    path('exam-branch/', views.exam_branch, name='exam_branch'),
    path('exam-branch/generate-report/', views.exam_branch_generate_report, name='exam_branch_generate_report'),
    path('exam-branch/batch-download/', views.exam_branch_batch_download, name='exam_branch_batch_download'),

    # ==================== Profile Settings ====================
    path('profile-settings/', views.profile_settings, name='profile_settings'),

    # ==================== About System ====================
    path('about/', views.about_system, name='about_system'),

    # ==================== Help Documentation ====================
    path('help/', views.help_documentation, name='help_documentation'),

    # ==================== Contact Support ====================
    path('contact/', views.contact_support, name='contact_support'),

    # ==================== Laboratory ====================
    path('laboratory/', views.laboratory, name='laboratory'),

    # ==================== Debug ====================
    path('test/', views.test_template, name='test_template'),
]