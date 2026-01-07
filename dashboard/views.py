from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import cloudinary.uploader


# --- AUTHENTICATION ---
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

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


# --- MAIN NAVIGATION PAGES ---
def dashboard(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


def faculty(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/faculty.html")


def syllabus(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/syllabus.html")


# --- PLACEHOLDER VIEWS FOR OTHER TABS ---
def students(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")  # Replace with students.html when ready


def exams(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")  # Replace with exams.html when ready


def laboratory(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")  # Replace with laboratory.html when ready


def gallery(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")  # Replace with gallery.html when ready


# --- PDF & CLOUDINARY UTILITIES ---
def download_faculty_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Faculty_Report.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    p.drawString(100, 750, "ANURAG ENGINEERING COLLEGE - Faculty Report")
    p.showPage()
    p.save()
    return response


@csrf_exempt
def upload_generated_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        employee_code = request.POST.get("employee_code", "").strip()
        if not employee_code:
            return JsonResponse({"error": "Employee code missing"}, status=400)

        upload_result = cloudinary.uploader.upload(
            pdf_file,
            resource_type="raw",
            folder="faculty_pdfs",
            public_id=employee_code,
            overwrite=True,
            unique_filename=False
        )
        return JsonResponse({"status": "success", "url": upload_result["secure_url"]})
    return JsonResponse({"error": "Invalid request"}, status=400)