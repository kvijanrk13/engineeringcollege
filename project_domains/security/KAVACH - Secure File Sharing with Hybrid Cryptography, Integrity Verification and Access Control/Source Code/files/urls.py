from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path("", views.my_files_view, name="my_files"),
    path("upload/", views.upload_file_view, name="upload"),
    path("download/<int:file_id>/", views.download_file_view, name="download"),
]
