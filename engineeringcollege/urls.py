# =========================================
# engineeringcollege/urls.py (FINAL VERSION)
# =========================================

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


# =========================================
# ✅ ROOT REDIRECT (CRITICAL FIX)
# =========================================
def home(request):
    return redirect('dashboard:dashboard')


urlpatterns = [
    # 🔥 IMPORTANT: Default route fix
    path('', home),

    # Admin
    path('admin/', admin.site.urls),

    # Dashboard app
    path('', include('dashboard.urls')),
]


# =========================================
# ✅ STATIC & MEDIA (LOCAL ONLY)
# =========================================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# =========================================
# ✅ ERROR HANDLERS
# =========================================
handler400 = 'dashboard.views.handler400'
handler403 = 'dashboard.views.handler403'
handler404 = 'dashboard.views.handler404'
handler500 = 'dashboard.views.handler500'