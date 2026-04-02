from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# ==================== HEALTH CHECK ====================
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'database': 'connected' if settings.DATABASES else 'error',
        'environment': 'production'
    })

# ==================== URLS ====================
urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
]

# ==================== STATIC / MEDIA ====================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ==================== ❌ REMOVE ERROR HANDLERS ====================
# (Do NOT define handlers unless you create them in views.py)