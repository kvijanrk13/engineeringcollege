"""
URL configuration for engineeringcollege project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Dashboard app URLs
    path('', include('dashboard.urls')),

    # Redirect root to dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # Project level views
    path('college-info/', views.college_info, name='college_info'),
    path('contact/', views.contact, name='contact'),
]

# Custom admin site settings
admin.site.site_header = "ANURAG Engineering College Administration"
admin.site.site_title = "College Admin Portal"
admin.site.index_title = "Welcome to College Management System"

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler404 = 'dashboard.views.handler404'
handler500 = 'dashboard.views.handler500'