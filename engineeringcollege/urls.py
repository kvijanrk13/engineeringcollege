# engineeringcollege/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from dashboard import views as dashboard_views

# Define handler404, handler500, etc. at module level for the project
handler404 = dashboard_views.handler404
handler500 = dashboard_views.handler500
handler403 = dashboard_views.handler403
handler400 = dashboard_views.handler400


def root_redirect(request):
    """Redirect root to admin login"""
    return redirect('dashboard:admin_login')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Root path - redirect to admin login
    path('', root_redirect, name='root'),

    # Dashboard app (includes all functionality)
    path('', include('dashboard.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)