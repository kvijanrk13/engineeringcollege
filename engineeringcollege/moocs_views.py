from urllib.parse import urlencode
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

MOCS_SET_3_ACCESS_FEE = getattr(settings, "MOOCS_SET_3_ACCESS_FEE", 499.00)


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
    set_number = int(body.get("set_number", 3))

    if not verified or email != session_email:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    # Check if already paid
    if MoocsPayment.objects.filter(email=email, set_number=set_number, status="completed").exists():
        return JsonResponse({"success": True, "already_paid": True})

    amount = int(MOCS_SET_3_ACCESS_FEE * 100)

    try:
        razorpay_order = _get_razorpay_client().order.create(
            dict(
                amount=amount,
                currency="INR",
                receipt=f"moocs_set_{set_number}_{email}",
            )
        )
    except Exception:
        logger.exception("Failed to create Razorpay order for MOOCS Set %s", set_number)
        return JsonResponse({"success": False, "error": "Unable to create payment order"}, status=500)

    MoocsPayment.objects.update_or_create(
        email=email,
        set_number=set_number,
        defaults={
            "amount": MOCS_SET_3_ACCESS_FEE,
            "razorpay_order_id": razorpay_order["id"],
            "status": "pending",
        },
    )

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
    set_number = int(body.get("set_number", 3))
    payment_id = body.get("razorpay_payment_id", "")
    order_id = body.get("razorpay_order_id", "")
    signature = body.get("razorpay_signature", "")

    if not verified or email != session_email:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    params_dict = {
        "razorpay_payment_id": payment_id,
        "razorpay_order_id": order_id,
        "razorpay_signature": signature,
    }

    try:
        result = _get_razorpay_client().utility.verify_payment_signature(params_dict)
        if result is not None:
            raise ValueError("Signature verification failed")
    except Exception:
        logger.exception("Razorpay signature verification failed for MOOCS Set %s", set_number)
        MoocsPayment.objects.filter(email=email, set_number=set_number).update(status="failed")
        return JsonResponse({"success": False, "error": "Payment verification failed"}, status=400)

    MoocsPayment.objects.filter(
        email=email, set_number=set_number, razorpay_order_id=order_id
    ).update(
        status="completed",
        razorpay_payment_id=payment_id,
        razorpay_signature=signature,
    )

    return JsonResponse({"success": True, "set_number": set_number, "email": email})


def moocs_logout(request):
    logout(request)
    return redirect("moocs")
