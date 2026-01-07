from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from io import BytesIO
import os
import traceback
from datetime import datetime
from .models import StudentRegistration
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
            "anrkitstudent": "anrkitstudent",
        }

        if username in valid_users and valid_users[username] == password:
            request.session["logged_in"] = True
            request.session["user_id"] = username
            request.session["is_faculty"] = username != "anrkitstudent"

            if username == "anrkitstudent":
                return redirect("dashboard:students")
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

    if request.session.get("user_id") == "anrkitstudent":
        return redirect("dashboard:students")

    total_students = StudentRegistration.objects.count()

    context = {
        'total_students': total_students,
    }
    return render(request, "dashboard/dashboard.html", context)


def faculty(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    if request.session.get("user_id") == "anrkitstudent":
        return redirect("dashboard:students")

    return render(request, "dashboard/faculty.html")


def syllabus(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    if request.session.get("user_id") == "anrkitstudent":
        return redirect("dashboard:students")

    return render(request, "dashboard/syllabus.html")


# --- STUDENT REGISTRATION & PDF GENERATION ---
def generate_student_pdf(student):
    """Generate PDF for student registration"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1,
        spaceAfter=30
    )
    story.append(Paragraph("ANURAG ENGINEERING COLLEGE", title_style))
    story.append(Paragraph("INFORMATION TECHNOLOGY DEPARTMENT", styles['Heading2']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("STUDENT REGISTRATION DETAILS", styles['Heading3']))
    story.append(Spacer(1, 30))

    student_data = [
        ["Hall Ticket Number:", student.ht_no or "N/A", "Student Name:", student.student_name or "N/A"],
        ["Father Name:", student.father_name or "N/A", "Mother Name:", student.mother_name or "N/A"],
        ["Gender:", student.gender or "N/A", "Date of Birth:", str(student.dob) if student.dob else "N/A"],
        ["Age:", str(student.age) if student.age else "N/A", "Nationality:", student.nationality or "N/A"],
        ["Category:", student.category or "N/A", "Religion:", student.religion or "N/A"],
        ["Blood Group:", student.blood_group or "N/A", "Aadhar Number:", student.aadhar or "N/A"],
        ["Address:", student.address or "N/A", "", ""],
        ["Parent Phone:", student.parent_phone or "N/A", "Student Phone:", student.student_phone or "N/A"],
        ["Email:", student.email or "N/A", "Admission Type:", student.admission_type or "N/A"],
        ["Year:", str(student.year) if student.year else "N/A", "Semester:",
         str(student.sem) if student.sem else "N/A"],
    ]

    if student.other_admission_details:
        student_data.append(["Admission Details:", student.other_admission_details, "", ""])

    student_table = Table(student_data, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(student_table)
    story.append(Spacer(1, 20))

    academic_data = [
        ["SSC Marks (%)", str(student.ssc_marks) if student.ssc_marks else "N/A"],
        ["Inter Marks (%)", str(student.inter_marks) if student.inter_marks else "N/A"],
        ["Current CGPA", str(student.cgpa) if student.cgpa else "N/A"],
        ["RTRP Project Title", student.rtrp_title if student.rtrp_title else "N/A"],
        ["Internship Title", student.intern_title if student.intern_title else "N/A"],
        ["Final Project Title", student.final_project_title if student.final_project_title else "N/A"],
    ]

    academic_table = Table(academic_data, colWidths=[2.5 * inch, 4 * inch])
    academic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(academic_table)
    story.append(Spacer(1, 20))

    if student.other_training:
        story.append(Paragraph("ADDITIONAL TRAINING", styles['Heading4']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(student.other_training, styles['Normal']))
        story.append(Spacer(1, 20))

    story.append(Spacer(1, 40))
    story.append(Paragraph("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles['Normal']))
    story.append(Paragraph("This is an official document of ANURAG Engineering College", styles['Normal']))

    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"PDF generation error: {e}")
        return generate_simple_pdf(student)


def generate_simple_pdf(student):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "ANURAG ENGINEERING COLLEGE")
    p.setFont("Helvetica", 14)
    p.drawString(100, 730, "INFORMATION TECHNOLOGY DEPARTMENT")
    p.drawString(100, 710, "STUDENT REGISTRATION")
    p.setFont("Helvetica", 12)
    p.drawString(100, 680, f"Hall Ticket No: {student.ht_no}")
    p.drawString(100, 660, f"Student Name: {student.student_name}")
    p.drawString(100, 640, f"Father Name: {student.father_name}")
    p.drawString(100, 620, f"Mother Name: {student.mother_name}")
    p.drawString(100, 600, f"Gender: {student.gender}")
    p.drawString(100, 580, f"Date of Birth: {student.dob}")
    p.drawString(100, 560, f"Age: {student.age}")
    p.drawString(100, 540, f"Email: {student.email}")
    p.drawString(100, 520, f"Phone: {student.student_phone}")
    p.drawString(100, 500, f"Year: {student.year}, Sem: {student.sem}")
    p.drawString(100, 480, f"Registration Date: {student.registration_date.strftime('%Y-%m-%d')}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def students(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    if request.method == "POST":
        try:
            ht_no = request.POST.get('ht_no', '').strip()
            student_name = request.POST.get('student_name', '').strip()

            if StudentRegistration.objects.filter(ht_no=ht_no).exists():
                messages.error(request, f'Student with Hall Ticket No {ht_no} already exists!')
                return render(request, "dashboard/students.html")

            student = StudentRegistration(
                ht_no=ht_no,
                student_name=student_name,
                father_name=request.POST.get('father_name', '').strip(),
                mother_name=request.POST.get('mother_name', '').strip(),
                gender=request.POST.get('gender', ''),
                dob=request.POST.get('dob'),
                age=int(request.POST.get('age', 0)) if request.POST.get('age') else 0,
                nationality=request.POST.get('nationality', 'Indian'),
                category=request.POST.get('category', ''),
                religion=request.POST.get('religion', ''),
                blood_group=request.POST.get('blood_group', ''),
                aadhar=request.POST.get('aadhar', '').strip(),
                address=request.POST.get('address', ''),
                parent_phone=request.POST.get('parent_phone', '').strip(),
                student_phone=request.POST.get('student_phone', '').strip(),
                email=request.POST.get('email', '').strip(),
                admission_type=request.POST.get('admission_type', ''),
                other_admission_details=request.POST.get('other_admission_details', ''),
                year=int(request.POST.get('year', 1)) if request.POST.get('year') else 1,
                sem=int(request.POST.get('sem', 1)) if request.POST.get('sem') else 1,
                ssc_marks=float(request.POST.get('ssc_marks')) if request.POST.get('ssc_marks') else None,
                inter_marks=float(request.POST.get('inter_marks')) if request.POST.get('inter_marks') else None,
                cgpa=float(request.POST.get('cgpa')) if request.POST.get('cgpa') else None,
                rtrp_title=request.POST.get('rtrp_title', ''),
                intern_title=request.POST.get('intern_title', ''),
                final_project_title=request.POST.get('final_project_title', ''),
                photo=request.FILES.get('photo'),
                cert_achieve=request.FILES.get('cert_achieve'),
                cert_intern=request.FILES.get('cert_intern'),
                cert_courses=request.FILES.get('cert_courses'),
                cert_sdp=request.FILES.get('cert_sdp'),
                cert_extra=request.FILES.get('cert_extra'),
                cert_placement=request.FILES.get('cert_placement'),
                cert_national=request.FILES.get('cert_national'),
                other_training=request.POST.get('other_training', '')
            )

            student.save()

            try:
                pdf_buffer = generate_student_pdf(student)
                pdf_filename = student.get_pdf_filename()

                # ---------- CLOUDINARY PUBLIC PDF UPLOAD (FIX) ----------
                pdf_buffer.seek(0)
                pdf_content = pdf_buffer.read()
                content_file = ContentFile(pdf_content)

                upload_result = cloudinary.uploader.upload(
                    content_file,
                    resource_type="raw",
                    folder="student_pdfs",
                    public_id=pdf_filename.replace(".pdf", ""),
                    access_mode="public",
                    overwrite=True,
                )
                student.pdf_url = upload_result["secure_url"]
                student.save()
                # -------------------------------------------------------

                request.session['student_id'] = student.id
                request.session['last_ht_no'] = student.ht_no

                messages.success(request, f'Registration submitted successfully! PDF generated.')
                return redirect('dashboard:view_pdf', student_id=student.id)

            except Exception as pdf_error:
                student.save()
                request.session['student_id'] = student.id
                messages.warning(request, f'Registration saved but PDF generation failed.')
                return redirect('dashboard:students')

        except Exception as e:
            traceback.print_exc()
            messages.error(request, f'Error submitting form: {str(e)}')

    return render(request, "dashboard/students.html")


def view_pdf(request, student_id):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    try:
        student = get_object_or_404(StudentRegistration, id=student_id)

        if request.session.get("user_id") == "anrkitstudent":
            session_student_id = request.session.get('student_id')
            if session_student_id != student_id:
                messages.error(request, 'You can only view your own PDF')
                return redirect('dashboard:students')

        if student.pdf_url:
            return redirect(student.pdf_url)
        else:
            messages.error(request, "PDF not available")
            return redirect("dashboard:students")

    except Exception as e:
        messages.error(request, f'Error viewing PDF: {str(e)}')
        return redirect('dashboard:students')


def download_pdf(request, student_id):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    try:
        student = get_object_or_404(StudentRegistration, id=student_id)

        if request.session.get("user_id") == "anrkitstudent":
            session_student_id = request.session.get('student_id')
            if session_student_id != student_id:
                messages.error(request, 'You can only download your own PDF')
                return redirect('dashboard:students')

        if student.pdf_url:
            response = redirect(student.pdf_url)
            response["Content-Disposition"] = f'attachment; filename="{student.get_pdf_filename()}"'
            return response
        else:
            messages.error(request, "PDF not available for download")
            return redirect("dashboard:students")

    except Exception as e:
        messages.error(request, f'Error downloading PDF: {str(e)}')
        return redirect('dashboard:students')


def students_data(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    if request.session.get("user_id") == "anrkitstudent":
        return redirect("dashboard:students")

    students = StudentRegistration.objects.all().order_by('-registration_date')

    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            ht_no__icontains=search_query
        ) | students.filter(
            student_name__icontains=search_query
        ) | students.filter(
            email__icontains=search_query
        )

    total_students = students.count()
    male_count = students.filter(gender='Male').count()
    female_count = students.filter(gender='Female').count()

    is_admin = request.session.get("user_id") == "7001"

    context = {
        'students': students,
        'search_query': search_query,
        'total_students': total_students,
        'male_count': male_count,
        'female_count': female_count,
        'is_admin': is_admin,
    }
    return render(request, "dashboard/students_data.html", context)


def delete_student(request, student_id):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")

    if request.session.get("user_id") != "7001":
        messages.error(request, 'You do not have permission to delete student data.')
        return redirect('dashboard:students_data')

    try:
        student = get_object_or_404(StudentRegistration, id=student_id)
        student_name = student.student_name
        ht_no = student.ht_no
        student.delete()
        messages.success(request, f'Student {student_name} (HT No: {ht_no}) deleted.')

    except Exception as e:
        messages.error(request, f'Error deleting student: {str(e)}')

    return redirect('dashboard:students_data')


def exambranch(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


def laboratory(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


def gallery(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


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
            unique_filename=False,
            access_mode="public"
        )
        return JsonResponse({"status": "success", "url": upload_result["secure_url"]})
    return JsonResponse({"error": "Invalid request"}, status=400)