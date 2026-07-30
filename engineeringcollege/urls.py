# engineeringcollege/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve


def health_check(request):
    """Health check endpoint for Render"""
    return HttpResponse("OK", status=200)


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('car-price/', include('car_price_app.urls')),
    path('aeclibrary/student/', include('student.urls')),
    path('aeclibrary/', include('library.urls')),
    path('etors/', include('etors.urls')),
    path('', include('dashboard.urls')),
]

# Serve static files in development.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve local media files even when DEBUG=False.
# Student photos/certificates may be stored in MEDIA_ROOT when Cloudinary is not configured.
if settings.MEDIA_URL:
    media_prefix = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += [
        re_path(
            rf'^{media_prefix}/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]
