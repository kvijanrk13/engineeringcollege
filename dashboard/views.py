from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import cloudinary.uploader

# ================= BASIC PAGES =================

def login_view(request):
    if request.method == "POST":
        if request.POST.get("username") == "7001" and request.POST.get("password") == "anrkitdept":
            request.session["logged_in"] = True
            return redirect("dashboard:dashboard")
        messages.error(request, "Invalid credentials")
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


# ================= CLOUDINARY PDF UPLOAD (FINAL & REQUIRED) =================

@csrf_exempt
def upload_generated_pdf(request):
    # 🔴 MANDATORY CHECK (WITHOUT THIS UPLOAD WILL FAIL)
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
    else:
        return JsonResponse({"error": "No PDF received"}, status=400)

    try:
        upload_result = cloudinary.uploader.upload(
            pdf_file,
            resource_type="raw",                 # ✅ REQUIRED FOR PDFs
            folder="faculty_pdfs",
            public_id=pdf_file.name.replace(".pdf", "")
        )

        return JsonResponse({
            "url": upload_result["secure_url"],
            "public_id": upload_result["public_id"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
