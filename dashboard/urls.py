from django.urls import path
from . import views
from .views import download_faculty_pdf

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('faculty/', views.faculty, name='faculty'),
    path('students/', views.students, name='students'),
    path('library/', views.library, name='library'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('exambranch/', views.exambranch, name='exambranch'),
    path('gallery/', views.gallery, name='gallery'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('download-faculty-pdf/', download_faculty_pdf, name='download_faculty_pdf'),
]
