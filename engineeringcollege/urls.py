from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # include dashboard app WITH namespace
    path("", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
]

# Serve media and static files in development
if settings.DEBUG:
    # Safely check if STATICFILES_DIRS is not empty to avoid IndexError
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

    # Serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)