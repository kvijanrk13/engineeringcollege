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

    # Student Registration & Data
    path("students/", views.students, name="students"),
    path("students-data/", views.students_data, name="students_data"),
    path("view-pdf/<int:student_id>/", views.view_pdf, name="view_pdf"),
    path("download-pdf/<int:student_id>/", views.download_pdf, name="download_pdf"),
    path("delete-student/<int:student_id>/", views.delete_student, name="delete_student"),

    # Faculty Registration & Management
    path("save-faculty-details/", views.save_faculty_details, name="save_faculty_details"),
    path("upload-faculty-photo/", views.upload_faculty_photo, name="upload_faculty_photo"),
    path("upload-faculty-pdf/", views.upload_faculty_pdf, name="upload_faculty_pdf"),
    path("delete-faculty/<int:faculty_id>/", views.delete_faculty, name="delete_faculty"),

    # Other Tabs
    path("exambranch/", views.exambranch, name="exambranch"),
    path("laboratory/", views.laboratory, name="laboratory"),
    path("library/", views.library, name="library"),
    path("gallery/", views.gallery, name="gallery"),

    # Utilities
    path("download-faculty-pdf/", views.download_faculty_pdf, name="download_faculty_pdf"),
    path("upload-generated-pdf/", views.upload_generated_pdf, name="upload_generated_pdf"),
]