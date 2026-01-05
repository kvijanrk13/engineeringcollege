from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ REQUIRED: include dashboard app WITH namespace
    path("", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
]
