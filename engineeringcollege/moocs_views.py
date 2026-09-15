from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.urls import reverse


def moocs_exam(request):
    verified = request.session.get("moocs_gmail_verified") is True
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
    # Flush the complete authenticated session so no Google/dashboard state can
    # immediately restore MOOC access after the two MOOC-specific keys are removed.
    logout(request)
    return redirect("moocs")
