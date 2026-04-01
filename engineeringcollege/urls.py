from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse  # Add this import

# Health check view
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'database': 'connected' if settings.DATABASES else 'error',
        'environment': 'production'
    })

urlpatterns = [
    path('health/', health_check),  # Add health check first
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = 'dashboard.views.handler400'
handler403 = 'dashboard.views.handler403'
handler404 = 'dashboard.views.handler404'
handler500 = 'dashboard.views.handler500'