"""
dashboard/urls.py - FINAL CLEAN VERSION
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    # =========================
    # DASHBOARD HOME
    # =========================
    path('', views.dashboard, name='dashboard'),

    # =========================
    # AUTHENTICATION
    # =========================
    path('login/', views.login_view, name='login'),
    path('student-login/', views.student_login, name='student_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # =========================
    # DASHBOARDS
    # =========================
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # =========================
    # STUDENT MANAGEMENT
    # =========================
    path('students/', views.students, name='students'),
    path('students-data/', views.students_data, name='students_data'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),

    # =========================
    # STUDENT PDF
    # =========================
    path('generate-student-pdf/<int:student_id>/', views.generate_student_pdf, name='generate_student_pdf'),
    path('view-pdf/<int:student_id>/', views.view_pdf, name='view_pdf'),
    path('download-pdf/<int:student_id>/', views.download_pdf, name='download_pdf'),

    # =========================
    # FACULTY MANAGEMENT
    # =========================
    path('faculty/', views.faculty_dashboard, name='faculty'),
    path('faculty-list/', views.faculty_list, name='faculty_list'),
    path('faculty/<int:faculty_id>/', views.faculty_dashboard, name='faculty_detail'),
    path('faculty/<int:faculty_id>/generate-pdf/', views.generate_faculty_pdf, name='generate_faculty_pdf'),
    path('faculty/<int:faculty_id>/download-pdf/', views.download_faculty_pdf, name='download_faculty_pdf'),

    # Merged PDF
    path('download-merged-pdf/<int:faculty_id>/', views.download_faculty_pdf, name='download_merged_pdf'),

    # =========================
    # CLOUDINARY
    # =========================
    path('upload-faculty-to-cloudinary/<int:faculty_id>/', views.upload_to_cloudinary, name='upload_to_cloudinary'),
    path('upload-faculty-photo/', views.upload_faculty_photo, name='upload_faculty_photo'),
    path('cloudinary-status/', views.cloudinary_status, name='cloudinary_status'),
    path('sync-to-cloudinary/<int:faculty_id>/', views.sync_to_cloudinary, name='sync_to_cloudinary'),
    path('get-cloudinary-url/<int:faculty_id>/', views.get_cloudinary_url, name='get_cloudinary_url'),

    # =========================
    # PDF PREVIEW
    # =========================
    path('preview-faculty-pdf/<int:faculty_id>/', views.preview_faculty_pdf, name='preview_faculty_pdf'),
    path('preview-merged-pdf/<int:faculty_id>/', views.preview_merged_pdf, name='preview_merged_pdf'),
    path('merge-certificates-with-pdf/<int:faculty_id>/', views.merge_certificates_with_pdf, name='merge_certificates_with_pdf'),
]
