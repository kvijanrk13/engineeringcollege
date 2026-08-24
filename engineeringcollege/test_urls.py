"""Minimal URL configuration for isolated library automation tests."""

from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView


def google_login_stub(request):
    """URL-reversal stub used by the student login/signup templates."""

    return HttpResponse(status=501)


urlpatterns = [
    path("MOOCS", TemplateView.as_view(template_name="moocs/index.html"), name="moocs"),
    path("MOOCS/", TemplateView.as_view(template_name="moocs/index.html")),
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
