# engineeringcollege/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [

    # Root → redirect to dashboard home
    path('', RedirectView.as_view(
        pattern_name='dashboard:dashboard',
        permanent=False
    ), name='home'),

    # Dashboard app
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),

    # Admin panel
    path('admin/', admin.site.urls),
]

# Serve static & media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
