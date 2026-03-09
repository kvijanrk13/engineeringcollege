# engineeringcollege/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Include dashboard URLs - this handles all dashboard routes including the root
    path('', include('dashboard.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler400 = 'dashboard.views.handler400'
handler403 = 'dashboard.views.handler403'
handler404 = 'dashboard.views.handler404'
handler500 = 'dashboard.views.handler500'