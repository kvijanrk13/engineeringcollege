from urllib.parse import urlencode
import json
import logging

from django.contrib.auth import logout
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import MoocsVisitor, MoocsExamResult
from .moocs_formulas import build_formula_payload, formula_totals


logger = logging.getLogger(__name__)


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
    has_completed_set_2 = bool(
        verified
        and email
        and MoocsExamResult.objects.filter(email=email, set_number=2).exists()
    )
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
            "moocs_has_completed_set_2": has_completed_set_2,
        },
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


def moocs_payment(request):
    return redirect("moocs")


def moocs_formulas(request):
    """Reference sheet of every formula for GATE, UGC NET and TS SET patterns."""
    verified = request.session.get("moocs_gmail_verified") is True
    email = request.session.get("moocs_gmail_email", "").strip().lower()

    if not verified or not email:
        login_query = urlencode({"role": "student", "target": "moocs"})
        return redirect(f"{reverse('dashboard:google_login')}?{login_query}")

    pattern_count, subject_count, formula_count = formula_totals()

    response = render(
        request,
        "moocs/formulas.html",
        {
            "moocs_gmail_verified": True,
            "moocs_gmail_email": email,
            "moocs_formula_patterns": build_formula_payload(),
            "moocs_pattern_count": pattern_count,
            "moocs_subject_count": subject_count,
            "moocs_formula_count": formula_count,
            "active_pattern": request.GET.get("pattern", "gate"),
        },
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


def moocs_logout(request):
    logout(request)
    return redirect("moocs")


def moocs_save_result(request):
    """Save exam result for a completed set."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    verified = request.session.get("moocs_gmail_verified") is True
    session_email = request.session.get("moocs_gmail_email", "").strip().lower()

    if not verified or not session_email:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    try:
        body = json.loads(request.body)
        if not isinstance(body, dict):
            raise ValueError("Expected a JSON object")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid request body"}, status=400)

    raw_email = body.get("email")
    if not isinstance(raw_email, str) or not raw_email.strip():
        return JsonResponse({"success": False, "error": "Email is required"}, status=400)
    email = raw_email.strip().lower()
    if email != session_email:
        return JsonResponse({"success": False, "error": "Email mismatch"}, status=403)

    set_number = body.get("set_number")
    score = body.get("score", 0)
    correct = body.get("correct", 0)
    incorrect = body.get("incorrect", 0)
    unattempted = body.get("unattempted", 0)
    accuracy = body.get("accuracy", 0.0)
    total_questions = body.get("total_questions", 100)
    max_marks = body.get("max_marks", 200)
    subject_scores = body.get("subject_scores", {})

    if (
        isinstance(set_number, bool)
        or not isinstance(set_number, int)
        or not 1 <= set_number <= 400
    ):
        return JsonResponse({"success": False, "error": "Invalid set number"}, status=400)

    if set_number >= 3 and not MoocsExamResult.objects.filter(
        email=email, set_number=2
    ).exists():
        return JsonResponse(
            {"success": False, "error": "Complete Set 2 to access and save later sets"},
            status=403,
        )

    # Save or update the exam result
    result, created = MoocsExamResult.objects.update_or_create(
        email=email,
        set_number=set_number,
        defaults={
            "score": score,
            "correct": correct,
            "incorrect": incorrect,
            "unattempted": unattempted,
            "accuracy": accuracy,
            "total_questions": total_questions,
            "max_marks": max_marks,
            "subject_scores": subject_scores,
        }
    )

    return JsonResponse({
        "success": True,
        "created": created,
        "set_number": result.set_number,
        "score": result.score,
    })


def moocs_scorecard(request):
    """Retrieve all completed exam results for the authenticated user."""
    verified = request.session.get("moocs_gmail_verified") is True
    email = request.session.get("moocs_gmail_email", "").strip().lower()

    if not verified or not email:
        login_query = urlencode({"role": "student", "target": "moocs"})
        return redirect(f"{reverse('dashboard:google_login')}?{login_query}")

    results = MoocsExamResult.objects.filter(email=email).order_by('set_number')

    # Prepare data for template
    scorecard_data = []
    for result in results:
        scorecard_data.append({
            'set_number': result.set_number,
            'score': result.score,
            'max_marks': result.max_marks,
            'correct': result.correct,
            'incorrect': result.incorrect,
            'unattempted': result.unattempted,
            'accuracy': result.accuracy,
            'total_questions': result.total_questions,
            'subject_scores': result.subject_scores,
            'completed_at': result.completed_at,
        })

    return render(request, "moocs/scorecard.html", {
        "moocs_gmail_email": email,
        "moocs_gmail_verified": verified,
        "scorecard_data": scorecard_data,
        "total_sets_completed": len(scorecard_data),
        "average_score": sum(r['score'] for r in scorecard_data) / len(scorecard_data) if scorecard_data else 0,
        "highest_score": max((r['score'] for r in scorecard_data), default=0),
    })


@csrf_exempt
def moocs_scorecard_api(request):
    """API endpoint to get scorecard data as JSON."""
    verified = request.session.get("moocs_gmail_verified") is True
    email = request.session.get("moocs_gmail_email", "").strip().lower()

    if not verified or not email:
        return JsonResponse({"success": False, "error": "Authentication required"}, status=403)

    results = MoocsExamResult.objects.filter(email=email).order_by('set_number')

    scorecard_data = []
    for result in results:
        scorecard_data.append({
            'set_number': result.set_number,
            'score': result.score,
            'max_marks': result.max_marks,
            'correct': result.correct,
            'incorrect': result.incorrect,
            'unattempted': result.unattempted,
            'accuracy': result.accuracy,
            'total_questions': result.total_questions,
            'subject_scores': result.subject_scores,
            'completed_at': result.completed_at.isoformat() if result.completed_at else None,
        })

    return JsonResponse({
        "success": True,
        "email": email,
        "results": scorecard_data,
        "total_sets_completed": len(scorecard_data),
        "average_score": sum(r['score'] for r in scorecard_data) / len(scorecard_data) if scorecard_data else 0,
        "highest_score": max((r['score'] for r in scorecard_data), default=0),
    })
