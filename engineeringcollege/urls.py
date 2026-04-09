from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views

urlpatterns = [
    # Home page -> login page
    path('', views.login_view, name='home'),

    # Dashboard app URLs
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),

    # Admin
    path('admin/', admin.site.urls),
]

# Serve static/media only in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)