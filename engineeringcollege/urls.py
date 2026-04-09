# engineeringcollege/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import redirect


def health_check(request):
    """Health check endpoint for Render"""
    return HttpResponse("OK", status=200)


def home_view(request):
    """Direct response to verify Django is handling the root URL"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>ANURAG Engineering College</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🏫 ANURAG Engineering College</h1>
        <p style="color: green;">✅ Django is successfully handling the root URL!</p>
        <p>Server time: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <hr>
        <h3>Navigation:</h3>
        <ul style="list-style: none; padding: 0;">
            <li><a href="/admin-login/">🔐 Admin Login</a></li>
            <li><a href="/student-login/">👨‍🎓 Student Login</a></li>
            <li><a href="/admin/">⚙️ Django Admin</a></li>
            <li><a href="/test/">🧪 Test Page</a></li>
        </ul>
    </body>
    </html>
    """)


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Direct response - no redirect
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)