from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import cloudinary.uploader
import json

# =========================================================
# FULL SYLLABUS DATA
# =========================================================

SYLLABUS_DATA = {
    # YOUR EXISTING SYLLABUS DATA (UNCHANGED)
}

SEM_ORDER = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]


def build_comparison():
    comparison_by_sem = []
    for sem in SEM_ORDER:
        mapping = {}
        for dept in ["IT", "CSE", "AIML"]:
            for subj in SYLLABUS_DATA.get(dept, {}).get(sem, []):
                key = subj["name"].strip().upper()
                if key not in mapping:
                    mapping[key] = {
                        "name": subj["name"],
                        "IT": None,
                        "CSE": None,
                        "AIML": None,
                    }
                mapping[key][dept] = {"code": subj["code"], "name": subj["name"]}

        rows = []
        for item in mapping.values():
            item["common_count"] = sum(
                1 for d in ["IT", "CSE", "AIML"] if item[d] is not None
            )
            rows.append(item)

        rows.sort(key=lambda x: (-x["common_count"], x["name"]))
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
    return render(request, "dashboard/faculty.html", {"sem_order": SEM_ORDER})


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
    y = A4[1] - 50
    p.setFont("Helvetica", 11)

    p.drawString(50, y, "ANURAG ENGINEERING COLLEGE")
    y -= 30
    p.drawString(50, y, "Faculty Details Report")

    p.showPage()
    p.save()
    return response


# ================= CLOUDINARY PDF UPLOAD =================
# PDF WILL BE SAVED AS EmployeeId.pdf

@csrf_exempt
def upload_generated_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]

        # Employee ID comes as filename (EmployeeId.pdf)
        employee_id = pdf_file.name.replace(".pdf", "").strip()

        result = cloudinary.uploader.upload(
            pdf_file,
            resource_type="raw",
            folder="faculty_pdfs",
            public_id=employee_id,   # 👈 EmployeeId as filename
            overwrite=True           # 👈 Replace if already exists
        )

        return JsonResponse({
            "employee_id": employee_id,
            "url": result["secure_url"]
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
