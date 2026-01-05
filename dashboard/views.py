from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import cloudinary.uploader

# =========================================================
# SYLLABUS DATA (UNCHANGED)
# =========================================================

SYLLABUS_DATA = {
    # existing syllabus data
}

SEM_ORDER = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]


def build_comparison():
    comparison_by_sem = []
    for sem in SEM_ORDER:
        rows = []
        comparison_by_sem.append({"sem": sem, "rows": rows})
    return comparison_by_sem


# ================= BASIC VIEWS =================

def index(request):
    return render(request, "dashboard/index.html")


def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def about(request):
    return render(request, "dashboard/about.html")


def faculty(request):
    return render(request, "dashboard/faculty.html")


def students(request):
    return render(request, "dashboard/students.html")


def library(request):
    return render(request, "dashboard/library.html")


def exambranch(request):
    return render(request, "dashboard/exambranch.html")


def gallery(request):
    return render(request, "dashboard/gallery.html")


# ================= LOGIN =================

def login_view(request):
    if request.method == "POST":
        if (
            request.POST.get("username") == "7001"
            and request.POST.get("password") == "anrkitdept"
        ):
            request.session["logged_in"] = True
            return redirect("dashboard:dashboard")

        messages.error(request, "Invalid credentials")

    return render(request, "dashboard/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("dashboard:login")


# ================= SYLLABUS =================

def syllabus(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    return render(
        request,
        "dashboard/syllabus.html",
        {
            "syllabus": SYLLABUS_DATA,
            "comparison_by_sem": build_comparison(),
        },
    )


# ================= PDF DOWNLOAD =================

def download_faculty_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Faculty_Report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica", 11)
    p.drawString(50, 800, "ANURAG ENGINEERING COLLEGE")
    p.drawString(50, 770, "Faculty Details Report")
    p.showPage()
    p.save()

    return response


# ================= CLOUDINARY PDF UPLOAD (FIXED & SAFE) =================

@csrf_exempt
def upload_generated_pdf(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Only POST allowed"}, status=405)

        pdf = request.FILES.get("pdf")
        employee_code = request.POST.get("employee_code")

        if not pdf:
            return JsonResponse({"error": "PDF file not received"}, status=400)

        if not employee_code:
            return JsonResponse({"error": "Employee Code missing"}, status=400)

        # Upload to Cloudinary as RAW (required for PDFs)
        result = cloudinary.uploader.upload(
            pdf,
            resource_type="raw",
            public_id=f"faculty_pdfs/{employee_code}",
            overwrite=True,
        )

        return JsonResponse(
            {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
            }
        )

    except Exception as e:
        # IMPORTANT: This exposes the REAL error instead of silent 500
        return JsonResponse(
            {
                "error": "Cloudinary upload failed",
                "details": str(e),
            },
            status=500,
        )
