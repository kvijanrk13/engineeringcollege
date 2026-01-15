from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfWriter, PdfReader
import io
import os
import traceback
from datetime import datetime, date
from .models import StudentRegistration
import cloudinary.uploader
import cloudinary
import cloudinary.utils as cloudinary_utils
import requests
from PIL import Image as PILImage
from io import BytesIO
import tempfile
import html

# Add this after the other imports
try:
    from dashboard.utils.cloudinary_utils import download_certificate_with_auth

    print("✓ cloudinary_utils imported successfully")
except ImportError as e:
    print(f"⚠ Warning: Failed to import cloudinary_utils: {e}")


    def get_file_bytes(file):
        if not file:
            return None
        try:
            file.seek(0)
            return BytesIO(file.read())
        except Exception as e:
            print(f"Error reading file: {e}")
            return None


def upload_cert_to_cloudinary(file):
    if not file:
        return None
    try:
        result = cloudinary.uploader.upload(
            file,
            folder="certificates",
            resource_type="image",
            type="upload",
            overwrite=True,
            invalidate=True
        )
        return result["public_id"]
    except Exception as e:
        print(f"Error uploading certificate to Cloudinary: {e}")
        return None


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        valid_users = {
            "7001": "Cutieminni@2", "5037": "anrkitdept", "7003": "anrkitdept",
            "7005": "anrkitdept", "7007": "anrkitdept", "7008": "anrkitdept",
            "7010": "anrkitdept", "7011": "anrkitdept", "3003": "anrkitdept",
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


def dashboard(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    if request.session.get("user_id") == "anrkitstudent":
        return redirect("dashboard:students")
    total_students = StudentRegistration.objects.count()
    context = {'total_students': total_students}
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


def generate_student_pdf(student):
    """Generate PDF for student registration with photo - INCLUDES TASK AND CSI REGISTRATION"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75 * inch, leftMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=20,
                                 textColor=colors.HexColor('#006400'))
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=14, alignment=1,
                                    spaceAfter=15, textColor=colors.HexColor('#000080'))
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading3'], fontSize=12, alignment=1, spaceAfter=20,
                                  textColor=colors.HexColor('#8B0000'))
    address_style = ParagraphStyle('AddressStyle', parent=styles['Normal'], fontSize=11, leading=14,
                                   textColor=colors.black, wordWrap='CJK', spaceAfter=12, borderPadding=10,
                                   backColor=colors.white, borderColor=colors.black, borderWidth=1, borderRadius=3)

    photo_cell = Spacer(1, 1)
    if student.photo:
        try:
            photo_url = cloudinary.utils.cloudinary_url(student.photo, secure=True, sign_url=True)[0]
            response = requests.get(photo_url, timeout=10)
            if response.status_code == 200:
                img = PILImage.open(BytesIO(response.content)).convert("RGB")
                img.thumbnail((150, 180), PILImage.Resampling.LANCZOS)
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format="JPEG")
                img_byte_arr.seek(0)
                photo_cell = ReportLabImage(img_byte_arr, width=1.5 * inch, height=1.8 * inch)
        except Exception as e:
            print("Error processing photo:", e)

    header_table_data = [
        [Paragraph("ANURAG ENGINEERING COLLEGE", title_style), photo_cell],
        [Paragraph("INFORMATION TECHNOLOGY DEPARTMENT", subtitle_style), ""],
        [Paragraph("STUDENT REGISTRATION DETAILS", header_style), ""]
    ]
    header_table = Table(header_table_data, colWidths=[4 * inch, 2 * inch])
    header_table.setStyle(TableStyle(
        [('ALIGN', (0, 0), (0, -1), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
         ('SPAN', (1, 0), (1, 2))]))
    story.append(header_table)
    story.append(Spacer(1, 30))

    address_text = student.address or "ADDRESS NOT PROVIDED"
    address_para = Paragraph(f"<b>Address:</b><br/>{html.escape(address_text)}", address_style)

    if student.dob:
        if isinstance(student.dob, (date, datetime)):
            formatted_dob = student.dob.strftime('%d-%m-%Y')
        else:
            try:
                formatted_dob = datetime.strptime(str(student.dob), '%Y-%m-%d').strftime('%d-%m-%Y')
            except:
                formatted_dob = str(student.dob)
    else:
        formatted_dob = "N/A"

    student_data = [
        ["Hall Ticket Number:", student.ht_no or "N/A", "Student Name:", student.student_name or "N/A"],
        ["Father Name:", student.father_name or "N/A", "Mother Name:", student.mother_name or "N/A"],
        ["Gender:", student.gender or "N/A", "Date of Birth:", formatted_dob],
        ["Age:", str(student.age) if student.age else "N/A", "Nationality:", student.nationality or "N/A"],
        ["Category:", student.category or "N/A", "Religion:", student.religion or "N/A"],
        ["Blood Group:", student.blood_group or "N/A", "APAAR ID:", student.apaar_id or "N/A"],
        ["Aadhar Number:", student.aadhar or "N/A", "EAMCET Rank:",
         str(student.eamcet_rank) if student.eamcet_rank else "N/A"],
        ["TASK Registered:", student.task_registered or "N/A", "TASK Username:",
         student.task_username if student.task_registered == "Yes" else "N/A"],
        ["CSI Registered:", student.csi_registered or "N/A", "CSI Membership ID:",
         student.csi_membership_id if student.csi_registered == "Yes" else "N/A"],
        ["Parent Phone:", student.parent_phone or "N/A", "Student Phone:", student.student_phone or "N/A"],
        ["Email:", student.email or "N/A", "Admission Type:", student.admission_type or "N/A"],
        ["Year:", str(student.year) if student.year else "N/A", "Semester:",
         str(student.sem) if student.sem else "N/A"],
    ]

    if student.other_admission_details:
        student_data.append(["Admission Details:", student.other_admission_details, "", ""])

    student_table = Table(student_data, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("ADDRESS DETAILS", header_style))
    story.append(Spacer(1, 10))
    address_table = Table([["Address:", address_para]], colWidths=[1.5 * inch, 5.5 * inch])
    address_table.setStyle(TableStyle(
        [('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E8E8E8')), ('GRID', (0, 0), (-1, -1), 1, colors.black),
         ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
         ('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 10),
         ('BACKGROUND', (1, 0), (1, 0), colors.white)]))
    story.append(address_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("ACADEMIC PERFORMANCE", header_style))
    academic_data = [
        ["SSC Marks (%)", str(student.ssc_marks) if student.ssc_marks else "N/A"],
        ["Inter Marks (%)", str(student.inter_marks) if student.inter_marks else "N/A"],
        ["Current CGPA", str(student.cgpa) if student.cgpa else "N/A"],
        ["RTRP Project Title", student.rtrp_title or "N/A"],
        ["Internship Title", student.intern_title or "N/A"],
        ["Final Project Title", student.final_project_title or "N/A"],
    ]
    academic_table = Table(academic_data, colWidths=[2.5 * inch, 4 * inch])
    academic_table.setStyle(TableStyle(
        [('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')), ('GRID', (0, 0), (-1, -1), 1, colors.black),
         ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
         ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold')]))
    story.append(academic_table)
    story.append(Spacer(1, 20))

    if student.other_training:
        story.append(Spacer(1, 10))
        story.append(Paragraph(student.other_training, styles['Normal']))
        story.append(Spacer(1, 20))

    story.append(Spacer(1, 40))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                           ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=1)))
    story.append(Paragraph("This is an official document of ANURAG Engineering College",
                           ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=1)))

    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        traceback.print_exc()
        return generate_simple_pdf(student)


def generate_simple_pdf(student):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "ANURAG ENGINEERING COLLEGE")
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, f"HT No: {student.ht_no}")
    p.drawString(100, 680, f"Name: {student.student_name}")
    p.save()
    buffer.seek(0)
    return buffer


def image_to_pdf(image_bytes):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    img = PILImage.open(BytesIO(image_bytes))
    img.thumbnail((500, 700), PILImage.Resampling.LANCZOS)
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    c.drawImage(img_buffer, 50, 100, width=500, height=700)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def merge_student_certificates(student, main_pdf_buffer, certificate_files):
    writer = PdfWriter()
    main_pdf_buffer.seek(0)
    reader = PdfReader(main_pdf_buffer)
    for page in reader.pages:
        writer.add_page(page)
    successful_merges = 0
    for field_name, file in certificate_files.items():
        if not file: continue
        try:
            file.seek(0)
            pdf_content = BytesIO(file.read())
            try:
                pdf_content.seek(0)
                cert_reader = PdfReader(pdf_content)
                for page in cert_reader.pages: writer.add_page(page)
                successful_merges += 1
            except:
                pdf_content.seek(0)
                img_bytes = pdf_content.read()
                if img_bytes:
                    img_pdf = image_to_pdf(img_bytes)
                    img_reader = PdfReader(img_pdf)
                    for page in img_reader.pages: writer.add_page(page)
                    successful_merges += 1
        except Exception as e:
            print(f"Merge error for {field_name}: {e}")
    final_buffer = BytesIO()
    writer.write(final_buffer)
    final_buffer.seek(0)
    return final_buffer


def students(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    if request.method == "POST":
        try:
            if 'photo' not in request.FILES:
                messages.error(request, 'Please upload a student photo. PDF generation cannot proceed without a photo.')
                return render(request, "dashboard/students.html")

            ht_no = request.POST.get('ht_no', '').strip().upper()
            student_name = request.POST.get('student_name', '').strip()
            parent_phone = request.POST.get('parent_phone', '').strip()
            student_phone = request.POST.get('student_phone', '').strip()
            if parent_phone == student_phone:
                messages.error(request, 'Parent Phone Number and Student Phone Number cannot be the same!')
                return render(request, "dashboard/students.html")
            if StudentRegistration.objects.filter(ht_no=ht_no).exists():
                messages.error(request, f'Student with Hall Ticket No {ht_no} already exists!')
                return render(request, "dashboard/students.html")
            dob_str = request.POST.get('dob', '')
            dob = None
            if dob_str:
                try:
                    day, month, year = map(int, dob_str.split('-'))
                    dob = f"{year:04d}-{month:02d}-{day:02d}"
                except:
                    messages.error(request, 'Invalid date format. Use DD-MM-YYYY.')
                    return render(request, "dashboard/students.html")

            task_reg = request.POST.get('task_registered', '').strip()
            task_user = request.POST.get('task_username', '').strip()
            csi_reg = request.POST.get('csi_registered', '').strip()
            csi_id = request.POST.get('csi_membership_id', '').strip()

            student = StudentRegistration(
                ht_no=ht_no, student_name=student_name,
                father_name=request.POST.get('father_name', '').strip(),
                mother_name=request.POST.get('mother_name', '').strip(),
                gender=request.POST.get('gender', ''), dob=dob,
                age=int(request.POST.get('age', 0)) if request.POST.get('age') else 0,
                nationality=request.POST.get('nationality', 'Indian'),
                category=request.POST.get('category', ''), religion=request.POST.get('religion', ''),
                blood_group=request.POST.get('blood_group', ''), apaar_id=request.POST.get('apaar_id', '').strip(),
                aadhar=request.POST.get('aadhar', '').strip(), address=request.POST.get('address', '').strip(),
                task_registered=task_reg, task_username=task_user if task_reg == "Yes" else '',
                csi_registered=csi_reg, csi_membership_id=csi_id if csi_reg == "Yes" else '',
                parent_phone=parent_phone, student_phone=student_phone, email=request.POST.get('email', '').strip(),
                admission_type=request.POST.get('admission_type', ''),
                eamcet_rank=request.POST.get('eamcet_rank') or None,
                year=int(request.POST.get('year', 1)), sem=int(request.POST.get('sem', 1)),
                ssc_marks=float(request.POST.get('ssc_marks', 0)) if request.POST.get('ssc_marks') else None,
                inter_marks=float(request.POST.get('inter_marks', 0)) if request.POST.get('inter_marks') else None,
                cgpa=float(request.POST.get('cgpa', 0)) if request.POST.get('cgpa') else None,
                rtrp_title=request.POST.get('rtrp_title', ''), intern_title=request.POST.get('intern_title', ''),
                final_project_title=request.POST.get('final_project_title', ''),
                other_training=request.POST.get('other_training', '')
            )

            # Upload photo
            upload_result = cloudinary.uploader.upload(
                request.FILES['photo'],
                folder="student_photos",
                public_id=f"{ht_no}",
                overwrite=True,
                access_mode="public"
            )
            student.photo = upload_result["public_id"]

            student.save()

            certificate_files = {k: request.FILES.get(k) for k in
                                 ['cert_achieve', 'cert_intern', 'cert_courses', 'cert_sdp', 'cert_extra',
                                  'cert_placement', 'cert_national']}
            base_pdf = generate_student_pdf(student)
            pdf_buffer = merge_student_certificates(student, base_pdf, certificate_files)

            upload_result = cloudinary.uploader.upload(ContentFile(pdf_buffer.read()), resource_type="raw",
                                                       folder="student_pdfs", public_id=f"student_{ht_no}",
                                                       overwrite=True, access_mode="public")
            student.pdf_url = upload_result["secure_url"]
            student.save()
            request.session['student_id'] = student.id
            messages.success(request, 'Registration Successful!')
            return redirect('dashboard:view_pdf', student_id=student.id)
        except Exception as e:
            traceback.print_exc()
            messages.error(request, f'Error: {str(e)}')
    return render(request, "dashboard/students.html")


def view_pdf(request, student_id):
    student = get_object_or_404(StudentRegistration, id=student_id)
    if student.pdf_url: return redirect(student.pdf_url)
    return redirect("dashboard:students")


def download_pdf(request, student_id):
    student = get_object_or_404(StudentRegistration, id=student_id)
    if student.pdf_url: return redirect(student.pdf_url)
    return redirect("dashboard:students")


def students_data(request):
    if not request.session.get("logged_in") or request.session.get("user_id") != "7001":
        messages.error(request, "Unauthorized access!")
        return redirect("dashboard:dashboard")

    if not request.session.get("portal_verified"):
        if request.method == "POST":
            secondary_pass = request.POST.get("portal_password")
            if secondary_pass == "Cutieminni@2":
                request.session["portal_verified"] = True
            else:
                messages.error(request, "Incorrect Portal Password!")
                return redirect("dashboard:dashboard")
        else:
            return redirect("dashboard:dashboard")

    students = StudentRegistration.objects.all().order_by('-registration_date')
    male_count = students.filter(gender='Male').count()
    female_count = students.filter(gender='Female').count()

    return render(request, "dashboard/students_data.html", {
        'students': students,
        'total_students': students.count(),
        'male_count': male_count,
        'female_count': female_count,
        'is_admin': True
    })


def delete_student(request, student_id):
    if request.session.get("user_id") == "7001":
        get_object_or_404(StudentRegistration, id=student_id).delete()
    return redirect('dashboard:students_data')


def exambranch(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


def laboratory(request):
    if not request.session.get("logged_in"):
        return redirect("dashboard:login")
    return render(request, "dashboard/dashboard.html")


def library(request):
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
        res = cloudinary.uploader.upload(request.FILES["pdf"], resource_type="raw", folder="faculty_pdfs",
                                         public_id=request.POST.get("employee_code", ""), overwrite=True,
                                         access_mode="public")
        return JsonResponse({"status": "success", "url": res["secure_url"]})
    return JsonResponse({"error": "Invalid request"}, status=400)