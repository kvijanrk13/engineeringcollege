from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("faculty/", views.faculty, name="faculty"),
    path("logout/", views.logout_view, name="logout"),

    path("download-faculty-pdf/", views.download_faculty_pdf, name="download_faculty_pdf"),

    # REQUIRED ENDPOINT
    path("upload-generated-pdf/", views.upload_generated_pdf, name="upload_generated_pdf"),
]
