# engineeringcollege/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard app (root)
    path("", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
]

# ✅ Serve static & media in development - CRITICAL FOR STUDENT PHOTOS
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ Also serve media in production if needed (adjust as per your deployment)
if not settings.DEBUG:
    # You might want to configure your web server (nginx/apache) to serve media files
    # For now, we'll also add this for safety
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)