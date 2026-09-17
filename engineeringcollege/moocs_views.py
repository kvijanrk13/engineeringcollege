from urllib.parse import urlencode
from decimal import Decimal
import json
import logging

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import MoocsPayment, MoocsVisitor


logger = logging.getLogger(__name__)

MOOCS_SET_3_ACCESS_FEE = Decimal(
    str(getattr(settings, "MOOCS_SET_3_ACCESS_FEE", "200.00") or "200.00")
)
MOCS_SET_3_ACCESS_FEE = MOOCS_SET_3_ACCESS_FEE


def moocs_exam(request):
    verified = request.session.get("moocs_gmail_verified") is True
    email = request.session.get("moocs_gmail_email", "").strip().lower()
    if verified and email:
        try:
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
            "moocs_razorpay_key_id": getattr(settings, "RAZORPAY_KEY_ID", ""),
        },
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


def _get_razorpay_client():
    import razorpay
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _razorpay_configured():
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)


def _render_payment_error(request, email, error, status=500):
    return render(
        request,
        "moocs/payment.html",
        {
            "moocs_gmail_email": email,
            "payment_error": error,
        },
        status=status,
    )


def _create_moocs_order(email, set_number):
    if not _razorpay_configured():
        raise RuntimeError("Razorpay credentials are not configured")
    amount = int(MOCS_SET_3_ACCESS_FEE * 100)
    razorpay_order = _get_razorpay_client().order.create(
        dict(
            amount=amount,
            currency="INR",
            receipt=f"moocs_set_{set_number}_{email}",
        )
    )
    MoocsPayment.objects.update_or_create(
        email=email,
        set_number=set_number,
        defaults={
            "amount": MOCS_SET_3_ACCESS_FEE,
            "razorpay_order_id": razorpay_order["id"],
            "status": "pending",
        },
    )
    return razorpay_order, amount


def moocs_payment(request):
    verified = request.session.get("moocs_gmail_verified") is True
    email = request.session.get("moocs_gmail_email", "").strip().lower()
    if not verified or not email:
        login_query = urlencode({"role": "student", "target": "moocs"})
        return redirect(f"{reverse('dashboard:google_login')}?{login_query}")

    try:
        set_number = int(request.GET.get("set", "3"))
    except (TypeError, ValueError):
        set_number = 3
    if set_number != 3:
        set_number = 3

    existing_payment = MoocsPayment.objects.filter(
        email=email, set_number=set_number
    ).order_by("-updated_at").first()
    if existing_payment and existing_payment.status == "completed":
        return redirect("/MOOCS/?payment=success&next_set=3")

    if not _razorpay_configured():
        return _render_payment_error(
            request,
            email,
            "Razorpay is not configured on this deployment. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in Render environment variables.",
            status=503,
        )

    try:
        razorpay_order, amount = _create_moocs_order(email, set_number)
    except Exception:
        logger.exception("Failed to create Razorpay order for MOOCS Set %s", set_number)
        return _render_payment_error(
                request,
                email,
                "Unable to create the Razorpay payment order. Please try again.",
            )

    response = render(
        request,
        "moocs/payment.html",
        {
            "moocs_gmail_email": email,
            "moocs_set_number": set_number,
            "moocs_amount": amount,
            "moocs_amount_paise": amount,
            "moocs_razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "moocs_razorpay_order_id": razorpay_order["id"],
        },
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


@csrf_exempt
def moocs_create_order(request):
    if not request.method == "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    verified = request.session.get("moocs_gmail_verified") is True
    session_email = request.session.get("moocs_gmail_email", "").strip().lower()

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid request body"}, status=400)

    email = body.get("email", "").strip().lower()
    try:
        set_number = int(body.get("set_number", 3))
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid set number"}, status=400)

    if set_number != 3:
        return JsonResponse({"success": False, "error": "Set 3 payment is required"}, status=400)

    if not _razorpay_configured():
        return JsonResponse(
            {"success": False, "error": "Razorpay is not configured on this deployment"},
            status=503,
        )

    if not verified or email != session_email:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    # Check if already paid
    if MoocsPayment.objects.filter(email=email, set_number=set_number, status="completed").exists():
        return JsonResponse({"success": True, "already_paid": True})

    try:
        razorpay_order, amount = _create_moocs_order(email, set_number)
    except Exception:
        logger.exception("Failed to create Razorpay order for MOOCS Set %s", set_number)
        return JsonResponse({"success": False, "error": "Unable to create payment order"}, status=500)

    return JsonResponse(
        {
            "success": True,
            "order_id": razorpay_order["id"],
            "amount": amount,
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID,
            "set_number": set_number,
            "email": email,
        }
    )


@csrf_exempt
def moocs_verify_payment(request):
    if not request.method == "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    verified = request.session.get("moocs_gmail_verified") is True
    session_email = request.session.get("moocs_gmail_email", "").strip().lower()

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid request body"}, status=400)

    email = body.get("email", "").strip().lower()
    try:
        set_number = int(body.get("set_number", 3))
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid set number"}, status=400)

    if set_number != 3:
        return JsonResponse({"success": False, "error": "Set 3 payment is required"}, status=400)

    payment_id = body.get("razorpay_payment_id", "")
    order_id = body.get("razorpay_order_id", "")
    signature = body.get("razorpay_signature", "")

    if not verified or email != session_email:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    payment_record = MoocsPayment.objects.filter(
        email=email, set_number=set_number, razorpay_order_id=order_id
    ).first()
    if not payment_record:
        return JsonResponse({"success": False, "error": "Payment order not found"}, status=400)

    params_dict = {
        "razorpay_payment_id": payment_id,
        "razorpay_order_id": order_id,
        "razorpay_signature": signature,
    }

    try:
        result = _get_razorpay_client().utility.verify_payment_signature(params_dict)
        if result is not None:
            raise ValueError("Signature verification failed")
        gateway_payment = _get_razorpay_client().payment.fetch(payment_id)
        if gateway_payment.get("order_id") != order_id or gateway_payment.get("status") != "captured":
            raise ValueError("Payment was not captured")
    except Exception:
        logger.exception("Razorpay payment verification failed for MOOCS Set %s", set_number)
        payment_record.status = "failed"
        payment_record.save(update_fields=["status", "updated_at"])
        return JsonResponse({"success": False, "error": "Payment verification failed"}, status=400)

    payment_record.status = "completed"
    payment_record.razorpay_payment_id = payment_id
    payment_record.razorpay_signature = signature
    payment_record.save(update_fields=[
        "status",
        "razorpay_payment_id",
        "razorpay_signature",
        "updated_at",
    ])

    return JsonResponse({"success": True, "set_number": set_number, "email": email})


def moocs_logout(request):
    logout(request)
    return redirect("moocs")
