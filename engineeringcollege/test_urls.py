"""Minimal URL configuration for isolated library automation tests."""

from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView
from engineeringcollege.moocs_views import moocs_exam, moocs_logout


def google_login_stub(request):
    """URL-reversal stub used by the student login/signup templates."""

    return HttpResponse(status=501)


urlpatterns = [
    path("MOOCS", moocs_exam, name="moocs"),
    path("MOOCS/", moocs_exam),
    path("MOOCS/logout/", moocs_logout, name="moocs_logout"),
    path(
        "accounts/",
        include(
            ([path("google-login/", google_login_stub, name="google_login")], "dashboard"),
            namespace="dashboard",
        ),
    ),
    path("aeclibrary/student/", include("student.urls")),
    path("aeclibrary/", include("library.urls")),
]
