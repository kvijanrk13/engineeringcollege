import hashlib
from urllib.parse import urlencode

import requests
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core import signing
from django.urls import reverse
from django.shortcuts import redirect, render

from crypto_engine.key_manager import generate_oauth_user_key_pair, generate_user_key_pair
from .forms import RegisterForm
from .models import UserKey


def _google_signin_enabled():
    return bool(
        getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
        and getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
    )


def _google_callback_url(request):
    return request.build_absolute_uri(reverse("accounts:google_callback"))


def _oauth_key_secret(email):
    seed = f"{settings.SECRET_KEY}:{email.lower()}:kavach-oauth-private-key"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _unique_google_username(email):
    username_base = email.split("@", 1)[0].lower().replace(".", "_")
    username_base = "".join(char for char in username_base if char.isalnum() or char in "_-")
    username_base = username_base[:140] or "gmail_user"
    username = username_base
    counter = 1
    while User.objects.filter(username=username).exists():
        counter += 1
        username = f"{username_base}_{counter}"
    return username


def _ensure_gmail_user_key(user):
    if hasattr(user, "key_pair"):
        return
    key_pair = generate_oauth_user_key_pair(_oauth_key_secret(user.email))
    UserKey.objects.create(
        user=user,
        public_key=key_pair["public_key"],
        encrypted_private_key=key_pair["encrypted_private_key"],
        key_source=UserKey.GMAIL,
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            key_pair = generate_user_key_pair(form.cleaned_data["password1"])
            UserKey.objects.create(
                user=user,
                public_key=key_pair["public_key"],
                encrypted_private_key=key_pair["encrypted_private_key"],
            )
            login(request, user)
            messages.success(request, "Registration successful. RSA keys were generated for your account.")
            return redirect("accounts:profile")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {
        "form": form,
        "google_signin_enabled": _google_signin_enabled(),
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login successful.")
            return redirect("accounts:profile")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {
        "form": form,
        "google_signin_enabled": _google_signin_enabled(),
    })


def google_login_view(request):
    if not _google_signin_enabled():
        messages.error(request, "Gmail sign-in is not configured yet. Add Google OAuth credentials first.")
        return redirect("accounts:register")

    state = signing.dumps({"next": request.GET.get("next") or reverse("accounts:profile")}, salt="kavach-google-oauth")
    request.session["kavach_google_oauth_state"] = state
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": _google_callback_url(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


def google_callback_view(request):
    expected_state = request.session.pop("kavach_google_oauth_state", "")
    received_state = request.GET.get("state", "")
    if not expected_state or expected_state != received_state:
        messages.error(request, "Invalid Gmail sign-in session. Please try again.")
        return redirect("accounts:register")

    try:
        state_payload = signing.loads(received_state, salt="kavach-google-oauth", max_age=10 * 60)
    except signing.BadSignature:
        messages.error(request, "Gmail sign-in expired. Please try again.")
        return redirect("accounts:register")

    code = request.GET.get("code", "")
    if not code:
        messages.error(request, "Gmail sign-in was cancelled or failed.")
        return redirect("accounts:register")

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": _google_callback_url(request),
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    if token_response.status_code != 200:
        messages.error(request, "Could not verify Gmail sign-in with Google.")
        return redirect("accounts:register")

    access_token = token_response.json().get("access_token")
    profile_response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if profile_response.status_code != 200:
        messages.error(request, "Could not read Gmail profile details.")
        return redirect("accounts:register")

    profile = profile_response.json()
    email = (profile.get("email") or "").strip().lower()
    if not profile.get("email_verified") or not email.endswith("@gmail.com"):
        messages.error(request, "Please sign in with a verified Gmail account.")
        return redirect("accounts:register")

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User.objects.create_user(
            username=_unique_google_username(email),
            email=email,
            first_name=(profile.get("given_name") or "")[:150],
            last_name=(profile.get("family_name") or "")[:150],
        )
        user.set_unusable_password()
        user.save()

    _ensure_gmail_user_key(user)
    login(request, user)
    messages.success(request, "Gmail sign-in successful. RSA keys are ready for your account.")
    return redirect(state_payload.get("next") or "accounts:profile")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    key_pair = getattr(request.user, "key_pair", None)
    return render(request, "accounts/profile.html", {"key_pair": key_pair})
