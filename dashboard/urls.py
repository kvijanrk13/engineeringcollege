from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Login & Authentication
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Main Pages
    path("dashboard/", views.dashboard, name="dashboard"),
    path("faculty/", views.faculty, name="faculty"),
    path("syllabus/", views.syllabus, name="syllabus"),  # ✅ This fixes the error

    # PDF Utilities
    path("download-faculty-pdf/", views.download_faculty_pdf, name="download_faculty_pdf"),
    path("upload-generated-pdf/", views.upload_generated_pdf, name="upload_generated_pdf"),
]