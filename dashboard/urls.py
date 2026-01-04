from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("index/", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("faculty/", views.faculty, name="faculty"),
    path("students/", views.students, name="students"),
    path("library/", views.library, name="library"),
    path("syllabus/", views.syllabus, name="syllabus"),
    path("exambranch/", views.exambranch, name="exambranch"),
    path("gallery/", views.gallery, name="gallery"),
    path("login/", views.login_view, name="login_explicit"),
    path("logout/", views.logout_view, name="logout"),
    path("download-faculty-pdf/", views.download_faculty_pdf),
    path("upload-generated-pdf/", views.upload_generated_pdf),
]
