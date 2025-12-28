from django.urls import path
from . import views
from .views import download_faculty_pdf

app_name = 'dashboard'

urlpatterns = [
    # --- ROOT URL POINTS TO LOGIN ---
    path('', views.login_view, name='login'),

    # --- DASHBOARD & OTHER PAGES ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('index/', views.index, name='index'),  # Kept index accessible if needed
    path('about/', views.about, name='about'),
    path('faculty/', views.faculty, name='faculty'),
    path('students/', views.students, name='students'),
    path('library/', views.library, name='library'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('exambranch/', views.exambranch, name='exambranch'),
    path('gallery/', views.gallery, name='gallery'),

    # --- AUTHENTICATION ---
    path('login/', views.login_view, name='login_explicit'),  # distinct name if needed
    path('logout/', views.logout_view, name='logout'),

    # --- PDF DOWNLOAD ---
    path('download-faculty-pdf/', download_faculty_pdf, name='download_faculty_pdf'),
]