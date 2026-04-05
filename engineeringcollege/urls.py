# engineeringcollege/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from dashboard import views as dashboard_views

# Define handler404, handler500, etc. at module level for the project
handler404 = dashboard_views.handler404
handler500 = dashboard_views.handler500
handler403 = dashboard_views.handler403
handler400 = dashboard_views.handler400

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Public entry points
    path('', dashboard_views.login_view, name='root_login'),
    path('home/', dashboard_views.login_view, name='home_root'),

    # Dashboard app (includes all functionality) - ONLY ONCE to avoid namespace warning
    path('', include('dashboard.urls')),

    # Direct login routes for convenience
    path('login/', dashboard_views.login_view, name='login_root'),
    path('admin-login/', dashboard_views.admin_login, name='admin_login_root'),
    path('student-login/', dashboard_views.student_login, name='student_login_root'),
    path('logout/', dashboard_views.logout_view, name='logout_root'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar if installed (optional)
    try:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
    except ImportError:
        pass
