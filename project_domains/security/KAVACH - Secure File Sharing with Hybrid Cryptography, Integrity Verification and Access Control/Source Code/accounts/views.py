from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from crypto_engine.key_manager import generate_user_key_pair
from .forms import RegisterForm
from .models import UserKey


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

    return render(request, "accounts/register.html", {"form": form})


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

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    key_pair = getattr(request.user, "key_pair", None)
    return render(request, "accounts/profile.html", {"key_pair": key_pair})
