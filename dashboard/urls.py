from django.urls import path
from dashboard.views import (
    login_view,
    dashboard,
    index,
    about,
    faculty,
    students,
    library,
    syllabus,
    exambranch,
    gallery,
    logout_view,
    download_faculty_pdf,
    upload_generated_pdf,
)

app_name = "dashboard"

urlpatterns = [
    path("", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("index/", index, name="index"),
    path("about/", about, name="about"),
    path("faculty/", faculty, name="faculty"),
    path("students/", students, name="students"),
    path("library/", library, name="library"),
    path("syllabus/", syllabus, name="syllabus"),
    path("exambranch/", exambranch, name="exambranch"),
    path("gallery/", gallery, name="gallery"),
    path("login/", login_view, name="login_explicit"),
    path("logout/", logout_view, name="logout"),
    path("download-faculty-pdf/", download_faculty_pdf),
    path("upload-generated-pdf/", upload_generated_pdf),
]
