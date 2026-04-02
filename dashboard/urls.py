from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    # ==================== ROOT ====================
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),

    # ==================== AUTH ====================
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('student-logout/', views.student_logout, name='student_logout'),

    # ==================== DASHBOARD ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    # ==================== STUDENTS ====================
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students-data/', views.students_data, name='students_data'),
    path('students/', views.students_list, name='students'),
    path('students/list/', views.students_list, name='students_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('students/import/', views.import_students, name='import_students'),
    path('students/export/', views.export_students, name='export_students'),

    # ==================== FACULTY ====================
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('faculty/<int:faculty_id>/', views.faculty_dashboard, name='faculty_detail'),
    path('faculty/list/', views.faculty_list, name='faculty_list'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/<int:faculty_id>/edit-complete/', views.edit_faculty_complete, name='edit_faculty_complete'),
    path('faculty/<int:faculty_id>/profile/', views.faculty_profile_view, name='faculty_profile_view'),

    # ==================== SYSTEM ====================
    path('system-status/', views.system_status, name='system_status'),
    path('system/status/', views.system_status, name='system_status_alt'),
    path('system/health/', views.system_health, name='system_health'),
    path('system/info/', views.system_info, name='system_info'),
    path('system/settings/', views.system_settings, name='system_settings'),

    # ==================== DELETE ====================
    path('research-project/<int:project_id>/delete/', views.delete_research_project, name='delete_research_project'),
    path('research-publication/<int:publication_id>/delete/', views.delete_research_publication, name='delete_research_publication'),
    path('fdp/<int:fdp_id>/delete/', views.delete_fdp, name='delete_fdp'),
    path('btech-project/<int:project_id>/delete/', views.delete_btech_project, name='delete_btech_project'),

    # ==================== ANALYTICS ====================
    path('faculty-analytics/', views.faculty_analytics, name='faculty_analytics'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('reports/', views.reports_view, name='reports'),
    path('statistics/', views.statistics_view, name='statistics'),

    # ==================== PAGES ====================
    path('syllabus/', views.syllabus_view, name='syllabus'),
    path('gallery/', views.gallery, name='gallery'),
    path('laboratory/', views.laboratory, name='laboratory'),
    path('exam-branch/', views.exam_branch, name='exam_branch'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('help/', views.help_view, name='help'),

    # ==================== CLOUDINARY ====================
    path('faculty/<int:faculty_id>/sync/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('faculty/<int:faculty_id>/upload/', views.upload_to_cloudinary, name='upload_to_cloudinary'),

    # ==================== API / DATA ====================
    path('api/students/', views.api_students, name='api_students'),
    path('api/faculty/', views.api_faculty, name='api_faculty'),
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('get-data/', views.get_data, name='get_data'),
    path('fetch-data/', views.fetch_data, name='fetch_data'),

    # ==================== DEBUG ====================
    path('test/', views.test_template, name='test_template'),
    path('debug-login/', views.debug_login, name='debug_login'),
    path('debug-cloudinary/', views.debug_cloudinary, name='debug_cloudinary'),
    path('debug-session/', views.test_session, name='test_session'),
    path('debug-faculty/<int:faculty_id>/', views.debug_faculty_data, name='debug_faculty_data'),
]