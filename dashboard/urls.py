from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Authentication
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Main Navigation
    path("dashboard/", views.dashboard, name="dashboard"),
    path("faculty/", views.faculty, name="faculty"),
    path("syllabus/", views.syllabus, name="syllabus"),

    # Horizontal Tab Placeholders
    path("students/", views.students, name="students"),
    path("exams/", views.exams, name="exambranch"),
    path("laboratory/", views.laboratory, name="laboratory"),
    path("gallery/", views.gallery, name="gallery"),

    # Utilities
    path("download-faculty-pdf/", views.download_faculty_pdf, name="download_faculty_pdf"),
    path("upload-generated-pdf/", views.upload_generated_pdf, name="upload_generated_pdf"),
]