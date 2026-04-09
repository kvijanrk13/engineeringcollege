# engineeringcollege/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from dashboard import views as dashboard_views

# Define error handlers - comment these out temporarily to avoid template errors
# handler404 = dashboard_views.handler404
# handler500 = dashboard_views.handler500
# handler403 = dashboard_views.handler403
# handler400 = dashboard_views.handler400


def health_check(request):
    """Health check endpoint for Render"""
    return HttpResponse("OK", status=200)


def root_view(request):
    """Root view - direct to admin login"""
    return dashboard_views.admin_login(request)


urlpatterns = [
    # Health check for Render
    path('health/', health_check, name='health_check'),

    # Admin
    path('admin/', admin.site.urls),

    # Root path - direct to admin login
    path('', root_view, name='root'),

    # Dashboard app URLs
    path('', include('dashboard.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)