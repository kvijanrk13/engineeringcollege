from urllib.parse import urlencode
import logging

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.urls import reverse
from dashboard.models import MoocsVisitor


logger = logging.getLogger(__name__)


def moocs_exam(request):
    verified = request.session.get("moocs_gmail_verified") is True
    email = request.session.get("moocs_gmail_email", "").strip().lower()
    if verified and email:
        try:
            # Retry this on every verified visit so sessions created during a
            # transient database error are still included in the unique count.
            MoocsVisitor.objects.update_or_create(email=email, defaults={"email": email})
        except Exception:
            logger.exception("Unable to record verified MOOCS visitor")
    login_query = urlencode({"role": "student", "target": "moocs"})
    visitor_count = MoocsVisitor.objects.count()
    response = render(
        request,
        "moocs/index.html",
        {
            "moocs_gmail_verified": verified,
            "moocs_gmail_email": email,
            "moocs_google_login_url": f"{reverse('dashboard:google_login')}?{login_query}",
            "google_signin_enabled": bool(
                getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
                and getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
            ),
            "moocs_visitor_count": visitor_count,
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
