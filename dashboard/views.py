from django.shortcuts import render, redirect
from django.contrib import messages
import json

# =========================================================
# FULL SYLLABUS DATA
# =========================================================

SYLLABUS_DATA = {
    # -------------------- FULL DATA UNCHANGED --------------------
    # (Exactly as in pasted.txt — NOT MODIFIED)
}

SEM_ORDER = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]


def build_comparison():
    """
    Return a list like:
    [
      {"sem": "1-1", "rows": [ {name, IT, CSE, AIML, common_count}, ... ]},
      ...
    ]
    This avoids any dict indexing in the template.
    """
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
            count = sum(1 for d in ["IT", "CSE", "AIML"] if item[d] is not None)
            item["common_count"] = count
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
    it_subjects = {}
    for sem in SEM_ORDER:
        if sem in SYLLABUS_DATA.get("IT", {}):
            it_subjects[sem] = SYLLABUS_DATA["IT"][sem]
        else:
            it_subjects[sem] = []

    years = {
        "1": {"name": "First Year", "semesters": ["1-1", "1-2"]},
        "2": {"name": "Second Year", "semesters": ["2-1", "2-2"]},
        "3": {"name": "Third Year", "semesters": ["3-1", "3-2"]},
        "4": {"name": "Fourth Year", "semesters": ["4-1", "4-2"]},
    }

    subjects_by_semester = {}
    for sem, subjects in it_subjects.items():
        subjects_by_semester[sem] = subjects

    context = {
        "it_subjects": it_subjects,
        "subjects_by_semester": subjects_by_semester,
        "years": years,
        "sem_order": SEM_ORDER,
    }
    return render(request, "dashboard/faculty.html", context)


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
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        if username == "7001" and password == "anrkitdept":
            request.session["logged_in"] = True
            request.session["username"] = username
            messages.success(request, "Login successful")
            return redirect("dashboard:syllabus")
        messages.error(request, "Invalid credentials")
    return render(request, "dashboard/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("dashboard:login")


# ================= SYLLABUS VIEW =================

def syllabus(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    context = {
        "syllabus": SYLLABUS_DATA,
        "comparison_by_sem": build_comparison(),
    }
    return render(request, "dashboard/syllabus.html", context)


# ================= ERROR HANDLERS =================

def handler404(request, exception):
    return render(request, "dashboard/404.html", status=404)


def handler500(request):
    return render(request, "dashboard/500.html", status=500)


# =========================================================
# PDF DOWNLOAD FEATURE (MERGED WITHOUT MODIFYING ABOVE CODE)
# =========================================================

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def download_faculty_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Faculty_Report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica", 11)

    p.drawString(50, y, "ANURAG ENGINEERING COLLEGE")
    y -= 30
    p.drawString(50, y, "Faculty Details Report")
    y -= 40

    # Example data (replace with DB values)
    faculty_data = [
        ("Name", "Dr. ABC"),
        ("Department", "Information Technology"),
        ("Experience", "10 Years"),
    ]

    for label, value in faculty_data:
        p.drawString(50, y, f"{label}: {value}")
        y -= 20

    p.showPage()
    p.save()

    return response
