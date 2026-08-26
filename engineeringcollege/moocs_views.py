from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse


def moocs_exam(request):
    verified = request.session.get("moocs_gmail_verified") is True
    if verified:
        request.session["moocs_exam_lock"] = True
    login_query = urlencode({"role": "student", "target": "moocs"})
    response = render(
        request,
        "moocs/index.html",
        {
            "moocs_gmail_verified": verified,
            "moocs_gmail_email": request.session.get("moocs_gmail_email", ""),
            "moocs_google_login_url": f"{reverse('dashboard:google_login')}?{login_query}",
            "google_signin_enabled": bool(
                getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
                and getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
            ),
        },
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


def moocs_logout(request):
    request.session.pop("moocs_gmail_verified", None)
    request.session.pop("moocs_gmail_email", None)
    request.session.pop("moocs_exam_lock", None)
    return redirect("moocs")
