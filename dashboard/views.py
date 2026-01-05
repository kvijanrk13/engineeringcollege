from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import cloudinary.uploader


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Define valid credentials
        valid_users = {
            "7001": "Cutieminni@2",
            "5037": "anrkitdept",
            "7003": "anrkitdept",
            "7005": "anrkitdept",
            "7007": "anrkitdept",
            "7008": "anrkitdept",
            "7010": "anrkitdept",
            "7011": "anrkitdept",
            "3003": "anrkitdept",
        }

        # Check credentials
        if username in valid_users and valid_users[username] == password:
            request.session["logged_in"] = True
            request.session["user_id"] = username
            return redirect("dashboard:dashboard")
        else:
            return render(request, "dashboard/login.html", {"error": "Invalid Credentials"})

    return render(request, "dashboard/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("dashboard:login")


def dashboard(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


def faculty(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/faculty.html")


# ✅ REQUIRED TO FIX NO REVERSE MATCH ERROR
def syllabus(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/syllabus.html")


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


# 🔥 UPDATED FUNCTION (ONLY THIS IS CHANGED)
@csrf_exempt
def upload_generated_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        employee_code = request.POST.get("employee_code", "").strip()

        if not employee_code:
            return JsonResponse({"error": "Employee code missing"}, status=400)
    else:
        return JsonResponse({"error": "No PDF received"}, status=400)

    # 🔥 FORCE CLOUDINARY FILE NAME = EMPLOYEE CODE
    upload_result = cloudinary.uploader.upload(
        pdf_file,
        resource_type="raw",
        folder="faculty_pdfs",
        public_id=employee_code,
        overwrite=True,
        unique_filename=False
    )

    return JsonResponse({
        "status": "success",
        "url": upload_result["secure_url"],
        "public_id": upload_result["public_id"]
    })
