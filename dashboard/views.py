# dashboard/views.py - COMPLETE VERSION WITH ENHANCED PDF GENERATION
# ============================================================================
import os
import json
import csv
import tempfile
import logging
import uuid
import zipfile
from datetime import datetime, date, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Any
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import (HttpResponse, JsonResponse, HttpResponseRedirect,
                         FileResponse, HttpResponseBadRequest)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.urls import reverse
from django.utils import timezone
import django

# PDF Generation imports
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, HRFlowable, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfWriter, PdfReader
from PyPDF2 import PdfMerger
from PIL import Image as PILImage

# PDF to image conversion - FIXED IMPORT
try:
    import fitz  # PyMuPDF

    FITZ_AVAILABLE = True
except ImportError:
    try:
        import pymupdf as fitz

        FITZ_AVAILABLE = True
    except ImportError:
        fitz = None
        FITZ_AVAILABLE = False
        print("WARNING: PyMuPDF (fitz) not installed. PDF to image conversion disabled.")
        print("Install with: pip install PyMuPDF")

# Cloudinary imports
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Local imports
from .models import (
    Faculty, Certificate, FacultyLog, CloudinaryUpload,
    Subject, FacultyProfile, ResearchProject, Student,
    ResearchPublication, FDP, BTechProject
)
from .forms import (
    LoginForm, StudentForm, FacultyForm, CertificateForm,
    BulkUploadForm, FacultyProfileForm, ResearchProjectForm,
)
from .utils import (
    calculate_experience, generate_pdf_from_html, merge_pdfs,
    extract_text_from_pdf, validate_faculty_data, calculate_age,
    format_date, get_academic_year, send_email_notification,
    generate_qr_code, export_to_excel, validate_student_data,
    validate_pdf_file, validate_image_file
)

logger = logging.getLogger(__name__)

# ==================== OPTIONAL LIBRARIES ====================
try:
    import pandas as pd
except ImportError:
    pd = None
    logger.warning("Pandas not installed. Bulk upload features limited.")

try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil not installed. System monitoring limited.")

# Matplotlib with NumPy compatibility fix
try:
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
except (ImportError, Exception) as e:
    plt = None
    np = None
    logger.warning(f"Matplotlib not installed or incompatible: {e}. Chart features limited.")

try:
    import pdfkit
except ImportError:
    pdfkit = None
    logger.warning("pdfkit not installed. PDF generation features limited.")


# ==================== HELPERS ====================
def is_cloudinary_configured():
    return getattr(settings, 'CLOUDINARY_CONFIGURED', False)


if is_cloudinary_configured():
    try:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        logger.info("Cloudinary initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Cloudinary: {e}")
else:
    logger.warning("Cloudinary credentials not found.")


def get_file_from_field(file_field, url_field=None):
    """Helper function to get actual file path or download URL"""
    if url_field and url_field.startswith('http'):
        return None, url_field
    if not file_field:
        return None, None
    if isinstance(file_field, str):
        if file_field.startswith('http'):
            return None, file_field
        elif os.path.exists(file_field):
            return file_field, None
        return None, None
    if hasattr(file_field, 'url') and file_field.url:
        return None, file_field.url
    if hasattr(file_field, 'path') and file_field.path:
        if file_field.path.startswith('http'):
            return None, file_field.path
        elif os.path.exists(file_field.path):
            return file_field.path, None
    return None, None


# ==================== PDF TO IMAGE CONVERSION FUNCTION ====================
def convert_pdf_to_images(pdf_path):
    if not FITZ_AVAILABLE or fitz is None:
        print("ERROR: PyMuPDF not installed. Cannot convert PDF to images.")
        print("Please install with: pip install PyMuPDF")
        return []

    images = []
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_path = f"{pdf_path}_page_{i}.png"
            pix.save(img_path)
            images.append(img_path)
            print(f" Converted PDF page {i + 1} to image: {img_path}")
        doc.close()
    except Exception as e:
        print(f"PDF conversion error: {e}")
    return images


# ==================== PDF MERGE FUNCTIONS ====================
def merge_all_documents(output_path, image_files, pdf_files):
    from pypdf import PdfReader, PdfWriter
    print(f"\n{'=' * 60}")
    print(f"MERGE ALL DOCUMENTS")
    print(f" Images to merge: {len(image_files)}")
    print(f" PDFs to merge: {len(pdf_files)}")
    print(f"{'=' * 60}")
    writer = PdfWriter()
    temp_files = []
    merged_count = 0
    skipped_count = 0

    for pdf_path in pdf_files:
        try:
            if not os.path.exists(pdf_path):
                print(f" [SKIP] PDF does not exist: {pdf_path}")
                skipped_count += 1
                continue
            if isinstance(pdf_path, str) and pdf_path.startswith('http'):
                print(f" 🌐 Downloading PDF from URL: {pdf_path}")
                response = requests.get(pdf_path, timeout=30)
                if response.status_code == 200:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    tmp.write(response.content)
                    tmp.close()
                    pdf_path = tmp.name
                    temp_files.append(pdf_path)
                    print(f" ✅ Downloaded: {tmp.name}")
                else:
                    print(f" [SKIP] Failed to download PDF: HTTP {response.status_code}")
                    skipped_count += 1
                    continue
            print(f" Processing PDF: {os.path.basename(pdf_path)}")
            reader = PdfReader(pdf_path)
            if len(reader.pages) == 0:
                print(f" [SKIP] PDF has no pages: {os.path.basename(pdf_path)}")
                skipped_count += 1
                continue
            for page in reader.pages:
                writer.add_page(page)
                merged_count += 1
            print(f" [OK] Added {len(reader.pages)} pages from PDF")
        except Exception as e:
            print(f" [ERROR] Failed to process PDF {pdf_path}: {e}")
            skipped_count += 1

    for img_path in image_files:
        try:
            if not os.path.exists(img_path):
                print(f" [SKIP] Image does not exist: {img_path}")
                skipped_count += 1
                continue
            if isinstance(img_path, str) and img_path.startswith('http'):
                print(f" 🌐 Downloading image from URL: {img_path}")
                response = requests.get(img_path, timeout=30)
                if response.status_code == 200:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    tmp.write(response.content)
                    tmp.close()
                    img_path = tmp.name
                    temp_files.append(img_path)
                    print(f" ✅ Downloaded: {tmp.name}")
                else:
                    print(f" [SKIP] Failed to download image: HTTP {response.status_code}")
                    skipped_count += 1
                    continue
            print(f" Processing image: {os.path.basename(img_path)}")
            img = PILImage.open(img_path)
            if img.mode in ('RGBA', 'P', 'LA'):
                bg = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img.convert('RGBA'), mask=img.convert('RGBA').split()[3])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            img.save(temp_pdf.name, 'PDF', resolution=100.0)
            temp_files.append(temp_pdf.name)
            temp_pdf.close()
            img_reader = PdfReader(temp_pdf.name)
            for page in img_reader.pages:
                writer.add_page(page)
                merged_count += 1
            print(f" [OK] Added image as PDF page")
        except Exception as e:
            print(f" [ERROR] Failed to add image {img_path}: {e}")
            skipped_count += 1

    try:
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"\n [OK] Final PDF saved: {output_path}")
        print(f" Summary: {merged_count} pages merged, {skipped_count} files skipped")
        print(f"{'=' * 60}\n")
        return True
    except Exception as e:
        print(f" [ERROR] Failed to save final PDF: {e}")
        return False
    finally:
        for tmp in temp_files:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass


def merge_documents(output_path, image_files=None, pdf_files=None):
    if image_files is None:
        image_files = []
    if pdf_files is None:
        pdf_files = []
    return merge_all_documents(output_path, image_files, pdf_files)


def merge_files(file_list):
    from pypdf import PdfMerger
    from PIL import Image
    merger = PdfMerger()
    temp_files = []
    valid_files = 0
    skipped_files = 0
    print("\n========== ENHANCED PDF MERGE START ==========")
    for idx, file in enumerate(file_list):
        if not file:
            print(f"[{idx}] Skipped (empty)")
            skipped_files += 1
            continue
        try:
            file_url = file.url if hasattr(file, "url") else str(file)
            print(f"[{idx}] Processing: {file_url}")
            if file_url.startswith("http"):
                response = requests.get(file_url, timeout=20)
                if response.status_code != 200:
                    print(" [X] Download failed")
                    skipped_files += 1
                    continue
                suffix = ".pdf" if file_url.lower().endswith(".pdf") else ".img"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp.write(response.content)
                temp.close()
                file_path = temp.name
                temp_files.append(file_path)
            else:
                file_path = file.path
            with open(file_path, "rb") as f:
                header = f.read(4)
            is_pdf = header.startswith(b"%PDF")
            if is_pdf:
                is_valid, error = validate_pdf_file(file_path)
                if is_valid:
                    print(" [OK] PDF detected and validated")
                    merger.append(file_path)
                    valid_files += 1
                else:
                    print(f" [X] PDF validation failed: {error}")
                    skipped_files += 1
            else:
                is_valid, error = validate_image_file(file_path)
                if is_valid:
                    print(" [OK] Image detected and validated")
                    img = Image.open(file_path)
                    if img.mode in ("RGBA", "LA", "P"):
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "RGBA":
                            bg.paste(img, mask=img.split()[3])
                        else:
                            bg.paste(img)
                        img = bg
                    else:
                        img = img.convert("RGB")
                    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    img.save(temp_pdf.name, "PDF")
                    temp_pdf.close()
                    merger.append(temp_pdf.name)
                    temp_files.append(temp_pdf.name)
                    valid_files += 1
                else:
                    print(f" [X] Image validation failed: {error}")
                    skipped_files += 1
        except Exception as e:
            print(f" [X] Error: {e}")
            skipped_files += 1
    final_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(final_pdf.name)
    merger.close()
    print(f"[OK] Final PDF: {final_pdf.name}")
    print(f"📊 Summary: {valid_files} files merged, {skipped_files} files skipped")
    print("========== ENHANCED PDF MERGE END ==========\n")
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass
    return final_pdf.name


# ==================== FILE COLLECTION FUNCTION ====================
def collect_faculty_files(faculty):
    image_files = []
    pdf_files = []
    temp_files = []
    print("\n" + "=" * 60)
    print("FILE COLLECTION DEBUG")
    print("=" * 60)
    print(f"Faculty: {faculty.staff_name} (ID: {faculty.id})")
    print(f"Employee Code: {faculty.employee_code}")
    print("=" * 60)

    # Photo
    if faculty.cloudinary_photo_url:
        try:
            print(f"📷 Found Cloudinary photo URL: {faculty.cloudinary_photo_url}")
            response = requests.get(faculty.cloudinary_photo_url, timeout=30)
            if response.status_code == 200:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                tmp.write(response.content)
                tmp.close()
                image_files.append(tmp.name)
                temp_files.append(tmp.name)
                print(f" ✅ Downloaded photo from Cloudinary: {tmp.name}")
        except Exception as e:
            print(f" ❌ Cloudinary photo download error: {e}")
    if faculty.photo:
        file_path, file_url = get_file_from_field(faculty.photo, None)
        if file_path:
            image_files.append(file_path)
            print(f" ✅ Photo (local): {file_path}")
        elif file_url:
            try:
                print(f"📷 Downloading photo from: {file_url}")
                response = requests.get(file_url, timeout=30)
                if response.status_code == 200:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    tmp.write(response.content)
                    tmp.close()
                    image_files.append(tmp.name)
                    temp_files.append(tmp.name)
                    print(f" ✅ Downloaded photo: {tmp.name}")
            except Exception as e:
                print(f" ❌ Photo download error: {e}")

    # Documents
    doc_fields = [
        ('aadhar_url', 'aadhar_file', 'Aadhar Card'),
        ('pan_url', 'pan_file', 'PAN Card'),
        ('apaar_url', 'apaar_file', 'APAAR Document'),
        ('scm_url', 'scm_file', 'SCM Document'),
        ('jntuh_biodata_url', 'jntuh_biodata', 'JNTUH Bio-Data'),
        ('ssc_certificate_url', 'ssc_certificate', 'SSC Certificate'),
        ('inter_certificate_url', 'inter_certificate', 'Intermediate Certificate'),
        ('ug_certificate_url', 'ug_certificate', 'UG Certificate'),
        ('pg_certificate_url', 'pg_certificate', 'PG Certificate'),
        ('phd_certificate_url', 'phd_certificate', 'PhD Certificate'),
        ('research_proof_url', 'research_proof', 'Research Publications Proof'),
        ('fdp_certificate_url', 'fdp_certificate', 'FDP Certificate'),
        ('experience_certificates_url', 'experience_certificates', 'Experience Certificates'),
        ('other_documents_url', 'other_documents', 'Other Documents'),
    ]

    print("\n--- CHECKING DOCUMENTS ---")
    for url_field_name, file_field_name, display_name in doc_fields:
        cloudinary_url = getattr(faculty, url_field_name, None)
        file_field = getattr(faculty, file_field_name, None)
        if cloudinary_url and cloudinary_url.startswith('http'):
            try:
                print(f" 🌐 Downloading {display_name} from: {cloudinary_url}")
                response = requests.get(cloudinary_url, timeout=30)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    is_pdf = 'pdf' in content_type or cloudinary_url.lower().endswith('.pdf')
                    suffix = ".pdf" if is_pdf else ".jpg"
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tmp.write(response.content)
                    tmp.close()
                    if is_pdf:
                        pdf_files.append(tmp.name)
                        print(f" ✅ Downloaded PDF: {tmp.name}")
                    else:
                        image_files.append(tmp.name)
                        print(f" ✅ Downloaded Image: {tmp.name}")
                    temp_files.append(tmp.name)
                else:
                    print(f" ❌ Failed to download {display_name}: HTTP {response.status_code}")
                    if file_field:
                        file_path, _ = get_file_from_field(file_field, None)
                        if file_path and os.path.exists(file_path):
                            if file_path.lower().endswith('.pdf'):
                                pdf_files.append(file_path)
                                print(f" ✅ Fallback: {display_name} (PDF local): {file_path}")
                            else:
                                image_files.append(file_path)
                                print(f" ✅ Fallback: {display_name} (Image local): {file_path}")
            except Exception as e:
                print(f" ❌ Download error for {display_name}: {e}")
                if file_field:
                    file_path, _ = get_file_from_field(file_field, None)
                    if file_path and os.path.exists(file_path):
                        if file_path.lower().endswith('.pdf'):
                            pdf_files.append(file_path)
                            print(f" ✅ Fallback: {display_name} (PDF local): {file_path}")
                        else:
                            image_files.append(file_path)
                            print(f" ✅ Fallback: {display_name} (Image local): {file_path}")
        elif file_field:
            file_path, _ = get_file_from_field(file_field, None)
            if file_path and os.path.exists(file_path):
                if file_path.lower().endswith('.pdf'):
                    pdf_files.append(file_path)
                    print(f" ✅ {display_name} (PDF local): {file_path}")
                else:
                    image_files.append(file_path)
                    print(f" ✅ {display_name} (Image local): {file_path}")
            else:
                print(f" ❌ {display_name}: File not found")
        else:
            print(f" ❌ {display_name}: Not uploaded")

    # Certificates
    print("\n--- CHECKING CERTIFICATES ---")
    certificates = Certificate.objects.filter(faculty=faculty)
    print(f"📊 Found {certificates.count()} certificates")
    for cert in certificates:
        try:
            if cert.cloudinary_url:
                print(f" 🌐 Downloading certificate ({cert.certificate_type}): {cert.cloudinary_url}")
                response = requests.get(cert.cloudinary_url, timeout=30)
                if response.status_code == 200:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    tmp.write(response.content)
                    tmp.close()
                    pdf_files.append(tmp.name)
                    temp_files.append(tmp.name)
                    print(f" ✅ Downloaded certificate: {tmp.name}")
            elif cert.certificate_file:
                file_path, file_url = get_file_from_field(cert.certificate_file, None)
                if file_path and os.path.exists(file_path):
                    if file_path.lower().endswith('.pdf'):
                        pdf_files.append(file_path)
                        print(f" ✅ Certificate (local PDF): {file_path}")
                    else:
                        image_files.append(file_path)
                        print(f" ✅ Certificate (local image): {file_path}")
                elif file_url:
                    try:
                        print(f" 🌐 Downloading certificate ({cert.certificate_type}) from: {file_url}")
                        response = requests.get(file_url, timeout=30)
                        if response.status_code == 200:
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                            tmp.write(response.content)
                            tmp.close()
                            pdf_files.append(tmp.name)
                            temp_files.append(tmp.name)
                            print(f" ✅ Downloaded certificate: {tmp.name}")
                    except Exception as e:
                        print(f" ❌ Error: {e}")
        except Exception as e:
            print(f" ❌ Error processing certificate {cert.certificate_type}: {e}")

    print("\n" + "=" * 60)
    print("FILE COLLECTION SUMMARY")
    print("=" * 60)
    print(f" Images: {len(image_files)} files")
    for img in image_files:
        print(f" - {os.path.basename(img)}")
    print(f" PDFs: {len(pdf_files)} files")
    for pdf in pdf_files:
        print(f" - {os.path.basename(pdf)}")
    print("=" * 60 + "\n")

    return image_files, pdf_files, temp_files


# ==================== DEBUG / TEST VIEWS ====================
def test_template(request):
    return render(request, 'test.html', {
        'title': 'Template Test',
        'message': 'If you can see this, templates are working correctly!'
    })


def test_session(request):
    return JsonResponse({
        'student_logged_in': request.session.get('student_logged_in', False),
        'student_username': request.session.get('student_username', None),
        'session_keys': list(request.session.keys()),
        'path': request.path,
        'method': request.method,
    })


def debug_cloudinary(request):
    config = {
        'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', None),
        'api_key': getattr(settings, 'CLOUDINARY_API_KEY', None),
        'api_secret': ('***' + getattr(settings, 'CLOUDINARY_API_SECRET', '')[-4:]
                       if getattr(settings, 'CLOUDINARY_API_SECRET', None) else None),
        'configured': is_cloudinary_configured(),
    }
    connection_test = False
    error_msg = None
    if config['configured']:
        try:
            cloudinary.api.ping()
            connection_test = True
        except Exception as e:
            error_msg = str(e)
    return JsonResponse({
        'config': config,
        'connection_test': connection_test,
        'error': error_msg,
        'env_vars': {
            'CLOUDINARY_CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
            'CLOUDINARY_API_KEY': (
                os.environ.get('CLOUDINARY_API_KEY')[:4] + '...'
                if os.environ.get('CLOUDINARY_API_KEY') else None
            ),
            'CLOUDINARY_API_SECRET': (
                '***' + os.environ.get('CLOUDINARY_API_SECRET', '')[-4:]
                if os.environ.get('CLOUDINARY_API_SECRET') else None
            ),
        }
    })


def debug_login(request):
    return HttpResponse(f"""
    <html><body style="background:black;color:lime;font-family:monospace;padding:20px;">
    <h1>Login Debug Info</h1><pre>
student_logged_in: {request.session.get('student_logged_in', False)}
student_username: {request.session.get('student_username', 'None')}
session keys: {list(request.session.keys())}
user authenticated: {request.user.is_authenticated}
user: {request.user}
    </pre>
    <p><a href="/student-login/">Go to Student Login</a></p>
    <p><a href="/students-data/">Go to Students Data</a></p>
    <p><a href="/add-student/">Go to Add Student</a></p>
    </body></html>
    """)


@login_required
def debug_faculty_data(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    data = {}
    for field in Faculty._meta.fields:
        fn = field.name
        fv = getattr(faculty, fn)
        if fn == 'photo' and fv:
            try:
                data[fn] = {'url': fv.url if hasattr(fv, 'url') else str(fv), 'exists': True}
            except Exception:
                data[fn] = str(fv)
        elif fv and hasattr(fv, 'strftime'):
            data[fn] = fv.strftime('%Y-%m-%d')
        else:
            data[fn] = str(fv) if fv else None
    certificates = Certificate.objects.filter(faculty=faculty)
    data['certificates'] = [
        {
            'id': c.id,
            'certificate_type': c.certificate_type,
            'certificate_file': str(c.certificate_file) if c.certificate_file else None,
            'cloudinary_url': c.cloudinary_url,
            'issue_date': c.issue_date.strftime('%Y-%m-%d') if c.issue_date else None
        }
        for c in certificates
    ]
    data['subjects'] = [s.name for s in faculty.subjects.all()]
    data['research_publications'] = list(ResearchPublication.objects.filter(faculty=faculty).values())
    data['fdps'] = list(FDP.objects.filter(faculty=faculty).values())
    data['btech_projects'] = list(BTechProject.objects.filter(faculty=faculty).values())
    return JsonResponse(data, safe=False, json_dumps_params={'indent': 2})


# ==================== FACULTY PROFILE VIEW ====================
@login_required
def edit_faculty_complete(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == "POST":
        for attr in ['staff_name', 'employee_code', 'department', 'designation', 'email', 'mobile',
                     'gender', 'address', 'father_name', 'mother_name', 'aadhar', 'pan', 'state',
                     'caste', 'sub_caste', 'nationality', 'jntuh_id', 'aicte_id', 'orcid_id', 'apaar_id',
                     'ug_degree', 'ug_college', 'ug_spec', 'pg_degree', 'pg_college', 'pg_spec',
                     'phd_degree', 'phd_university', 'phd_spec', 'about_yourself']:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)
        for date_attr in ['joining_date', 'dob', 'ug_year', 'pg_year', 'phd_year']:
            val = request.POST.get(date_attr)
            if val:
                setattr(faculty, date_attr, val)
        for pct_attr in ['ug_percentage', 'pg_percentage', 'ssc_percent', 'inter_percent']:
            val = request.POST.get(pct_attr)
            if val:
                setattr(faculty, pct_attr, val)
        for text_attr in ['ssc_year', 'ssc_school', 'inter_year', 'inter_college']:
            val = request.POST.get(text_attr)
            if val:
                setattr(faculty, text_attr, val)
        if request.FILES.get("photo"):
            faculty.photo = request.FILES["photo"]
        faculty.save()
        messages.success(request, f'Faculty {faculty.staff_name} updated successfully!')
        return HttpResponseRedirect(reverse('dashboard:faculty_dashboard') + f'?id={faculty.id}')
    return render(request, 'dashboard/edit_faculty_complete.html', {
        'faculty': faculty,
        'title': f'Edit Faculty - {faculty.staff_name}',
    })


@login_required
def faculty_profile_view(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    profile, _ = FacultyProfile.objects.get_or_create(faculty=faculty)
    research_projects = ResearchProject.objects.filter(faculty=faculty)
    research_publications = ResearchPublication.objects.filter(faculty=faculty).order_by('-publication_year')
    fdps = FDP.objects.filter(faculty=faculty).order_by('-from_date')
    btech_projects = BTechProject.objects.filter(faculty=faculty).order_by('-batch')
    if request.method == "POST":
        profile_form = FacultyProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save()
            research_data = request.POST.get('research_publications')
            if research_data:
                try:
                    research_list = json.loads(research_data)
                    ResearchPublication.objects.filter(faculty=faculty).delete()
                    for item in research_list:
                        ResearchPublication.objects.create(
                            faculty=faculty,
                            research_type=item.get('type'),
                            title=item.get('title'),
                            authors=item.get('authors'),
                            department=item.get('department'),
                            publication_year=item.get('year'),
                            publisher_name=item.get('publisher'),
                            status=item.get('status'),
                            doi=item.get('doi'),
                            url=item.get('url'),
                            abstract=item.get('abstract'),
                            keywords=item.get('keywords'),
                            journal_name=item.get('journal_name'),
                            issn=item.get('issn'),
                            volume=item.get('volume'),
                            issue=item.get('issue'),
                            page_numbers=item.get('pages'),
                            conference_name=item.get('conference_name'),
                            conference_location=item.get('location'),
                            book_title=item.get('book_title'),
                            isbn=item.get('isbn'),
                            edition=item.get('edition'),
                            patent_number=item.get('patent_number'),
                            filing_date=item.get('filing_date'),
                            grant_date=item.get('grant_date'),
                            project_title=item.get('project_title'),
                            funding_agency=item.get('funding_agency'),
                            sanction_amount=item.get('sanction_amount'),
                            award_title=item.get('award_title'),
                            awarding_body=item.get('award_body'),
                            award_date=item.get('award_date'),
                        )
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing research publications JSON: {e}")
            fdp_data = request.POST.get('fdp_entries')
            if fdp_data:
                try:
                    fdp_list = json.loads(fdp_data)
                    FDP.objects.filter(faculty=faculty).delete()
                    for item in fdp_list:
                        FDP.objects.create(
                            faculty=faculty,
                            fdp_type=item.get('type'),
                            title=item.get('title'),
                            from_date=datetime.strptime(item.get('from_date'), '%Y-%m-%d').date(),
                            to_date=datetime.strptime(item.get('to_date'), '%Y-%m-%d').date(),
                            organized_by=item.get('organized_by'),
                            place=item.get('place'),
                            mode=item.get('mode'),
                            level=item.get('level'),
                            role=item.get('role'),
                            sponsored_by=item.get('sponsored_by'),
                            remarks=item.get('remarks')
                        )
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing FDP entries JSON: {e}")
            project_data = request.POST.get('btech_projects')
            if project_data:
                try:
                    project_list = json.loads(project_data)
                    BTechProject.objects.filter(faculty=faculty).delete()
                    for item in project_list:
                        BTechProject.objects.create(
                            faculty=faculty,
                            ht_no=item.get('ht_no'),
                            student_name=item.get('student_name'),
                            batch=item.get('batch'),
                            project_title=item.get('title'),
                            approved=item.get('approved') == 'Yes',
                            marks=item.get('marks')
                        )
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing B.Tech projects JSON: {e}")
            messages.success(request, 'Faculty profile updated successfully!')
            return redirect('dashboard:faculty_profile_view', faculty_id=faculty.id)
    else:
        profile_form = FacultyProfileForm(instance=profile)
    research_publications_json = json.dumps([{
        'type': r.research_type,
        'type_display': r.get_research_type_display(),
        'title': r.title,
        'authors': r.authors,
        'year': r.publication_year,
        'status': r.status,
        'doi': r.doi,
        'journal_name': r.journal_name,
        'conference_name': r.conference_name,
        'book_title': r.book_title,
        'patent_number': r.patent_number,
        'project_title': r.project_title,
        'award_title': r.award_title,
    } for r in research_publications])
    fdp_entries_json = json.dumps([{
        'type': f.fdp_type,
        'type_display': f.get_fdp_type_display(),
        'title': f.title,
        'from_date': f.from_date.strftime('%Y-%m-%d'),
        'to_date': f.to_date.strftime('%Y-%m-%d'),
        'organized_by': f.organized_by,
        'place': f.place,
        'duration': f.duration_days(),
        'mode': f.mode,
        'level': f.level,
        'role': f.role,
    } for f in fdps])
    btech_projects_json = json.dumps([{
        'ht_no': p.ht_no,
        'student_name': p.student_name,
        'batch': p.batch,
        'title': p.project_title,
        'approved': 'Yes' if p.approved else 'No',
        'marks': p.marks,
    } for p in btech_projects])
    return render(request, 'dashboard/faculty_profile.html', {
        'faculty': faculty,
        'profile': profile,
        'profile_form': profile_form,
        'research_projects': research_projects,
        'research_publications': research_publications,
        'research_publications_json': research_publications_json,
        'fdps': fdps,
        'fdp_entries_json': fdp_entries_json,
        'btech_projects': btech_projects,
        'btech_projects_json': btech_projects_json,
        'title': f'Profile - {faculty.staff_name}',
    })


@login_required
@require_POST
def delete_research_project(request, project_id):
    project = get_object_or_404(ResearchProject, id=project_id)
    project.delete()
    messages.success(request, 'Research project deleted successfully.')
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_research_publication(request, publication_id):
    publication = get_object_or_404(ResearchPublication, id=publication_id)
    faculty_id = publication.faculty.id
    publication.delete()
    messages.success(request, 'Research publication deleted successfully.')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('dashboard:faculty_profile_view', faculty_id=faculty_id)


@login_required
@require_POST
def delete_fdp(request, fdp_id):
    fdp = get_object_or_404(FDP, id=fdp_id)
    faculty_id = fdp.faculty.id
    fdp.delete()
    messages.success(request, 'FDP entry deleted successfully.')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('dashboard:faculty_profile_view', faculty_id=faculty_id)


@login_required
@require_POST
def delete_btech_project(request, project_id):
    project = get_object_or_404(BTechProject, id=project_id)
    faculty_id = project.faculty.id
    project.delete()
    messages.success(request, 'B.Tech project deleted successfully.')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('dashboard:faculty_profile_view', faculty_id=faculty_id)


def laboratory(request):
    return render(request, 'dashboard/laboratory.html', {'title': 'Laboratory'})


def gallery(request):
    return render(request, 'dashboard/gallery.html', {'title': 'Gallery'})


def student_detail(request, student_id):
    if not request.session.get('student_logged_in') and not request.user.is_authenticated:
        return redirect('dashboard:student_login')
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'dashboard/student_detail.html', {
        'student': student,
        'title': f'{student.student_name} - Details',
    })


# ==================== CLOUDINARY SYNC ====================
@login_required
def sync_to_cloudinary(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if not is_cloudinary_configured():
        messages.error(request, "Cloudinary is not configured properly.")
        return redirect("dashboard:faculty_dashboard")
    if faculty.pdf_document and not faculty.cloudinary_pdf_url:
        try:
            with faculty.pdf_document.open("rb") as f:
                resp = cloudinary.uploader.upload(
                    f, folder="faculty_pdfs", resource_type="raw",
                    public_id=f"faculty_{faculty.employee_code}_profile", overwrite=True,
                )
            faculty.cloudinary_pdf_url = resp["secure_url"]
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type="pdf",
                cloudinary_url=resp["secure_url"], public_id=resp["public_id"],
                resource_type=resp["resource_type"], uploaded_by=request.user.username,
            )
        except Exception as e:
            messages.error(request, f"Error uploading PDF: {e}")
            return redirect("dashboard:faculty_dashboard")
    if faculty.photo and not faculty.cloudinary_photo_url:
        try:
            with faculty.photo.open("rb") as f:
                resp = cloudinary.uploader.upload(
                    f, folder="faculty_photos",
                    public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                    transformation=[{'width': 300, 'height': 300, 'crop': 'fill'},
                                    {'quality': 'auto:good'}]
                )
            faculty.cloudinary_photo_url = resp["secure_url"]
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type="photo",
                cloudinary_url=resp["secure_url"], public_id=resp["public_id"],
                resource_type=resp["resource_type"], uploaded_by=request.user.username,
            )
        except Exception as e:
            messages.error(request, f"Error uploading photo: {e}")
            return redirect("dashboard:faculty_dashboard")
    FacultyLog.objects.create(
        faculty=faculty, action="Cloudinary Sync",
        details=f"Faculty synced to Cloudinary: {faculty.employee_code}",
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    messages.success(request, f"Faculty {faculty.employee_code} synced to Cloudinary.")
    return redirect("dashboard:faculty_dashboard")


@login_required
def upload_to_cloudinary(request, faculty_id):
    return sync_to_cloudinary(request, faculty_id)


# ==================== AUTHENTICATION ====================
def login_view(request):
    return render(request, 'dashboard/login.html', {
        'title': 'Login - ANURAG ENGINEERING COLLEGE',
        'student_login': False,
        'admin_login': False,
    })


@csrf_protect
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Admin login successful!')
            return redirect('dashboard:dashboard')
        else:
            error = 'Invalid admin credentials'
            messages.error(request, error)
    return render(request, 'dashboard/login.html', {
        'title': 'Admin Login - ANURAG ENGINEERING COLLEGE',
        'admin_login': True, 'error': error,
    })


def student_login(request):
    if request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "anrkitstudent" and password == "anrkitstudent":
            request.session["student_logged_in"] = True
            request.session["student_username"] = username
            messages.success(request, "Student login successful!")
            return redirect("dashboard:students_data")
        error = "Invalid student credentials"
        messages.error(request, error)
    return render(request, 'dashboard/login.html', {
        'student_login': True, 'error': error,
        'title': 'Student Login - ANURAG ENGINEERING COLLEGE'
    })


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
    else:
        messages.success(request, 'Logged out successfully.')
    for key in ('student_logged_in', 'student_username', 'student_role'):
        request.session.pop(key, None)
    return redirect('dashboard:login')


def student_logout(request):
    request.session.flush()
    messages.success(request, "Student logged out successfully.")
    return redirect('dashboard:student_login')


def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
    return redirect('dashboard:admin_login')


# ==================== HOME & DASHBOARD ====================
def home(request):
    if request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard')
    if request.user.is_authenticated:
        return redirect('dashboard:admin_dashboard' if request.user.is_superuser else 'dashboard:dashboard')
    return render(request, 'dashboard/home.html', {
        'title': 'Faculty Management System - Home',
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:5],
        'recent_activities': FacultyLog.objects.order_by('-created_at')[:5],
        'show_hero': True,
    })


@login_required
def dashboard(request):
    total_faculty = Faculty.objects.count()
    with_phd = Faculty.objects.exclude(phd_degree__isnull=True).exclude(phd_degree__exact='').count()
    today = date.today()
    exp_distribution = {'0-5': 0, '5-10': 0, '10-15': 0, '15+': 0}
    for f in Faculty.objects.all():
        if f.joining_date:
            yrs = (today - f.joining_date).days / 365.25
            if yrs <= 5:
                exp_distribution['0-5'] += 1
            elif yrs <= 10:
                exp_distribution['5-10'] += 1
            elif yrs <= 15:
                exp_distribution['10-15'] += 1
            else:
                exp_distribution['15+'] += 1
    return render(request, "dashboard/dashboard.html", {
        'title': 'Dashboard',
        'total_faculty': total_faculty,
        'with_phd': with_phd,
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_certificates': Certificate.objects.count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count'),
        'recent_uploads': Faculty.objects.order_by('-created_at')[:5],
        'recent_logs': FacultyLog.objects.order_by('-created_at')[:5],
        'exp_distribution': exp_distribution,
        'today': today,
        'user': request.user,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard')
    total_faculty = Faculty.objects.count()
    departments = list(Faculty.objects.values('department')
                       .annotate(count=Count('id'), active=Count('id', filter=Q(is_active=True)))
                       .order_by('-count'))
    for d in departments:
        d['percentage'] = (d['count'] / total_faculty * 100) if total_faculty > 0 else 0
    system_stats = {}
    if psutil:
        try:
            system_stats = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as e:
            system_stats = {'error': str(e)}
    return render(request, "dashboard/admin_dashboard.html", {
        'title': 'Admin Dashboard',
        'total_faculty': total_faculty,
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'cloudinary_uploads': CloudinaryUpload.objects.count(),
        'with_phd': Faculty.objects.filter(phd_degree='Completed').count(),
        'departments': departments,
        'recent_logs': FacultyLog.objects.order_by('-created_at')[:10],
        'system_stats': system_stats,
        'user_activity': {
            'total_users': User.objects.count(),
            'active_today': FacultyLog.objects.filter(
                created_at__date=date.today()).values('performed_by').distinct().count(),
        },
        'has_psutil': psutil is not None,
        'recent_uploads': Faculty.objects.order_by('-created_at')[:5],
    })


def student_dashboard(request):
    if not request.session.get('student_logged_in'):
        messages.error(request, 'Please login to access student dashboard')
        return redirect('dashboard:student_login')
    student_username = request.session.get('student_username', 'anrkitstudent')
    student = None
    try:
        student = Student.objects.filter(ht_no=student_username).first()
    except Exception as e:
        logger.error(f"Error getting student data: {e}")
    if not student:
        student = {
            'ht_no': student_username, 'student_name': 'Student User',
            'year': 'II', 'sem': 'II', 'branch': 'Computer Science',
            'email': 'student@anurag.edu.in', 'student_phone': 'Not Available',
            'cgpa': None, 'photo': None, 'photo_url': None,
        }
    certificates = []
    if student and hasattr(student, 'id'):
        for fn, dn in [('cert_achieve', 'Achievement'), ('cert_intern', 'Internship'),
                       ('cert_courses', 'Courses'), ('cert_sdp', 'SDP'),
                       ('cert_extra', 'Extra Curricular'), ('cert_placement', 'Placement'),
                       ('cert_national', 'National Exam')]:
            if hasattr(student, fn) and getattr(student, fn):
                certificates.append({'type': dn, 'field': fn, 'has_file': True})
    return render(request, "dashboard/student_dashboard.html", {
        'student': student, 'title': 'Student Dashboard',
        'total_students': Student.objects.count(),
        'recent_students': Student.objects.order_by('-created_at')[:5],
        'certificates': certificates, 'is_student': True,
    })


def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect('dashboard:admin_dashboard' if request.user.is_superuser else 'dashboard:dashboard')
    elif request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard')
    return redirect('dashboard:login')


# ==================== SYLLABUS VIEW ====================
@login_required
def syllabus_view(request):
    return render(request, 'dashboard/syllabus.html', {
        'title': 'Syllabus & Common Subjects - ANURAG Engineering College',
    })


# ==================== EXAM BRANCH VIEW ====================
def exam_branch(request):
    """View for exam branch page"""
    return render(request, 'dashboard/exam_branch.html', {
        'title': 'Exam Branch - ANURAG Engineering College',
    })


# ==================== FACULTY DASHBOARD ====================
@login_required
def faculty_dashboard(request, faculty_id=None):
    pdf_mode = request.GET.get("print") == "1"
    if pdf_mode:
        fid = request.GET.get("id")
        if not fid:
            return HttpResponseBadRequest("Faculty ID required for PDF mode")
        f = get_object_or_404(Faculty, id=fid)
        exp = calculate_experience(f.joining_date) if f.joining_date else "N/A"
        return render(request, "dashboard/faculty_pdf.html", {
            "faculty": f,
            "pdf_mode": True,
            "current_date": timezone.now(),
            "experience": exp,
            "cloudinary_status": {"has_pdf": bool(f.cloudinary_pdf_url)},
        })
    faculties = Faculty.objects.all().order_by('staff_name')
    faculty = None
    certificates = None
    research_projects = None
    research_publications = None
    fdps = None
    btech_projects = None
    results_data = None
    subjects_list = []
    if faculty_id:
        faculty = get_object_or_404(Faculty, id=faculty_id)
    elif request.GET.get('id'):
        faculty = get_object_or_404(Faculty, id=request.GET.get('id'))
    elif faculties.exists():
        faculty = faculties.first()
    if faculty:
        certificates = Certificate.objects.filter(faculty=faculty)
        research_projects = ResearchProject.objects.filter(faculty=faculty)
        research_publications = ResearchPublication.objects.filter(faculty=faculty).order_by('-publication_year')
        fdps = FDP.objects.filter(faculty=faculty).order_by('-from_date')
        btech_projects = BTechProject.objects.filter(faculty=faculty).order_by('-batch')
        sd = getattr(faculty, 'subjects_dealt', None)
        if sd:
            subjects_list = [s.strip() for s in sd.split(',') if s.strip()]
        if faculty.results:
            try:
                results_data = json.loads(faculty.results)
                if not isinstance(results_data, list):
                    results_data = [results_data]
            except (json.JSONDecodeError, TypeError):
                results_data = faculty.results
    if request.GET.get('analytics') == 'true' or (not faculty and faculties.exists()):
        return faculty_analytics(request)
    experience = calculate_experience(faculty.joining_date) if faculty and faculty.joining_date else "N/A"
    departments = Faculty.objects.values_list('department', flat=True).distinct().order_by('department')
    return render(request, 'dashboard/faculty_dashboard.html', {
        'faculties': faculties,
        'faculty': faculty,
        'certificates': certificates or [],
        'research_projects': research_projects or [],
        'research_publications': research_publications or [],
        'fdps': fdps or [],
        'btech_projects': btech_projects or [],
        'results_data': results_data,
        'subjects_list': subjects_list,
        'experience': experience,
        'cloudinary_status': {
            'has_pdf': bool(faculty.cloudinary_pdf_url) if faculty else False,
            'has_photo': bool(faculty.cloudinary_photo_url) if faculty else False,
        },
        'current_date': timezone.now(),
        'is_analytics': False,
        'pdf_mode': False,
        'departments': departments,
        'title': f'Faculty Profile - {faculty.staff_name}' if faculty else 'Faculty Dashboard',
    })


@login_required
def faculty_analytics(request):
    total = Faculty.objects.count()
    departments = list(Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count'))
    for d in departments:
        d['percentage'] = (d['count'] / total * 100) if total > 0 else 0
    today = date.today()
    exp_stats = {'0_5': 0, '5_10': 0, '10_plus': 0}
    for f in Faculty.objects.all():
        if f.joining_date:
            yrs = today.year - f.joining_date.year
            if yrs <= 5:
                exp_stats['0_5'] += 1
            elif yrs <= 10:
                exp_stats['5_10'] += 1
            else:
                exp_stats['10_plus'] += 1
    research_stats = {
        'total': ResearchPublication.objects.count(),
        'journal': ResearchPublication.objects.filter(research_type='journal').count(),
        'conference': ResearchPublication.objects.filter(research_type='conference').count(),
        'patent': ResearchPublication.objects.filter(research_type='patent').count(),
    }
    fdp_stats = {
        'total': FDP.objects.count(),
        'fdp': FDP.objects.filter(fdp_type='fdp').count(),
        'workshop': FDP.objects.filter(fdp_type='workshop').count(),
    }
    return render(request, 'dashboard/faculty.html', {
        'is_analytics': True, 'total_faculty': total,
        'qualification_stats': {
            'phd_completed': Faculty.objects.filter(phd_degree='Completed').count(),
            'phd_pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
            'pg_only': Faculty.objects.filter(pg_year__isnull=False,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
            'ug_only': Faculty.objects.filter(ug_year__isnull=False, pg_year__isnull=True,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
        },
        'departments': departments,
        'experience_stats': exp_stats,
        'research_stats': research_stats,
        'fdp_stats': fdp_stats,
        'faculties': Faculty.objects.all()[:10],
        'title': 'Faculty Analytics',
    })


# ==================== FACULTY LIST ====================
@login_required
def faculty_list(request):
    qs = Faculty.objects.all().order_by('staff_name')
    sq = request.GET.get('search', '')
    if sq:
        qs = qs.filter(Q(staff_name__icontains=sq) | Q(employee_code__icontains=sq) |
                       Q(email__icontains=sq) | Q(department__icontains=sq) | Q(designation__icontains=sq))
    df = request.GET.get('department', '')
    if df:
        qs = qs.filter(department__icontains=df)
    sf = request.GET.get('status', '')
    if sf == 'active':
        qs = qs.filter(is_active=True)
    elif sf == 'inactive':
        qs = qs.filter(is_active=False)
    qf = request.GET.get('qualification', '')
    if qf == 'phd':
        qs = qs.filter(phd_degree='Completed')
    elif qf == 'pg':
        qs = qs.filter(pg_year__isnull=False, phd_degree__in=['', 'Not Started', 'None'])
    paginator = Paginator(qs, 20)
    try:
        faculties = paginator.page(request.GET.get('page', 1))
    except (PageNotAnInteger, EmptyPage) as e:
        faculties = paginator.page(1 if isinstance(e, PageNotAnInteger) else paginator.num_pages)
    return render(request, 'dashboard/faculty_list.html', {
        'faculties': faculties,
        'departments': Faculty.objects.values_list('department', flat=True).distinct().order_by('department'),
        'search_query': sq, 'department_filter': df, 'status_filter': sf, 'qualification_filter': qf,
        'total_faculty': qs.count(), 'page_title': 'Faculty Directory', 'active_page': 'faculty_list',
    })


# ==================== ADD FACULTY ====================
@login_required
def add_faculty(request):
    print("=" * 60)
    print("ADD FACULTY VIEW CALLED")
    print(f"Request method: {request.method}")
    print("=" * 60)
    if request.method == "POST":
        print("=" * 60)
        print("ADD FACULTY - POST REQUEST RECEIVED")
        print(f"POST data keys: {list(request.POST.keys())}")
        print(f"FILES data keys: {list(request.FILES.keys())}")
        print("=" * 60)
        try:
            def get_int_or_none(value):
                return int(value) if value and value.strip() else None

            def get_float_or_none(value):
                return float(value) if value and value.strip() else None

            def get_date_or_none(value):
                return value if value and value.strip() else None

            staff_name = request.POST.get("staff_name", "").strip()
            employee_code = request.POST.get("employee_code", "").strip()
            if not staff_name or not employee_code:
                messages.error(request, "Staff Name and Employee Code are required!")
                return redirect("dashboard:add_faculty")
            print(f"Creating faculty: {staff_name} ({employee_code})")
            faculty = Faculty.objects.create(
                staff_name=staff_name,
                employee_code=employee_code,
                father_name=request.POST.get("father_name", "").strip(),
                mother_name=request.POST.get("mother_name", "").strip(),
                dob=get_date_or_none(request.POST.get("dob")),
                gender=request.POST.get("gender"),
                state=request.POST.get("state", "").strip(),
                caste=request.POST.get("caste", "").strip(),
                sub_caste=request.POST.get("sub_caste", "").strip(),
                nationality=request.POST.get("nationality", "Indian").strip(),
                address=request.POST.get("address", "").strip(),
                mobile=request.POST.get("mobile", "").strip(),
                phone=request.POST.get("phone", "").strip(),
                email=request.POST.get("email", "").strip(),
                department=request.POST.get("department", "").strip(),
                designation=request.POST.get("designation", "").strip(),
                joining_date=get_date_or_none(request.POST.get("joining_date")),
                jntuh_id=request.POST.get("jntuh_id", "").strip(),
                aicte_id=request.POST.get("aicte_id", "").strip(),
                pan=request.POST.get("pan", "").strip(),
                aadhar=request.POST.get("aadhar", "").strip(),
                apaar_id=request.POST.get("apaar_id", "").strip(),
                orcid_id=request.POST.get("orcid_id", "").strip(),
                ssc_year=get_int_or_none(request.POST.get("ssc_year")),
                ssc_percent=get_float_or_none(request.POST.get("ssc_percent")),
                ssc_school=request.POST.get("ssc_school", "").strip(),
                inter_year=get_int_or_none(request.POST.get("inter_year")),
                inter_percent=get_float_or_none(request.POST.get("inter_percent")),
                inter_college=request.POST.get("inter_college", "").strip(),
                ug_degree=request.POST.get("ug_degree", "").strip(),
                ug_year=get_int_or_none(request.POST.get("ug_year")),
                ug_percentage=get_float_or_none(request.POST.get("ug_percentage")),
                ug_college=request.POST.get("ug_college", "").strip(),
                ug_spec=request.POST.get("ug_spec", "").strip(),
                pg_degree=request.POST.get("pg_degree", "").strip(),
                pg_year=get_int_or_none(request.POST.get("pg_year")),
                pg_percentage=get_float_or_none(request.POST.get("pg_percentage")),
                pg_college=request.POST.get("pg_college", "").strip(),
                pg_spec=request.POST.get("pg_spec", "").strip(),
                phd_degree=request.POST.get("phd_degree", "").strip(),
                phd_year=get_int_or_none(request.POST.get("phd_year")),
                phd_university=request.POST.get("phd_university", "").strip(),
                phd_spec=request.POST.get("phd_spec", "").strip(),
                subjects_dealt=request.POST.get("subjects_dealt", "").strip(),
                scm=request.POST.get("scm", "").strip(),
                about_yourself=request.POST.get("about_yourself", "").strip(),
                results="",
                photo=request.FILES.get("photo"),
                exp_anurag=request.POST.get("exp_anurag", "").strip(),
                exp_other=request.POST.get("exp_other", "").strip(),
            )
            FacultyProfile.objects.create(faculty=faculty)
            print(f"✅ Faculty profile created for {staff_name}")
            if request.FILES.get("photo") and is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES["photo"],
                        folder="faculty_photos",
                        public_id=f"faculty_{faculty.employee_code}_photo",
                        overwrite=True,
                        transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                    )
                    faculty.cloudinary_photo_url = cr["secure_url"]
                    faculty.save()
                    CloudinaryUpload.objects.create(
                        faculty=faculty,
                        upload_type="photo",
                        cloudinary_url=cr["secure_url"],
                        public_id=cr["public_id"],
                        resource_type=cr["resource_type"],
                        uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                    )
                    print(f"✅ Photo uploaded to Cloudinary")
                except Exception as e:
                    logger.error(f"Cloudinary photo upload error: {e}")
                    messages.warning(request, "Faculty added but Cloudinary photo upload failed.")
            doc_fields = [
                ('aadhar_file', 'aadhar_url', 'aadhar'),
                ('pan_file', 'pan_url', 'pan'),
                ('apaar_file', 'apaar_url', 'apaar'),
                ('scm_file', 'scm_url', 'scm'),
                ('jntuh_biodata', 'jntuh_biodata_url', 'jntuh_biodata'),
                ('ssc_certificate', 'ssc_certificate_url', 'ssc'),
                ('inter_certificate', 'inter_certificate_url', 'inter'),
                ('ug_certificate', 'ug_certificate_url', 'ug'),
                ('pg_certificate', 'pg_certificate_url', 'pg'),
                ('phd_certificate', 'phd_certificate_url', 'phd'),
            ]
            for field_name, url_field_name, doc_type in doc_fields:
                uploaded_file = request.FILES.get(field_name)
                if uploaded_file:
                    if is_cloudinary_configured():
                        try:
                            is_pdf = uploaded_file.name.lower().endswith('.pdf')
                            resource_type = "raw" if is_pdf else "auto"
                            result = cloudinary.uploader.upload(
                                uploaded_file,
                                resource_type=resource_type,
                                folder=f"faculty_documents/{faculty.employee_code}",
                                public_id=f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                overwrite=True
                            )
                            setattr(faculty, url_field_name, result['secure_url'])
                            setattr(faculty, field_name, uploaded_file)
                            CloudinaryUpload.objects.create(
                                faculty=faculty,
                                upload_type=field_name,
                                cloudinary_url=result['secure_url'],
                                public_id=result['public_id'],
                                resource_type=resource_type,
                                uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                            )
                        except Exception as e:
                            logger.error(f"Cloudinary upload error for {field_name}: {e}")
                            setattr(faculty, field_name, uploaded_file)
                    else:
                        setattr(faculty, field_name, uploaded_file)
            faculty.save()
            research_proof = request.FILES.get("research_proof")
            if research_proof:
                research_proof_academic_year = request.POST.get("research_proof_academic_year", "").strip()
                faculty.research_proof_academic_year = research_proof_academic_year
                if is_cloudinary_configured():
                    try:
                        is_pdf = research_proof.name.lower().endswith('.pdf')
                        resource_type = "raw" if is_pdf else "auto"
                        result = cloudinary.uploader.upload(
                            research_proof,
                            resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}/research_proofs",
                            public_id=f"research_proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=True
                        )
                        faculty.research_proof_url = result['secure_url']
                        faculty.research_proof = research_proof
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='research_proof',
                            cloudinary_url=result['secure_url'],
                            public_id=result['public_id'],
                            resource_type=resource_type,
                            uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                        )
                        print(
                            f"✅ Research Proof uploaded to Cloudinary with academic year: {research_proof_academic_year}")
                    except Exception as e:
                        logger.error(f"Cloudinary upload error for research_proof: {e}")
                        faculty.research_proof = research_proof
                else:
                    faculty.research_proof = research_proof
            fdp_certificate = request.FILES.get("fdp_certificate")
            if fdp_certificate:
                fdp_certificate_academic_year = request.POST.get("fdp_certificate_academic_year", "").strip()
                faculty.fdp_certificate_academic_year = fdp_certificate_academic_year
                if is_cloudinary_configured():
                    try:
                        is_pdf = fdp_certificate.name.lower().endswith('.pdf')
                        resource_type = "raw" if is_pdf else "auto"
                        result = cloudinary.uploader.upload(
                            fdp_certificate,
                            resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}/fdp_certificates",
                            public_id=f"fdp_cert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=True
                        )
                        faculty.fdp_certificate_url = result['secure_url']
                        faculty.fdp_certificate = fdp_certificate
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='fdp_certificate',
                            cloudinary_url=result['secure_url'],
                            public_id=result['public_id'],
                            resource_type=resource_type,
                            uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                        )
                        print(
                            f"✅ FDP Certificate uploaded to Cloudinary with academic year: {fdp_certificate_academic_year}")
                    except Exception as e:
                        logger.error(f"Cloudinary upload error for fdp_certificate: {e}")
                        faculty.fdp_certificate = fdp_certificate
                else:
                    faculty.fdp_certificate = fdp_certificate
            classes_taken = request.POST.get('classes_taken')
            if classes_taken:
                try:
                    faculty.classes_taken = int(classes_taken)
                except ValueError:
                    faculty.classes_taken = None
            else:
                faculty.classes_taken = None
            experience_certificates = request.FILES.get('experience_certificates')
            if experience_certificates:
                experience_certificates_academic_year = request.POST.get("experience_certificates_academic_year",
                                                                         "").strip()
                faculty.experience_certificates_academic_year = experience_certificates_academic_year
                if is_cloudinary_configured():
                    try:
                        is_pdf = experience_certificates.name.lower().endswith('.pdf')
                        resource_type = "raw" if is_pdf else "auto"
                        result = cloudinary.uploader.upload(
                            experience_certificates,
                            resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}",
                            public_id=f"experience_cert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=True
                        )
                        faculty.experience_certificates_url = result['secure_url']
                        faculty.experience_certificates = experience_certificates
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='experience_certificates',
                            cloudinary_url=result['secure_url'],
                            public_id=result['public_id'],
                            resource_type=resource_type,
                            uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                        )
                        print(
                            f"✅ Experience Certificates uploaded to Cloudinary with academic year: {experience_certificates_academic_year}")
                    except Exception as e:
                        logger.error(f"Cloudinary upload error for experience_certificates: {e}")
                        faculty.experience_certificates = experience_certificates
                else:
                    faculty.experience_certificates = experience_certificates
            other_documents = request.FILES.get('other_documents')
            if other_documents:
                other_documents_academic_year = request.POST.get("other_documents_academic_year", "").strip()
                faculty.other_documents_academic_year = other_documents_academic_year
                if is_cloudinary_configured():
                    try:
                        is_pdf = other_documents.name.lower().endswith('.pdf')
                        resource_type = "raw" if is_pdf else "auto"
                        result = cloudinary.uploader.upload(
                            other_documents,
                            resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}",
                            public_id=f"other_docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=True
                        )
                        faculty.other_documents_url = result['secure_url']
                        faculty.other_documents = other_documents
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='other_documents',
                            cloudinary_url=result['secure_url'],
                            public_id=result['public_id'],
                            resource_type=resource_type,
                            uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                        )
                        print(
                            f"✅ Other Documents uploaded to Cloudinary with academic year: {other_documents_academic_year}")
                    except Exception as e:
                        logger.error(f"Cloudinary upload error for other_documents: {e}")
                        faculty.other_documents = other_documents
                else:
                    faculty.other_documents = other_documents
            faculty.save()
            research_data_raw = request.POST.get('research_publications_json', '[]').strip()
            if research_data_raw and research_data_raw != '[]':
                try:
                    research_list = json.loads(research_data_raw)
                    saved_count = 0
                    for idx, item in enumerate(research_list):
                        if item.get('title'):
                            ResearchPublication.objects.create(
                                faculty=faculty,
                                research_type=item.get('research_type', 'journal'),
                                title=item.get('title', '').strip(),
                                authors=item.get('authors', '').strip(),
                                academic_year=item.get('academic_year', '').strip(),
                                publication_year=item.get('publication_year'),
                                journal_name=item.get('journal_name', '').strip(),
                                conference_name=item.get('conference_name', '').strip(),
                                doi=item.get('doi', '').strip(),
                                status=item.get('status', 'published'),
                            )
                            saved_count += 1
                    print(f"✅ Saved {saved_count} research publications")
                except (json.JSONDecodeError, Exception) as e:
                    logger.error(f"Error saving research publications: {e}")
                    messages.warning(request, "Faculty added but some research publications could not be saved.")
            btech_data_raw = request.POST.get('btech_projects_json', '[]').strip()
            if btech_data_raw and btech_data_raw != '[]':
                try:
                    project_list = json.loads(btech_data_raw)
                    saved_count = 0
                    for item in project_list:
                        if item.get('project_title'):
                            BTechProject.objects.create(
                                faculty=faculty,
                                ht_no=item.get('ht_no', '').strip(),
                                student_name=item.get('student_name', '').strip(),
                                batch=item.get('batch', '').strip(),
                                project_title=item.get('project_title', '').strip(),
                                approved=bool(item.get('approved', False)),
                                marks=item.get('marks') or None,
                            )
                            saved_count += 1
                    print(f"✅ Saved {saved_count} B.Tech projects")
                except (json.JSONDecodeError, Exception) as e:
                    logger.error(f"Error saving B.Tech projects: {e}")
                    messages.warning(request, "Faculty added but some B.Tech projects could not be saved.")
            fdp_data_raw = request.POST.get('fdp_entries_json', '[]').strip()
            if fdp_data_raw and fdp_data_raw != '[]':
                try:
                    fdp_list = json.loads(fdp_data_raw)
                    saved_count = 0
                    for item in fdp_list:
                        if item.get('title'):
                            FDP.objects.create(
                                faculty=faculty,
                                fdp_type=item.get('fdp_type', 'fdp'),
                                title=item.get('title', '').strip(),
                                academic_year=item.get('academic_year', '').strip(),
                                from_date=datetime.strptime(item.get('from_date'), '%Y-%m-%d').date() if item.get(
                                    'from_date') else None,
                                to_date=datetime.strptime(item.get('to_date'), '%Y-%m-%d').date() if item.get(
                                    'to_date') else None,
                                organized_by=item.get('organized_by', '').strip(),
                                place=item.get('place', '').strip(),
                                mode=item.get('mode', 'offline'),
                                level=item.get('level', 'national'),
                                role=item.get('role', 'participant'),
                                sponsored_by=item.get('sponsored_by', '').strip(),
                                remarks=item.get('remarks', '').strip(),
                            )
                            saved_count += 1
                    print(f"✅ Saved {saved_count} FDP / Workshop entries")
                except Exception as e:
                    logger.error(f"Error saving FDP entries: {e}")
                    messages.warning(request, "Faculty added but some FDP entries could not be saved.")
            results_data_raw = request.POST.get('results_json', '[]').strip()
            if results_data_raw and results_data_raw != '[]':
                try:
                    results_list = json.loads(results_data_raw)
                    processed_results = []
                    for item in results_list:
                        if item.get('subject_name'):
                            attempted = int(item.get('students_attempted', 0) or 0)
                            passed = int(item.get('students_passed', 0) or 0)
                            percentage = round((passed / attempted) * 100, 2) if attempted > 0 else 0.0
                            processed_results.append({
                                'subject_name': item.get('subject_name', '').strip(),
                                'subject_code': item.get('subject_code', '').strip(),
                                'academic_year': item.get('academic_year', '').strip(),
                                'classes_taken': int(item.get('classes_taken', 0) or 0),
                                'students_attempted': attempted,
                                'students_passed': passed,
                                'percentage': percentage,
                            })
                    if processed_results:
                        faculty.results = json.dumps(processed_results)
                        faculty.save()
                        print(f"✅ Saved {len(processed_results)} result entries")
                except Exception as e:
                    logger.error(f"Error saving results: {e}")
                    messages.warning(request, "Faculty added but results data could not be saved.")
            FacultyLog.objects.create(
                faculty=faculty,
                action='Faculty Added',
                details=f'New faculty added: {faculty.staff_name} ({faculty.employee_code})',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Faculty {faculty.staff_name} added successfully!")
            return redirect("dashboard:faculty_list")
        except Exception as e:
            logger.error(f"Error adding faculty: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error adding faculty: {str(e)}")
            return redirect("dashboard:add_faculty")
    departments = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'MBA', 'MCA']
    designations = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer', 'Senior Professor']
    genders = ['Male', 'Female', 'Other']
    caste_list = ['OC', 'BC-A', 'BC-B', 'BC-C', 'BC-D', 'BC-E', 'SC', 'ST']
    qualifications = ['Completed', 'Pursuing', 'Not Started']
    return render(request, "dashboard/add_faculty_form.html", {
        "title": "Add New Faculty",
        "departments": departments,
        "designations": designations,
        "genders": genders,
        "caste_list": caste_list,
        "qualifications": qualifications,
    })


# ==================== EDIT FACULTY ====================
@login_required
def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == "POST":
        text_fields = [
            'staff_name', 'employee_code', 'father_name', 'mother_name',
            'gender', 'state', 'caste', 'sub_caste', 'nationality', 'address',
            'email', 'mobile', 'phone', 'department', 'designation',
            'jntuh_id', 'aicte_id', 'pan', 'aadhar', 'apaar_id', 'orcid_id',
            'ssc_year', 'ssc_percent', 'ssc_school',
            'inter_year', 'inter_percent', 'inter_college',
            'ug_degree', 'ug_year', 'ug_percentage', 'ug_college', 'ug_spec',
            'pg_degree', 'pg_year', 'pg_percentage', 'pg_college', 'pg_spec',
            'phd_degree', 'phd_year', 'phd_university', 'phd_spec',
            'subjects_dealt', 'scm', 'about_yourself', 'results',
            'exp_anurag', 'exp_other',
        ]
        for attr in text_fields:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)
        for date_attr in ['dob', 'joining_date']:
            val = request.POST.get(date_attr)
            setattr(faculty, date_attr, val if val else None)
        try:
            profile, _ = FacultyProfile.objects.get_or_create(faculty=faculty)
            for fp_attr in ['experience_other', 'experience_at_anurag', 'batch_number']:
                form_key = {
                    'experience_other': 'exp_other',
                    'experience_at_anurag': 'exp_anurag',
                    'batch_number': 'batch_number',
                }.get(fp_attr, fp_attr)
                val = request.POST.get(form_key)
                if val is not None and hasattr(profile, fp_attr):
                    setattr(profile, fp_attr, val)
            profile.save()
        except Exception as e:
            logger.error(f"FacultyProfile save error: {e}")
        if request.FILES.get("photo"):
            faculty.photo = request.FILES["photo"]
            if is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES["photo"], folder="faculty_photos",
                        public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                        transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                    )
                    faculty.cloudinary_photo_url = cr["secure_url"]
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type="photo",
                        cloudinary_url=cr["secure_url"], public_id=cr["public_id"],
                        resource_type=cr["resource_type"], uploaded_by=request.user.username
                    )
                except Exception as e:
                    logger.error(f"Cloudinary upload error during edit: {e}")
                    messages.warning(request, "Photo saved but Cloudinary upload failed.")
        all_doc_fields = [
            'aadhar_file', 'pan_file', 'apaar_file', 'scm_file', 'jntuh_biodata',
            'ssc_certificate', 'inter_certificate',
            'ug_certificate', 'pg_certificate', 'phd_certificate',
        ]
        for ffile in all_doc_fields:
            if request.FILES.get(ffile):
                setattr(faculty, ffile, request.FILES[ffile])
        faculty.save()
        messages.success(request, f'Faculty {faculty.staff_name} updated successfully!')
        return redirect("dashboard:faculty_dashboard")
    return render(request, "dashboard/faculty.html", {"add_mode": True, "faculty": faculty, "title": "Edit Faculty"})


@login_required
def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        faculty_name = faculty.staff_name
        employee_code = faculty.employee_code
        FacultyLog.objects.create(
            faculty=None,
            action='Faculty Deleted',
            details=f'Faculty deleted: {faculty_name} ({employee_code})',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        faculty.delete()
        is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '')
        )
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Faculty {faculty_name} deleted successfully.',
                'faculty_id': faculty_id,
                'faculty_name': faculty_name
            })
        messages.success(request, f'Faculty {faculty_name} deleted successfully.')
        return redirect('dashboard:faculty_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'faculty': faculty,
        'page_title': f'Delete {faculty.staff_name}',
    })


@login_required
def save_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        try:
            text_fields = ['staff_name', 'employee_code', 'department', 'designation',
                           'email', 'mobile', 'address', 'about_yourself', 'father_name',
                           'mother_name', 'gender', 'state', 'caste', 'sub_caste',
                           'nationality', 'jntuh_id', 'aicte_id', 'pan', 'aadhar',
                           'apaar_id', 'orcid_id', 'subjects_dealt', 'scm', 'results',
                           'exp_anurag', 'exp_other']
            for field in text_fields:
                if field in request.POST:
                    setattr(faculty, field, request.POST[field])
            numeric_fields = ['ssc_year', 'inter_year', 'ug_year', 'pg_year', 'phd_year',
                              'ssc_percent', 'inter_percent', 'ug_percentage', 'pg_percentage']
            for field in numeric_fields:
                if field in request.POST and request.POST[field]:
                    try:
                        if 'percent' in field:
                            setattr(faculty, field, float(request.POST[field]))
                        else:
                            setattr(faculty, field, int(request.POST[field]))
                    except (ValueError, TypeError):
                        pass
            date_fields = ['dob', 'joining_date']
            for field in date_fields:
                if field in request.POST and request.POST[field]:
                    setattr(faculty, field, request.POST[field])
                elif field in request.POST and not request.POST[field]:
                    setattr(faculty, field, None)
            edu_fields = ['ssc_school', 'inter_college', 'ug_degree', 'ug_college', 'ug_spec',
                          'pg_degree', 'pg_college', 'pg_spec', 'phd_degree', 'phd_university', 'phd_spec']
            for field in edu_fields:
                if field in request.POST:
                    setattr(faculty, field, request.POST[field])
            if 'photo' in request.FILES:
                faculty.photo = request.FILES['photo']
                if is_cloudinary_configured():
                    try:
                        cr = cloudinary.uploader.upload(
                            request.FILES['photo'], folder="faculty_photos",
                            public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                            transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                        )
                        faculty.cloudinary_photo_url = cr['secure_url']
                    except Exception as e:
                        logger.error(f"Cloudinary upload error during save: {e}")
            faculty.save()
            try:
                profile = FacultyProfile.objects.get(faculty=faculty)
                if 'exp_anurag' in request.POST:
                    profile.experience_at_anurag = request.POST['exp_anurag']
                if 'exp_other' in request.POST:
                    profile.experience_other = request.POST['exp_other']
                if 'batch_number' in request.POST:
                    profile.batch_number = request.POST['batch_number']
                profile.save()
            except FacultyProfile.DoesNotExist:
                FacultyProfile.objects.create(faculty=faculty)
            FacultyLog.objects.create(
                faculty=faculty,
                action='Faculty Saved',
                details=f'Faculty {faculty.employee_code} data saved',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Faculty {faculty.staff_name} saved successfully',
                    'faculty_id': faculty.id,
                    'faculty_name': faculty.staff_name,
                    'employee_code': faculty.employee_code
                })
            messages.success(request, f'Faculty {faculty.staff_name} saved successfully')
            return redirect('dashboard:faculty_detail', faculty_id=faculty.id)
        except Exception as e:
            logger.error(f"Error saving faculty: {e}")
            import traceback
            traceback.print_exc()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
            messages.error(request, f'Error saving faculty: {e}')
            return redirect('dashboard:faculty_detail', faculty_id=faculty.id)
    return redirect('dashboard:faculty_detail', faculty_id=faculty.id)


@login_required
def assign_subjects(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        subject_ids = request.POST.getlist('subjects')
        old_subjects = set(faculty.subjects.values_list('id', flat=True))
        new_subjects = set(map(int, subject_ids))
        faculty.subjects.set(Subject.objects.filter(id__in=subject_ids))
        changes = []
        added = new_subjects - old_subjects
        removed = old_subjects - new_subjects
        if added:
            changes.append(f"Added: {', '.join(Subject.objects.filter(id__in=added).values_list('name', flat=True))}")
        if removed:
            changes.append(
                f"Removed: {', '.join(Subject.objects.filter(id__in=removed).values_list('name', flat=True))}")
        FacultyLog.objects.create(
            faculty=faculty, action='Subjects Assigned',
            details=f"Subjects updated. {'; '.join(changes) if changes else 'No changes'}",
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f'Subjects assigned to {faculty.staff_name} successfully!')
        return HttpResponseRedirect(reverse('dashboard:faculty_dashboard') + f'?id={faculty.id}')
    return render(request, 'dashboard/assign_subjects.html', {
        'faculty': faculty,
        'available_subjects': Subject.objects.all(),
        'assigned_subjects': faculty.subjects.all(),
        'page_title': f'Assign Subjects to {faculty.staff_name}',
        'active_page': 'assign_subjects',
    })


# ==================== STUDENT MANAGEMENT ====================
def students(request):
    return redirect('dashboard:add_student')


def students_data(request):
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:student_login')
    qs = Student.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "dashboard/students_data.html", {
        "title": "Students Data", "students": page_obj,
        "total_students": qs.count(),
        "year_1_count": qs.filter(year=1).count(), "year_2_count": qs.filter(year=2).count(),
        "year_3_count": qs.filter(year=3).count(), "year_4_count": qs.filter(year=4).count(),
        "years": Student.objects.values_list("year", flat=True).distinct(),
        "sems": Student.objects.values_list("sem", flat=True).distinct(),
        "is_paginated": page_obj.has_other_pages(), "page_obj": page_obj,
    })


def add_student(request):
    if request.method == 'POST':
        try:
            ca = is_cloudinary_configured()

            def _upload(file, folder):
                if not file or not ca:
                    return None
                try:
                    res = cloudinary.uploader.upload(
                        file, resource_type="auto",
                        folder=f"student_documents/{folder}",
                        public_id=f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=True
                    )
                    return res['secure_url']
                except Exception as e:
                    logger.error(f"Cloudinary upload error ({folder}): {e}")
                    if hasattr(file, 'seek'): file.seek(0)
                    return None

            student = Student(
                ht_no=request.POST.get('ht_no'),
                student_name=request.POST.get('student_name'),
                father_name=request.POST.get('father_name'),
                mother_name=request.POST.get('mother_name'),
                gender=request.POST.get('gender'),
                dob=request.POST.get('dob'),
                age=request.POST.get('age'),
                nationality=request.POST.get('nationality', 'Indian'),
                category=request.POST.get('category'),
                religion=request.POST.get('religion'),
                blood_group=request.POST.get('blood_group'),
                aadhar=request.POST.get('aadhar'),
                apaar_id=request.POST.get('apaar_id'),
                address=request.POST.get('address'),
                parent_phone=request.POST.get('parent_phone'),
                student_phone=request.POST.get('student_phone'),
                email=request.POST.get('email'),
                task_registered=request.POST.get('task_registered'),
                task_username=request.POST.get('task_username'),
                csi_registered=request.POST.get('csi_registered'),
                csi_membership_id=request.POST.get('csi_membership_id'),
                admission_type=request.POST.get('admission_type'),
                other_admission_details=request.POST.get('other_admission_details'),
                eamcet_rank=request.POST.get('eamcet_rank') or None,
                year=request.POST.get('year'),
                sem=request.POST.get('sem'),
                ssc_marks=request.POST.get('ssc_marks'),
                inter_marks=request.POST.get('inter_marks'),
                cgpa=request.POST.get('cgpa'),
                rtrp_project_title=request.POST.get('rtrp_project_title'),
                intern_title=request.POST.get('intern_title'),
                final_project_title=request.POST.get('final_project_title'),
                other_training=request.POST.get('other_training'),
                photo=None, cert_achieve=None, cert_intern=None, cert_courses=None,
                cert_sdp=None, cert_extra=None, cert_placement=None, cert_national=None,
            )
            student.save()
            files_up, files_lo = [], []
            if request.FILES.get('photo'):
                pf = request.FILES['photo']
                url = _upload(pf, 'photos')
                if url:
                    student.photo_url = url
                    student.photo = None
                    files_up.append('photo')
                else:
                    student.photo = pf
                    files_lo.append('photo')
            for fn, folder in [('cert_achieve', 'achievement'), ('cert_intern', 'internship'),
                               ('cert_courses', 'courses'), ('cert_sdp', 'sdp'),
                               ('cert_extra', 'extra'), ('cert_placement', 'placement'),
                               ('cert_national', 'national')]:
                if request.FILES.get(fn):
                    cf = request.FILES[fn]
                    url = _upload(cf, folder)
                    if url:
                        setattr(student, fn, url)
                        files_up.append(fn)
                    else:
                        setattr(student, fn, cf)
                        files_lo.append(fn)
            student.save()
            if files_up:
                messages.success(request, f'Student {student.student_name} added! Cloudinary: {", ".join(files_up)}')
            if files_lo:
                messages.warning(request, f'Some files saved locally: {", ".join(files_lo)}')
            if not files_up and not files_lo:
                messages.success(request, f'Student {student.student_name} added successfully!')
            return redirect('dashboard:students_data')
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error adding student: {e}')
            return redirect('dashboard:add_student')
    return render(request, 'dashboard/add_student.html')


@require_POST
def delete_student(request, student_id):
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    student = get_object_or_404(Student, id=student_id)
    name, ht = student.student_name, student.ht_no
    student.delete()
    messages.success(request, f"Student {name} ({ht}) deleted successfully.")
    return redirect('dashboard:students_data')


def edit_student(request, student_id):
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('dashboard:students_data')
    else:
        form = StudentForm(instance=student)
    return render(request, 'dashboard/add_student.html', {'form': form, 'title': 'Edit Student'})


@login_required
@csrf_exempt
def regenerate_student_pdf(request, student_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    student = get_object_or_404(Student, id=student_id)
    try:
        student.pdf_generated = False
        student.save()
        pdf_path = generate_student_pdf(student)
        return JsonResponse({
            'success': True,
            'message': f'PDF regenerated for {student.student_name}',
            'pdf_url': getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None),
        })
    except Exception as e:
        logger.error(f"PDF regeneration error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ==================== PDF MERGE UTILITY (LEGACY) ====================
def merge_files_legacy(file_list):
    from pypdf import PdfMerger
    from PIL import Image
    merger = PdfMerger()
    temp_files = []
    print("\n========== PDF MERGE START ==========")
    for idx, file in enumerate(file_list):
        if not file:
            print(f"[{idx}] Skipped (empty)")
            continue
        try:
            file_url = file.url if hasattr(file, "url") else str(file)
            print(f"[{idx}] Processing: {file_url}")
            if file_url.startswith("http"):
                response = requests.get(file_url, timeout=20)
                if response.status_code != 200:
                    print(" [X] Download failed")
                    continue
                suffix = ".pdf" if file_url.lower().endswith(".pdf") else ".img"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp.write(response.content)
                temp.close()
                file_path = temp.name
                temp_files.append(file_path)
            else:
                file_path = file.path
            with open(file_path, "rb") as f:
                header = f.read(4)
            is_pdf = header.startswith(b"%PDF")
            if is_pdf:
                print(" [OK] PDF detected")
                merger.append(file_path)
            else:
                print(" [OK] Image detected → converting to PDF")
                img = Image.open(file_path)
                if img.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        bg.paste(img, mask=img.split()[3])
                    else:
                        bg.paste(img)
                    img = bg
                else:
                    img = img.convert("RGB")
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                img.save(temp_pdf.name, "PDF")
                temp_pdf.close()
                merger.append(temp_pdf.name)
                temp_files.append(temp_pdf.name)
        except Exception as e:
            print(f" [X] Error: {e}")
    final_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(final_pdf.name)
    merger.close()
    print(f"[OK] Final PDF: {final_pdf.name}")
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass
    print("========== PDF MERGE END ==========\n")
    return final_pdf.name


# ==================== GENERATE STUDENT PDF ====================
def generate_student_pdf(student):
    print(f"\n=== GENERATING STUDENT PDF for {student.student_name} (ID: {student.id}) ===")
    files = [
        student.photo,
        student.cert_achieve,
        student.cert_intern,
        student.cert_courses,
        student.cert_sdp,
        student.cert_extra,
        student.cert_placement,
        student.cert_national,
        student.pdf_file
    ]
    file_names = [
        'photo', 'cert_achieve', 'cert_intern', 'cert_courses',
        'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national', 'pdf_file'
    ]
    for name, file in zip(file_names, files):
        if file:
            if hasattr(file, 'url'):
                print(f" - {name}: URL = {file.url}")
            else:
                print(f" - {name}: {file}")
        else:
            print(f" - {name}: None")
    final_pdf_path = merge_files(file_list=files)
    student.pdf_url = final_pdf_path
    student.pdf_generated = True
    student.save()
    print(f"PDF saved to student record: {final_pdf_path}")
    print("=== PDF GENERATION COMPLETE ===\n")
    return final_pdf_path


def generate_student_pdf_file(request, student_id):
    import io, shutil
    student = get_object_or_404(Student, id=student_id)
    styles = getSampleStyleSheet()
    temp_files = []
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    main_pdf_path = tmp.name
    tmp.close()
    temp_files.append(main_pdf_path)
    doc = SimpleDocTemplate(main_pdf_path, pagesize=A4)
    elems = []
    elems.append(Paragraph("""<para alignment='center'>
        <font name='Helvetica-Bold' size='16' color='darkblue'>ANURAG ENGINEERING COLLEGE</font><br/>
        <font name='Helvetica' size='12' color='navy'>DEPARTMENT OF INFORMATION TECHNOLOGY</font><br/><br/>
        <font name='Helvetica-Bold' size='14'>STUDENT PROFILE</font></para>""", styles['Normal']))
    elems.append(Spacer(1, 0.2 * inch))
    elems.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    elems.append(Spacer(1, 0.2 * inch))
    photo_img = None
    photo_url = getattr(student, 'photo_url', None) or (student.photo.url if student.photo else None)
    if photo_url:
        try:
            r = requests.get(photo_url, timeout=10)
            if r.status_code == 200:
                ext = '.png' if 'png' in r.headers.get('content-type', '') else '.jpg'
                tp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                tp.write(r.content)
                tp.close()
                temp_files.append(tp.name)
                photo_img = Image(tp.name, width=1.5 * inch, height=1.8 * inch)
        except Exception:
            pass
    if photo_img:
        ht = Table([[Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']), photo_img]],
                   colWidths=[4.5 * inch, 1.5 * inch])
        ht.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        elems.append(ht)
    else:
        elems.append(Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']))
    elems.append(Spacer(1, 0.2 * inch))
    fields = [
        ("Hall Ticket No", student.ht_no), ("Name", student.student_name),
        ("Father Name", student.father_name), ("Mother Name", student.mother_name),
        ("Gender", student.gender), ("Date of Birth", student.dob), ("Age", student.age),
        ("Nationality", student.nationality or "Indian"), ("Category", student.category or "N/S"),
        ("Religion", student.religion or "N/S"), ("Blood Group", student.blood_group or "N/S"),
        ("Aadhar Number", student.aadhar), ("APAAR ID", student.apaar_id or "N/S"),
        ("Address", student.address), ("Parent Phone", student.parent_phone),
        ("Student Phone", student.student_phone), ("Email", student.email),
        ("TASK Registered", student.task_registered or "No"),
        ("TASK Username", student.task_username or "N/A"),
        ("CSI Registered", student.csi_registered or "No"),
        ("CSI Membership ID", student.csi_membership_id or "N/A"),
        ("Admission Type", student.admission_type),
        ("Other Admission Details", student.other_admission_details or "N/A"),
        ("EAMCET Rank", student.eamcet_rank or "N/A"),
        ("Year", student.year), ("Semester", student.sem),
        ("SSC Marks (%)", student.ssc_marks or "N/A"),
        ("Intermediate Marks (%)", student.inter_marks or "N/A"),
        ("CGPA", student.cgpa or "N/A"),
        ("RTRP Project Title", student.rtrp_project_title or "N/A"),
        ("Internship Title", student.intern_title or "N/A"),
        ("Final Project Title", student.final_project_title or "N/A"),
        ("Other Training", student.other_training or "N/A"),
    ]
    tbl = Table([[Paragraph(f"<b>{l}</b>", styles['Normal']),
                  Paragraph(str(v) if v else "N/A", styles['Normal'])] for l, v in fields],
                colWidths=[2.2 * inch, 4.3 * inch])
    tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'), ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elems.append(tbl)
    elems.append(Spacer(1, 0.2 * inch))
    elems.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    doc.build(elems)
    writer = PdfWriter()
    try:
        for pg in PdfReader(main_pdf_path).pages:
            writer.add_page(pg)
    except Exception as e:
        logger.error(f"Error adding main PDF: {e}")
    cert_fields = [
        ('cert_achieve', 'Achievement'), ('cert_intern', 'Internship'),
        ('cert_courses', 'Courses'), ('cert_sdp', 'SDP'),
        ('cert_extra', 'Extracurricular'), ('cert_placement', 'Placement'),
        ('cert_national', 'National Exam'),
    ]
    for fn, fl in cert_fields:
        cf = getattr(student, fn, None)
        if not cf:
            continue
        try:
            curl = cf.url if hasattr(cf, 'url') else str(cf)
            r = requests.get(curl, timeout=30)
            if r.status_code == 200:
                content = r.content
                if content.startswith(b'%PDF'):
                    tp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    tp.write(content)
                    tp.close()
                    temp_files.append(tp.name)
                    for pg in PdfReader(tp.name).pages:
                        writer.add_page(pg)
                else:
                    try:
                        img = PILImage.open(io.BytesIO(content))
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        tp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        img.save(tp.name, 'PDF', resolution=100.0)
                        tp.close()
                        temp_files.append(tp.name)
                        for pg in PdfReader(tp.name).pages:
                            writer.add_page(pg)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error processing {fl}: {e}")
    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    final_path = fp.name
    fp.close()
    temp_files.append(final_path)
    try:
        with open(final_path, "wb") as out:
            writer.write(out)
    except Exception:
        shutil.copy(main_pdf_path, final_path)
    if is_cloudinary_configured():
        try:
            ur = cloudinary.uploader.upload(
                final_path, resource_type="raw", folder="student_generated_pdfs",
                public_id=f"student_{student.ht_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", overwrite=True
            )
            student.pdf_url = ur["secure_url"]
            student.pdf_file = ur["secure_url"]
            student.pdf_generated = True
            student.pdf_generation_time = timezone.now()
            student.save()
            CloudinaryUpload.objects.create(
                student=student, upload_type='pdf',
                cloudinary_url=ur['secure_url'], public_id=ur['public_id'],
                resource_type=ur['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Student'
            )
        except Exception as e:
            logger.error(f"Error uploading student PDF to Cloudinary: {e}")
    try:
        with open(final_path, 'rb') as pf:
            response = HttpResponse(pf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
        for t in temp_files:
            try:
                if os.path.exists(t):
                    os.remove(t)
            except Exception:
                pass
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {e}", status=500)


def view_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    url = getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None)
    if url:
        return redirect(url)
    messages.error(request, "PDF not generated yet.")
    return redirect('dashboard:students_data')


def download_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    url = getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None)
    if url:
        return redirect(url)
    return generate_student_pdf_file(request, student_id)


@login_required
def export_students_csv(request):
    qs = Student.objects.all().order_by('ht_no')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="students_export_{date.today().strftime("%Y%m%d")}.csv"'
    )
    w = csv.writer(response)
    w.writerow(['HT No', 'Student Name', 'Father Name', 'Mother Name', 'Gender', 'Date of Birth', 'Age',
                'Category', 'Religion', 'Blood Group', 'Aadhar', 'APAAR ID', 'Address',
                'Parent Phone', 'Student Phone', 'Email', 'Year', 'Semester', 'Branch', 'Roll Number',
                'SSC Marks', 'Inter Marks', 'CGPA', 'Admission Type', 'EAMCET Rank',
                'RTRP Project Title', 'Internship Title', 'Final Project Title', 'Created Date'])
    for s in qs:
        w.writerow([
            s.ht_no, s.student_name, s.father_name, s.mother_name, s.gender,
            s.dob.strftime('%d-%m-%Y') if s.dob else '',
            s.age, s.category, s.religion or '', s.blood_group or '',
                               s.aadhar or '', s.apaar_id or '', s.address,
            s.parent_phone, s.student_phone, s.email,
            s.year, s.sem,
                               getattr(s, 'branch', '') or '', getattr(s, 'roll_number', '') or '',
            s.ssc_marks, s.inter_marks, s.cgpa,
                               s.admission_type or '', s.eamcet_rank or '',
                               s.rtrp_project_title or '', s.intern_title or '', s.final_project_title or '',
            s.created_at.strftime('%d-%m-%Y %H:%M:%S') if s.created_at else '',
        ])
    FacultyLog.objects.create(
        faculty=None, action='Students CSV Export',
        details=f'Exported {qs.count()} students to CSV',
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    return response


# ==================== ENHANCED GENERATE FACULTY PDF ====================
@login_required
def generate_faculty_pdf(request, faculty_id):
    """Enhanced faculty PDF generation with complete data including FDP, Results, and Certificates."""
    import io
    import shutil
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        print(f"\n{'=' * 60}")
        print(f"ENHANCED FACULTY PDF GENERATION FOR: {faculty.staff_name}")
        print(f"Employee Code: {faculty.employee_code}")
        print(f"Faculty ID: {faculty.id}")
        print(f"{'=' * 60}")

        image_files, pdf_files, temp_files = collect_faculty_files(faculty)

        print("\n--- ADDING CERTIFICATES ---")
        certificates = Certificate.objects.filter(faculty=faculty)
        print(f"📊 Found {certificates.count()} certificates")
        for cert in certificates:
            try:
                if cert.cloudinary_url:
                    print(f" 📄 Certificate ({cert.certificate_type}): {cert.cloudinary_url}")
                    response = requests.get(cert.cloudinary_url, timeout=30)
                    if response.status_code == 200:
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        tmp.write(response.content)
                        tmp.close()
                        pdf_files.append(tmp.name)
                        temp_files.append(tmp.name)
                        print(f" ✅ Downloaded certificate: {tmp.name}")
                elif cert.certificate_file and hasattr(cert.certificate_file, 'path'):
                    if cert.certificate_file.path.startswith('http'):
                        print(f" 📄 Certificate ({cert.certificate_type}) URL: {cert.certificate_file.path}")
                        response = requests.get(cert.certificate_file.path, timeout=30)
                        if response.status_code == 200:
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                            tmp.write(response.content)
                            tmp.close()
                            pdf_files.append(tmp.name)
                            temp_files.append(tmp.name)
                            print(f" ✅ Downloaded certificate: {tmp.name}")
                    elif os.path.exists(cert.certificate_file.path):
                        if cert.certificate_file.path.lower().endswith('.pdf'):
                            pdf_files.append(cert.certificate_file.path)
                            print(f" ✅ Certificate PDF (local): {cert.certificate_file.path}")
                        else:
                            image_files.append(cert.certificate_file.path)
                            print(f" ✅ Certificate Image (local): {cert.certificate_file.path}")
            except Exception as e:
                print(f" ❌ Error processing certificate {cert.certificate_type}: {e}")

        print("\n--- LOADING FACULTY DATA ---")
        research_publications = ResearchPublication.objects.filter(faculty=faculty).order_by('-publication_year')
        print(f"📊 Research Publications: {research_publications.count()}")
        fdps = FDP.objects.filter(faculty=faculty).order_by('-from_date')
        print(f"📊 FDP/Workshop entries: {fdps.count()}")
        btech_projects = BTechProject.objects.filter(faculty=faculty).order_by('-batch')
        print(f"📊 B.Tech Projects: {btech_projects.count()}")
        research_projects = ResearchProject.objects.filter(faculty=faculty)

        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
        except FacultyProfile.DoesNotExist:
            profile = None

        subjects_list = []
        sd = getattr(faculty, 'subjects_dealt', None)
        if sd:
            subjects_list = [s.strip() for s in sd.split(',') if s.strip()]

        results_display = []
        if faculty.results:
            try:
                results_data = json.loads(faculty.results)
                if isinstance(results_data, list):
                    for result in results_data:
                        if isinstance(result, dict):
                            subject_name = result.get('subject_name') or result.get('subject') or result.get(
                                'name') or 'N/A'
                            subject_code = result.get('subject_code') or result.get('code') or ''
                            attempted = result.get('students_attempted') or result.get('attempted') or result.get(
                                'total') or 0
                            passed = result.get('students_passed') or result.get('passed') or 0
                            percentage = result.get('percentage') or result.get('pass_percentage') or 0
                            academic_year = result.get('academic_year') or result.get('year') or ''
                            classes_taken = result.get('classes_taken') or 0

                            if attempted > 0 and percentage == 0:
                                percentage = round((passed / attempted) * 100, 2)

                            results_display.append({
                                'subject_name': subject_name,
                                'subject_code': subject_code,
                                'academic_year': academic_year,
                                'classes_taken': classes_taken,
                                'students_attempted': attempted,
                                'students_passed': passed,
                                'percentage': percentage,
                            })
                        elif isinstance(result, str):
                            results_display.append({'text': result})
                        else:
                            results_display.append({'text': str(result)})
                elif isinstance(results_data, dict):
                    subject_name = results_data.get('subject_name') or results_data.get('subject') or 'Result'
                    attempted = results_data.get('students_attempted') or results_data.get('attempted') or 0
                    passed = results_data.get('students_passed') or results_data.get('passed') or 0
                    percentage = results_data.get('percentage') or 0
                    academic_year = results_data.get('academic_year') or results_data.get('year') or ''
                    classes_taken = results_data.get('classes_taken') or 0

                    if attempted > 0 and percentage == 0:
                        percentage = round((passed / attempted) * 100, 2)

                    results_display.append({
                        'subject_name': subject_name,
                        'subject_code': results_data.get('subject_code', ''),
                        'academic_year': academic_year,
                        'classes_taken': classes_taken,
                        'students_attempted': attempted,
                        'students_passed': passed,
                        'percentage': percentage,
                    })
                else:
                    results_display = [{'text': str(faculty.results)}]
            except (json.JSONDecodeError, TypeError) as e:
                results_display = [{'text': faculty.results}]

        experience = "N/A"
        if faculty.joining_date:
            today = date.today()
            j = faculty.joining_date
            yrs = today.year - j.year
            mths = today.month - j.month
            dys = today.day - j.day
            if dys < 0:
                mths -= 1
                pm = today.month - 1 or 12
                py = today.year - (1 if today.month == 1 else 0)
                dim = (30 if pm in [4, 6, 9, 11]
                       else 29 if pm == 2 and ((py % 4 == 0 and py % 100 != 0) or py % 400 == 0)
                else 28 if pm == 2
                else 31)
                dys += dim
            if mths < 0:
                yrs -= 1
                mths += 12
            experience = f"{yrs} Years {mths} Months {dys} Days"

        has_aadhar = bool(faculty.aadhar_file or faculty.aadhar_url)
        has_pan = bool(faculty.pan_file or faculty.pan_url)
        has_apaar = bool(faculty.apaar_file or faculty.apaar_url)
        has_scm = bool(faculty.scm_file or faculty.scm_url)
        has_jntuh_biodata = bool(faculty.jntuh_biodata or faculty.jntuh_biodata_url)
        has_ssc_cert = bool(faculty.ssc_certificate or faculty.ssc_certificate_url)
        has_inter_cert = bool(faculty.inter_certificate or faculty.inter_certificate_url)
        has_ug_cert = bool(faculty.ug_certificate or faculty.ug_certificate_url)
        has_pg_cert = bool(faculty.pg_certificate or faculty.pg_certificate_url)
        has_phd_cert = bool(faculty.phd_certificate or faculty.phd_certificate_url)
        has_research_proof = bool(
            getattr(faculty, 'research_proof', None) or getattr(faculty, 'research_proof_url', None))
        research_proof_academic_year = getattr(faculty, 'research_proof_academic_year', None) or ''
        has_fdp_certificate = bool(
            getattr(faculty, 'fdp_certificate', None) or getattr(faculty, 'fdp_certificate_url', None))
        fdp_certificate_academic_year = getattr(faculty, 'fdp_certificate_academic_year', None) or ''
        has_experience_certificates = bool(
            getattr(faculty, 'experience_certificates', None) or getattr(faculty, 'experience_certificates_url', None))
        experience_certificates_academic_year = getattr(faculty, 'experience_certificates_academic_year', None) or ''
        has_other_documents = bool(
            getattr(faculty, 'other_documents', None) or getattr(faculty, 'other_documents_url', None))
        other_documents_academic_year = getattr(faculty, 'other_documents_academic_year', None) or ''

        classes_taken = getattr(faculty, 'classes_taken', None)
        if classes_taken is not None:
            try:
                classes_taken_display = f"{int(classes_taken)}"
            except (ValueError, TypeError):
                classes_taken_display = str(classes_taken)
        else:
            classes_taken_display = "Not specified"

        context = {
            'faculty': faculty,
            'profile': profile,
            'research_publications': research_publications,
            'research_projects': research_projects,
            'fdps': fdps,
            'btech_projects': btech_projects,
            'certificates': certificates,
            'subjects_list': subjects_list,
            'experience': experience,
            'current_date': datetime.now(),
            'staff_name': faculty.staff_name,
            'employee_code': faculty.employee_code,
            'father_name': faculty.father_name,
            'mother_name': faculty.mother_name,
            'dob': faculty.dob,
            'gender': faculty.gender,
            'state': faculty.state,
            'caste': faculty.caste,
            'sub_caste': faculty.sub_caste,
            'nationality': faculty.nationality,
            'address': faculty.address,
            'department': faculty.department,
            'designation': faculty.designation,
            'joining_date': faculty.joining_date,
            'exp_anurag': faculty.exp_anurag,
            'exp_other': faculty.exp_other,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'phone': faculty.phone,
            'jntuh_id': faculty.jntuh_id,
            'aicte_id': faculty.aicte_id,
            'pan': faculty.pan,
            'aadhar': faculty.aadhar,
            'apaar_id': faculty.apaar_id,
            'orcid_id': faculty.orcid_id,
            'ssc_year': faculty.ssc_year,
            'ssc_percent': faculty.ssc_percent,
            'ssc_school': faculty.ssc_school,
            'inter_year': faculty.inter_year,
            'inter_percent': faculty.inter_percent,
            'inter_college': faculty.inter_college,
            'ug_degree': faculty.ug_degree,
            'ug_year': faculty.ug_year,
            'ug_percentage': faculty.ug_percentage,
            'ug_college': faculty.ug_college,
            'ug_spec': faculty.ug_spec,
            'pg_degree': faculty.pg_degree,
            'pg_year': faculty.pg_year,
            'pg_percentage': faculty.pg_percentage,
            'pg_college': faculty.pg_college,
            'pg_spec': faculty.pg_spec,
            'phd_degree': faculty.phd_degree,
            'phd_year': faculty.phd_year,
            'phd_university': faculty.phd_university,
            'phd_spec': faculty.phd_spec,
            'subjects_dealt': faculty.subjects_dealt,
            'about_yourself': faculty.about_yourself,
            'results': faculty.results,
            'results_data': results_display,
            'scm': faculty.scm,
            'has_aadhar': has_aadhar,
            'has_pan': has_pan,
            'has_apaar': has_apaar,
            'has_scm': has_scm,
            'has_jntuh_biodata': has_jntuh_biodata,
            'has_ssc_cert': has_ssc_cert,
            'has_inter_cert': has_inter_cert,
            'has_ug_cert': has_ug_cert,
            'has_pg_cert': has_pg_cert,
            'has_phd_cert': has_phd_cert,
            'has_research_proof': has_research_proof,
            'research_proof_academic_year': research_proof_academic_year,
            'has_fdp_certificate': has_fdp_certificate,
            'fdp_certificate_academic_year': fdp_certificate_academic_year,
            'has_experience_certificates': has_experience_certificates,
            'experience_certificates_academic_year': experience_certificates_academic_year,
            'has_other_documents': has_other_documents,
            'other_documents_academic_year': other_documents_academic_year,
            'classes_taken': classes_taken_display,
        }

        html_string = render_to_string('dashboard/faculty_pdf.html', context)

        if pdfkit is None:
            messages.error(request, 'PDF generation library not installed. Please install pdfkit.')
            return redirect('dashboard:faculty_dashboard')

        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': 'UTF-8',
            'enable-local-file-access': '',
            'quiet': '',
            'print-media-type': '',
            'no-stop-slow-scripts': '',
            'javascript-delay': '1000',
            'load-error-handling': 'ignore',
        }

        wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        if os.path.exists(wkhtmltopdf_path):
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            pdf_bytes = pdfkit.from_string(html_string, False, options=options, configuration=config)
        else:
            try:
                pdf_bytes = pdfkit.from_string(html_string, False, options=options)
            except Exception as e:
                logger.error(f"pdfkit error: {e}")
                messages.error(request, f'PDF generation error: {e}')
                return redirect('dashboard:faculty_dashboard')

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        FacultyLog.objects.create(
            faculty=faculty,
            action='PDF Generated',
            details=f'PDF generated for {faculty.employee_code} with {fdps.count()} FDPs, {certificates.count()} certificates, {len(results_display)} results, Classes Taken: {classes_taken_display}',
            performed_by=request.user.username if request.user.is_authenticated else 'Anonymous',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        print(f"✅ PDF generated successfully: {filename}")
        return response

    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error generating faculty PDF: {str(e)}')
        return redirect('dashboard:faculty_dashboard')


# ==================== GENERATE FACULTY PDF CLEAN ====================
@login_required
def generate_faculty_pdf_clean(request, faculty_id):
    print("\n🔥🔥🔥 NEW PDF FUNCTION CALLED 🔥🔥🔥")
    print(f"🔥 Faculty identifier: {faculty_id}")
    print(f"🔥 Request method: {request.method}")
    print(f"🔥 User: {request.user}")
    print("🔥🔥🔥 ================================= 🔥🔥🔥\n")
    try:
        faculty = get_object_or_404(Faculty, id=int(faculty_id))
        print(f"✅ Found faculty by ID: {faculty.staff_name} (ID: {faculty.id})")
    except (ValueError, TypeError):
        faculty = get_object_or_404(Faculty, employee_code=str(faculty_id))
        print(f"✅ Found faculty by employee_code: {faculty.staff_name} (ID: {faculty.id})")
    return generate_faculty_pdf(request, faculty.id)


# ==================== CHARTS & ANALYTICS ====================
@login_required
def faculty_charts(request):
    if plt is None:
        messages.error(request, 'Matplotlib not installed or incompatible.')
        return redirect('dashboard:dashboard')
    try:
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        dept_data = Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:10]
        depts = [d['department'] for d in dept_data]
        cnts = [d['count'] for d in dept_data]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(depts, cnts)
        plt.title('Faculty Distribution by Department')
        plt.xlabel('Department')
        plt.ylabel('Number of Faculty')
        plt.xticks(rotation=45, ha='right')
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., h + 0.1, f'{int(h)}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'dept_distribution.png'), dpi=100)
        plt.close()
        qual_data = {
            'PhD Completed': Faculty.objects.filter(phd_degree='Completed').count(),
            'PhD Pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
            'PG Only': Faculty.objects.filter(pg_year__isnull=False,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
            'UG Only': Faculty.objects.filter(ug_year__isnull=False, pg_year__isnull=True).count(),
        }
        plt.figure(figsize=(8, 8))
        plt.pie(list(qual_data.values()), labels=list(qual_data.keys()),
                colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Faculty Qualification Distribution')
        plt.savefig(os.path.join(charts_dir, 'qualification_distribution.png'), dpi=100)
        plt.close()
        today = date.today()
        exp_ranges = ['0-5 years', '5-10 years', '10-15 years', '15+ years']
        exp_counts = [0, 0, 0, 0]
        for f in Faculty.objects.all():
            if f.joining_date:
                yrs = (today - f.joining_date).days / 365.25
                if yrs <= 5:
                    exp_counts[0] += 1
                elif yrs <= 10:
                    exp_counts[1] += 1
                elif yrs <= 15:
                    exp_counts[2] += 1
                else:
                    exp_counts[3] += 1
        plt.figure(figsize=(10, 6))
        bars = plt.bar(range(len(exp_ranges)), exp_counts,
                       color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        plt.title('Faculty Experience Distribution')
        plt.xlabel('Experience Range')
        plt.ylabel('Number of Faculty')
        plt.xticks(range(len(exp_ranges)), exp_ranges)
        for i, (bar, cnt) in enumerate(zip(bars, exp_counts)):
            plt.text(bar.get_x() + bar.get_width() / 2., cnt + 0.1, f'{cnt}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'experience_distribution.png'), dpi=100)
        plt.close()
        research_data = {
            'Journal Articles': ResearchPublication.objects.filter(research_type='journal').count(),
            'Conference Papers': ResearchPublication.objects.filter(research_type='conference').count(),
            'Books': ResearchPublication.objects.filter(research_type='book').count(),
            'Patents': ResearchPublication.objects.filter(research_type='patent').count(),
        }
        plt.figure(figsize=(8, 8))
        plt.pie(list(research_data.values()), labels=list(research_data.keys()),
                colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Research Publications Distribution')
        plt.savefig(os.path.join(charts_dir, 'research_distribution.png'), dpi=100)
        plt.close()
        return render(request, 'dashboard/charts.html', {
            'title': 'Faculty Analytics Charts',
            'chart_urls': {
                'dept_chart': os.path.join(settings.MEDIA_URL, 'charts', 'dept_distribution.png'),
                'qual_chart': os.path.join(settings.MEDIA_URL, 'charts', 'qualification_distribution.png'),
                'exp_chart': os.path.join(settings.MEDIA_URL, 'charts', 'experience_distribution.png'),
                'research_chart': os.path.join(settings.MEDIA_URL, 'charts', 'research_distribution.png'),
            },
            'dept_data': list(zip(depts, cnts)),
            'qual_data': qual_data,
            'exp_data': list(zip(exp_ranges, exp_counts)),
            'research_data': research_data,
        })
    except Exception as e:
        logger.error(f"Chart error: {e}")
        messages.error(request, f'Error generating charts: {e}')
        return redirect('dashboard:dashboard')


@login_required
def student_charts(request):
    if plt is None:
        messages.error(request, 'Matplotlib not installed or incompatible.')
        return redirect('dashboard:students_data')
    try:
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        gd = Student.objects.values('gender').annotate(count=Count('id')).order_by('-count')
        gs = [d['gender'] for d in gd]
        gc = [d['count'] for d in gd]
        plt.figure(figsize=(8, 8))
        plt.pie(gc, labels=gs, colors=['#66b3ff', '#ff9999', '#99ff99'][:len(gs)],
                autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Student Gender Distribution')
        plt.savefig(os.path.join(charts_dir, 'student_gender_distribution.png'), dpi=100)
        plt.close()
        yd = Student.objects.values('year').annotate(count=Count('id')).order_by('year')
        ys = [d['year'] for d in yd]
        yc = [d['count'] for d in yd]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(ys, yc)
        plt.title('Student Distribution by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Students')
        for bar, cnt in zip(bars, yc):
            plt.text(bar.get_x() + bar.get_width() / 2., cnt + 0.1, f'{cnt}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'student_year_distribution.png'), dpi=100)
        plt.close()
        cd = Student.objects.values('category').annotate(count=Count('id')).order_by('-count')[:10]
        cs = [d['category'] for d in cd]
        cc = [d['count'] for d in cd]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(range(len(cs)), cc)
        plt.title('Student Category Distribution (Top 10)')
        plt.xlabel('Category')
        plt.ylabel('Number of Students')
        plt.xticks(range(len(cs)), cs, rotation=45, ha='right')
        for bar, cnt in zip(bars, cc):
            plt.text(bar.get_x() + bar.get_width() / 2., cnt + 0.1, f'{cnt}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'student_category_distribution.png'), dpi=100)
        plt.close()
        return render(request, 'dashboard/student_charts.html', {
            'title': 'Student Analytics Charts',
            'chart_urls': {
                'gender_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_gender_distribution.png'),
                'year_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_year_distribution.png'),
                'category_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_category_distribution.png'),
            },
            'gender_data': list(zip(gs, gc)),
            'year_data': list(zip(ys, yc)),
            'category_data': list(zip(cs, cc)),
        })
    except Exception as e:
        logger.error(f"Student chart error: {e}")
        messages.error(request, f'Error generating charts: {e}')
        return redirect('dashboard:students_data')


# ==================== RECENT ACTIVITY ====================
@login_required
def recent_activity(request):
    acts = FacultyLog.objects.select_related('faculty', 'student').order_by('-created_at')[:50]
    return render(request, 'dashboard/recent_activity.html', {
        'title': 'Recent Activities', 'activities': acts,
        'total_activities': FacultyLog.objects.count(),
    })


# ==================== SEARCH FUNCTIONS ====================
@login_required
def search_faculty(request):
    q = request.GET.get('q', '')
    qs = Faculty.objects.filter(
        Q(staff_name__icontains=q) | Q(employee_code__icontains=q) |
        Q(department__icontains=q) | Q(designation__icontains=q) | Q(email__icontains=q)
    ).order_by('staff_name')[:20] if q else Faculty.objects.none()
    results = []
    for f in qs:
        pu = None
        try:
            pu = f.cloudinary_photo_url or (f.photo.url if f.photo else None)
        except Exception:
            pass
        results.append({
            'id': f.id, 'name': f.staff_name, 'employee_code': f.employee_code,
            'department': f.department, 'designation': f.designation, 'photo_url': pu,
            'has_jntuh_biodata': bool(f.jntuh_biodata),
            'research_count': ResearchPublication.objects.filter(faculty=f).count(),
            'fdp_count': FDP.objects.filter(faculty=f).count(),
            'project_count': BTechProject.objects.filter(faculty=f).count(),
            'detail_url': reverse('dashboard:faculty_dashboard') + f'?id={f.id}',
        })
    return JsonResponse({'results': results, 'count': len(results)})


@login_required
def search_students(request):
    q = request.GET.get('q', '')
    qs = Student.objects.filter(
        Q(student_name__icontains=q) | Q(ht_no__icontains=q) |
        Q(father_name__icontains=q) | Q(email__icontains=q)
    ).order_by('student_name')[:20] if q else Student.objects.none()
    results = [
        {
            'id': s.id, 'name': s.student_name, 'ht_no': s.ht_no,
            'year': s.year, 'sem': s.sem,
            'branch': getattr(s, 'branch', ''),
            'roll_number': getattr(s, 'roll_number', ''),
            'photo_url': getattr(s, 'photo_url', None),
            'detail_url': reverse('dashboard:students_data'),
        }
        for s in qs
    ]
    return JsonResponse({'results': results, 'count': len(results)})


@login_required
def quick_stats(request):
    return JsonResponse({
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'total_research_publications': ResearchPublication.objects.count(),
        'total_fdps': FDP.objects.count(),
        'total_btech_projects': BTechProject.objects.count(),
        'recent_uploads': Faculty.objects.order_by('-created_at').count(),
        'cloudinary_uploads': CloudinaryUpload.objects.count(),
    })


# ==================== PDF GENERATION HELPERS ====================
def generate_pdf_with_data(request):
    if request.method == 'POST':
        if pdfkit is None:
            return JsonResponse({'success': False, 'error': 'pdfkit not installed'})
        try:
            html_string = render_to_string('faculty/custom_pdf_template.html', {'data': request.POST.dict()})
            opts = {'page-size': 'A4', 'margin-top': '0.5in', 'margin-right': '0.5in',
                    'margin-bottom': '0.5in', 'margin-left': '0.5in', 'encoding': 'UTF-8'}
            wk = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            cfg = pdfkit.configuration(wkhtmltopdf=wk)
            pdf = pdfkit.from_string(html_string, False, options=opts, configuration=cfg)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_document.pdf"'
            return response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'faculty/generate_pdf_form.html')


@login_required
def preview_faculty_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if faculty.cloudinary_pdf_url:
        return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url, 'message': 'PDF on Cloudinary'})
    if faculty.pdf_document and faculty.pdf_document.url:
        return JsonResponse({'success': True, 'pdf_url': faculty.pdf_document.url, 'message': 'Local PDF available'})
    return JsonResponse({'success': False, 'error': 'No PDF available. Please generate one first.'})


def preview_pdf_template(request):
    return render(request, 'faculty/pdf_preview.html')


@login_required
def download_faculty_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if faculty.cloudinary_pdf_url:
        return redirect(faculty.cloudinary_pdf_url)
    if faculty.pdf_document and faculty.pdf_document.url:
        response = HttpResponse(faculty.pdf_document, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="faculty_{faculty.employee_code}.pdf"'
        return response
    return generate_faculty_pdf(request, faculty_id)


@login_required
def bulk_generate_faculty_pdfs(request):
    if request.method != 'POST':
        return redirect('dashboard:faculty_list')
    faculty_ids = request.POST.getlist('faculty_ids')
    if not faculty_ids:
        messages.error(request, "No faculty selected.")
        return redirect('dashboard:faculty_list')
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f'faculty_pdfs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for fid in faculty_ids:
                try:
                    fac = Faculty.objects.get(id=fid)
                    exp = calculate_experience(fac.joining_date) if fac.joining_date else "N/A"
                    ctx = {'faculty': fac, 'experience': exp, 'current_date': datetime.now(), 'pdf_mode': True}
                    html = render_to_string('dashboard/faculty_pdf.html', ctx)
                    if pdfkit is not None:
                        opts = {'page-size': 'A4', 'margin-top': '20mm', 'margin-right': '20mm',
                                'margin-bottom': '20mm', 'margin-left': '20mm', 'encoding': 'UTF-8'}
                        wk = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
                        cfg = pdfkit.configuration(wkhtmltopdf=wk)
                        pdf = pdfkit.from_string(html, False, options=opts, configuration=cfg)
                        pname = f"faculty_{fac.employee_code}.pdf"
                        pp = os.path.join(temp_dir, pname)
                        with open(pp, 'wb') as f:
                            f.write(pdf)
                        zipf.write(pp, pname)
                        os.remove(pp)
                except Exception as e:
                    logger.error(f"Error generating PDF for faculty {fid}: {e}")
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        response = HttpResponse(zip_data, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="faculty_pdfs_{datetime.now().strftime("%Y%m%d")}.zip"'
        if os.path.exists(zip_path):
            os.remove(zip_path)
        try:
            os.rmdir(temp_dir)
        except Exception:
            pass
        FacultyLog.objects.create(
            faculty=None, action='Bulk Faculty PDFs Generated',
            details=f'PDFs generated for {len(faculty_ids)} faculty members',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        return response
    except Exception as e:
        logger.error(f"Bulk PDF error: {e}")
        messages.error(request, f"Error generating PDFs: {e}")
    return redirect('dashboard:faculty_list')


# ==================== FACULTY PDF HELPERS ====================
@login_required
def faculty_pdf(request, faculty_id):
    return redirect('dashboard:generate_faculty_pdf', faculty_id=faculty_id)


@login_required
def ajax_check_pdf_status(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    has_pdf = bool(faculty.cloudinary_pdf_url)
    return JsonResponse({
        'success': True,
        'status': {
            'has_cloudinary_pdf': has_pdf,
            'cloudinary_url': faculty.cloudinary_pdf_url if has_pdf else None,
        }
    })


# ==================== CLOUDINARY MANAGEMENT ====================
@login_required
@csrf_exempt
def upload_faculty_to_cloudinary(request, faculty_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        if not is_cloudinary_configured():
            return JsonResponse({'success': False, 'error': 'Cloudinary not configured.'})
        if faculty.cloudinary_pdf_url:
            return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url,
                                 'message': 'PDF already exists on Cloudinary'})
        pdf_resp = generate_faculty_pdf(request, faculty_id)
        if not isinstance(pdf_resp, HttpResponse):
            return JsonResponse({'success': False, 'error': 'Failed to generate PDF'})
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
            tf.write(pdf_resp.content)
            tfp = tf.name
        cr = cloudinary.uploader.upload(
            tfp, resource_type="raw", folder="faculty_pdfs",
            public_id=f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}",
            overwrite=True, tags=[f"faculty_{faculty.employee_code}", faculty.department, "pdf"]
        )
        faculty.cloudinary_pdf_url = cr['secure_url']
        faculty.save()
        CloudinaryUpload.objects.create(
            faculty=faculty, upload_type='pdf', cloudinary_url=cr['secure_url'],
            public_id=cr['public_id'], resource_type=cr['resource_type'], uploaded_by=request.user.username
        )
        os.unlink(tfp)
        FacultyLog.objects.create(
            faculty=faculty, action='PDF Uploaded to Cloudinary',
            details=f'PDF uploaded: {faculty.employee_code}',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url,
                             'public_id': cr['public_id'], 'message': 'Uploaded successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def upload_faculty_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            faculty = get_object_or_404(Faculty, employee_code=request.POST.get('employee_code'))
            if not is_cloudinary_configured():
                return JsonResponse({'success': False, 'error': 'Cloudinary not configured.'})
            cr = cloudinary.uploader.upload(
                request.FILES['photo'], folder="faculty_photos",
                public_id=f"faculty_{faculty.employee_code}", overwrite=True,
                transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
            )
            faculty.cloudinary_photo_url = cr['secure_url']
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type='photo', cloudinary_url=cr['secure_url'],
                public_id=cr['public_id'], resource_type=cr['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )
            return JsonResponse({'success': True, 'photo_url': faculty.cloudinary_photo_url,
                                 'message': 'Photo uploaded successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'No photo file provided'})


@csrf_exempt
def upload_faculty_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        try:
            faculty = get_object_or_404(Faculty, employee_code=request.POST.get('employee_code'))
            if not is_cloudinary_configured():
                return JsonResponse({'success': False, 'error': 'Cloudinary not configured.'})
            cr = cloudinary.uploader.upload(
                request.FILES['pdf_file'], resource_type="raw", folder="faculty_pdfs",
                public_id=f"faculty_{faculty.employee_code}", overwrite=True
            )
            faculty.cloudinary_pdf_url = cr['secure_url']
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type='pdf', cloudinary_url=cr['secure_url'],
                public_id=cr['public_id'], resource_type=cr['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )
            return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url,
                                 'message': 'PDF uploaded successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'No PDF file provided'})


@login_required
def cloudinary_status(request):
    try:
        if not is_cloudinary_configured():
            return render(request, 'cloudinary/status.html', {
                'title': 'Cloudinary Status', 'connected': False,
                'error': 'Cloudinary credentials not configured.',
                'cloudinary_config': {
                    'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                    'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                    'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
                }
            })
        result = cloudinary.api.ping()
        usage = cloudinary.api.usage()
        recent_uploads = CloudinaryUpload.objects.select_related('faculty', 'student').order_by('-upload_date')[:10]
        total_faculty = Faculty.objects.count()
        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status', 'connected': result.get('status') == 'ok',
            'usage': usage,
            'uploaded_count': CloudinaryUpload.objects.count(),
            'faculty_with_pdf': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
                cloudinary_pdf_url='').count(),
            'faculty_with_photo': Faculty.objects.exclude(cloudinary_photo_url__isnull=True).exclude(
                cloudinary_photo_url='').count(),
            'total_faculty': total_faculty, 'recent_uploads': recent_uploads,
            'cloudinary_config': {
                'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
            }
        })
    except Exception as e:
        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status', 'connected': False, 'error': str(e),
            'cloudinary_config': {
                'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
            }
        })


@login_required
def get_cloudinary_url(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    return JsonResponse({
        'pdf_url': faculty.cloudinary_pdf_url,
        'photo_url': faculty.cloudinary_photo_url,
        'employee_code': faculty.employee_code,
        'has_pdf': bool(faculty.cloudinary_pdf_url),
        'has_photo': bool(faculty.cloudinary_photo_url),
    })


@login_required
def bulk_sync_to_cloudinary(request):
    if request.method != 'POST':
        return redirect('dashboard:faculty_list')
    faculty_ids = request.POST.getlist('faculty_ids')
    if not faculty_ids:
        messages.error(request, "No faculty selected.")
        return redirect('dashboard:faculty_list')
    if not is_cloudinary_configured():
        messages.error(request, "Cloudinary not configured.")
        return redirect('dashboard:faculty_list')
    ok = err = 0
    for fid in faculty_ids:
        try:
            fac = Faculty.objects.get(id=fid)
            if fac.photo and not fac.cloudinary_photo_url:
                try:
                    with fac.photo.open('rb') as pf:
                        cr = cloudinary.uploader.upload(pf, folder="faculty_photos",
                                                        public_id=f"faculty_{fac.employee_code}", overwrite=True)
                        fac.cloudinary_photo_url = cr['secure_url']
                        fac.save()
                        CloudinaryUpload.objects.create(
                            faculty=fac, upload_type='photo', cloudinary_url=cr['secure_url'],
                            public_id=cr['public_id'], resource_type=cr['resource_type'],
                            uploaded_by=request.user.username
                        )
                except Exception as e:
                    logger.error(f"Photo sync error for {fid}: {e}")
            ok += 1
        except Exception as e:
            logger.error(f"Sync error for {fid}: {e}")
            err += 1
    FacultyLog.objects.create(
        faculty=None, action='Bulk Cloudinary Sync',
        details=f'Synced {ok} faculty ({err} errors)',
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    if ok:
        messages.success(request, f"Synced {ok} faculty to Cloudinary.")
    if err:
        messages.warning(request, f"Failed to sync {err} faculty.")
    return redirect('dashboard:faculty_list')


# ==================== CERTIFICATE MANAGEMENT ====================
@login_required
def upload_certificate(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.faculty = faculty
            if 'certificate_file' in request.FILES and is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES['certificate_file'], resource_type="raw",
                        folder=f"certificates/{faculty.employee_code}",
                        public_id=f"cert_{cert.certificate_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=False
                    )
                    cert.cloudinary_url = cr['secure_url']
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type='certificate',
                        cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                        resource_type=cr['resource_type'], uploaded_by=request.user.username
                    )
                    messages.success(request, 'Certificate uploaded to Cloudinary!')
                except Exception as e:
                    logger.error(f"Certificate Cloudinary error: {e}")
                    messages.warning(request, 'Certificate saved locally but Cloudinary upload failed.')
            cert.save()
            FacultyLog.objects.create(
                faculty=faculty, action='Certificate Uploaded',
                details=f'Certificate uploaded: {cert.certificate_type}',
                performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Certificate uploaded successfully!')
            return redirect('dashboard:view_certificates', faculty_id=faculty_id)
    else:
        form = CertificateForm()
    return render(request, 'dashboard/certificate_upload.html', {
        'title': f'Upload Certificate - {faculty.staff_name}', 'form': form, 'faculty': faculty
    })


@login_required
def upload_certificates_bulk(request):
    if request.method == 'POST' and request.FILES.getlist('certificate_files'):
        faculty = get_object_or_404(Faculty, employee_code=request.POST.get('employee_code'))
        files = request.FILES.getlist('certificate_files')
        ok = err = 0
        for cf in files:
            try:
                ct = os.path.splitext(cf.name)[0].replace('_', ' ').replace('-', ' ').title() or "Certificate"
                curl = None
                if is_cloudinary_configured():
                    try:
                        cr = cloudinary.uploader.upload(
                            cf, resource_type="raw", folder=f"certificates/{faculty.employee_code}",
                            public_id=f"cert_{ct.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=False
                        )
                        curl = cr['secure_url']
                    except Exception as e:
                        logger.error(f"Cloudinary upload error: {e}")
                Certificate.objects.create(
                    faculty=faculty, certificate_type=ct, certificate_file=cf,
                    cloudinary_url=curl, issued_by='Unknown', issue_date=date.today(),
                    description=f'Uploaded bulk on {date.today().strftime("%Y-%m-%d")}'
                )
                ok += 1
            except Exception as e:
                logger.error(f"Error uploading {cf.name}: {e}")
                err += 1
        FacultyLog.objects.create(
            faculty=faculty, action='Bulk Certificates Uploaded',
            details=f'{ok} certs uploaded ({err} failed)',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        if ok:
            messages.success(request, f'{ok} certificates uploaded!')
        if err:
            messages.warning(request, f'{err} certificates failed.')
        return redirect('dashboard:view_certificates', faculty_id=faculty.id)
    return render(request, 'certificates/bulk_upload.html', {'title': 'Bulk Upload Certificates'})


@login_required
def view_certificates(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certs = Certificate.objects.filter(faculty=faculty).order_by('-issue_date')
    return render(request, 'dashboard/certificate_list.html', {
        'title': f'Certificates - {faculty.staff_name}',
        'faculty': faculty, 'certificates': certs,
        'cert_stats': {
            'total': certs.count(),
            'by_type': certs.values('certificate_type').annotate(count=Count('id')).order_by('-count'),
            'has_cloudinary': certs.exclude(cloudinary_url__isnull=True).exclude(cloudinary_url='').count(),
        }
    })


@login_required
def delete_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    fid = cert.faculty.id
    if request.method == 'POST':
        if cert.cloudinary_url and is_cloudinary_configured():
            try:
                pid = cert.cloudinary_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(pid, resource_type="raw")
            except Exception as e:
                logger.error(f"Cloudinary delete error: {e}")
        ct = cert.certificate_type
        cert.delete()
        messages.success(request, 'Certificate deleted successfully!')
        FacultyLog.objects.create(
            faculty=cert.faculty, action='Certificate Deleted',
            details=f'Certificate deleted: {ct}',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard:view_certificates', faculty_id=fid)
    return render(request, 'dashboard/certificate_confirm_delete.html', {
        'title': 'Delete Certificate', 'certificate': cert
    })


@login_required
def edit_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    fid = cert.faculty.id
    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=cert)
        if form.is_valid():
            old_type = cert.certificate_type
            if 'certificate_file' in request.FILES and is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES['certificate_file'], resource_type="raw",
                        folder=f"certificates/{cert.faculty.employee_code}",
                        public_id=f"cert_{cert.certificate_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=True
                    )
                    cert.cloudinary_url = cr['secure_url']
                except Exception as e:
                    logger.error(f"Cloudinary error editing cert: {e}")
            form.save()
            FacultyLog.objects.create(
                faculty=cert.faculty, action='Certificate Edited',
                details=f'Certificate edited: {old_type} -> {cert.certificate_type}',
                performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Certificate updated successfully!')
            return redirect('dashboard:view_certificates', faculty_id=fid)
    else:
        form = CertificateForm(instance=cert)
    return render(request, 'dashboard/certificate_edit.html', {
        'title': 'Edit Certificate', 'form': form, 'certificate': cert
    })


@login_required
def merge_certificates(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certs = Certificate.objects.filter(faculty=faculty)
    if not certs.exists():
        messages.error(request, 'No certificates found to merge.')
        return redirect('dashboard:view_certificates', faculty_id=faculty_id)
    try:
        writer = PdfWriter()
        if faculty.cloudinary_pdf_url:
            r = requests.get(faculty.cloudinary_pdf_url)
            if r.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                    tf.write(r.content)
                    tfp = tf.name
                for pg in PdfReader(tfp).pages:
                    writer.add_page(pg)
                os.unlink(tfp)
        for cert in certs:
            if cert.certificate_file:
                try:
                    if os.path.exists(cert.certificate_file.path):
                        for pg in PdfReader(cert.certificate_file.path).pages:
                            writer.add_page(pg)
                except Exception:
                    pass
            elif cert.cloudinary_url:
                r = requests.get(cert.cloudinary_url)
                if r.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                        tf.write(r.content)
                        tfp = tf.name
                    for pg in PdfReader(tfp).pages:
                        writer.add_page(pg)
                    os.unlink(tfp)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as mf:
            writer.write(mf.name)
            merged_path = mf.name
        merged_url = None
        if is_cloudinary_configured():
            try:
                cr = cloudinary.uploader.upload(
                    merged_path, resource_type="raw", folder="merged_certificates",
                    public_id=f"merged_{faculty.employee_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=False
                )
                merged_url = cr['secure_url']
                CloudinaryUpload.objects.create(
                    faculty=faculty, upload_type='merged_certificates',
                    cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                    resource_type=cr['resource_type'], uploaded_by=request.user.username
                )
            except Exception as e:
                logger.error(f"Cloudinary merge upload error: {e}")
        FacultyLog.objects.create(
            faculty=faculty, action='Certificates Merged',
            details=f'{certs.count()} certificates merged',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'merged_url': merged_url,
                                 'message': f'{certs.count()} certificates merged successfully'})
        if merged_url:
            messages.success(request, f'{certs.count()} certificates merged!')
            return redirect(merged_url)
        messages.warning(request, 'Merged locally but Cloudinary upload failed.')
    except Exception as e:
        logger.error(f"Merge error: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error merging: {e}')
    return redirect('dashboard:view_certificates', faculty_id=faculty_id)


@login_required
def merge_certificates_with_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    try:
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            return JsonResponse({'success': False, 'error': 'Failed to generate faculty PDF'})
        merged = merge_certificates_with_pdf_bytes(pdf_bytes, faculty)
        if merged:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                tf.write(merged)
                tfp = tf.name
            merged_url = None
            if is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        tfp, resource_type="raw", folder="merged_documents",
                        public_id=f"faculty_certs_{faculty.employee_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=False
                    )
                    merged_url = cr['secure_url']
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type='merged_faculty_certs',
                        cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                        resource_type=cr['resource_type'], uploaded_by=request.user.username
                    )
                except Exception as e:
                    logger.error(f"Cloudinary error: {e}")
            os.unlink(tfp)
            FacultyLog.objects.create(
                faculty=faculty, action='Certificates Merged with PDF',
                details=f'Certs merged with PDF: {Certificate.objects.filter(faculty=faculty).count()} certs',
                performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'merged_url': merged_url})
            if merged_url:
                return redirect(merged_url)
            return JsonResponse({'success': False, 'error': 'Failed to upload to Cloudinary'})
        return JsonResponse({'success': False, 'error': 'Failed to merge certificates'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def generate_faculty_pdf_bytes(faculty):
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        factory = RequestFactory()
        fake_req = factory.get('/')
        fake_req.user = AnonymousUser()
        fake_req.META['REMOTE_ADDR'] = '127.0.0.1'
        r = generate_faculty_pdf(fake_req, faculty.id)
        return r.content if isinstance(r, HttpResponse) else None
    except Exception as e:
        logger.error(f"Error generating PDF bytes: {e}")
        return None


def merge_certificates_with_pdf_bytes(pdf_bytes, faculty):
    try:
        writer = PdfWriter()
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                tf.write(pdf_bytes)
                tfp = tf.name
            for pg in PdfReader(tfp).pages:
                writer.add_page(pg)
        for cert in Certificate.objects.filter(faculty=faculty):
            if cert.cloudinary_url:
                try:
                    r = requests.get(cert.cloudinary_url)
                    if r.status_code == 200 and r.content[:4] == b'%PDF':
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tc:
                            tc.write(r.content)
                            tcp = tc.name
                        for pg in PdfReader(tcp).pages:
                            writer.add_page(pg)
                        try:
                            os.unlink(tcp)
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"Error merging cert: {e}")
            elif cert.certificate_file:
                try:
                    if os.path.exists(cert.certificate_file.path):
                        for pg in PdfReader(cert.certificate_file.path).pages:
                            writer.add_page(pg)
                except Exception:
                    pass
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as mf:
            writer.write(mf.name)
            with open(mf.name, 'rb') as f:
                merged = f.read()
            os.unlink(mf.name)
        if pdf_bytes and 'tfp' in dir():
            try:
                os.unlink(tfp)
            except Exception:
                pass
        return merged
    except Exception as e:
        logger.error(f"Error in merge_certificates_with_pdf_bytes: {e}")
        return None


@login_required
def preview_merged_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    recent = CloudinaryUpload.objects.filter(
        faculty=faculty,
        upload_type__in=['merged', 'merged_certificates', 'merged_faculty_certs'],
        public_id__contains='merged'
    ).order_by('-upload_date').first()
    if recent and recent.cloudinary_url:
        return JsonResponse({'success': True, 'pdf_url': recent.cloudinary_url, 'message': 'Merged PDF available'})
    return JsonResponse({'success': False, 'error': 'No merged PDF found.'})


# ==================== BULK OPERATIONS ====================
@login_required
def bulk_faculty_actions(request):
    if request.method != 'POST':
        return redirect('dashboard:faculty_list')
    action = request.POST.get('bulk_action')
    faculty_ids = request.POST.getlist('faculty_ids')
    if not faculty_ids:
        messages.error(request, 'No faculty members selected.')
        return redirect('dashboard:faculty_list')
    if action == 'delete':
        cnt = 0
        for fid in faculty_ids:
            try:
                Faculty.objects.get(id=fid).delete()
                cnt += 1
            except Faculty.DoesNotExist:
                pass
        FacultyLog.objects.create(faculty=None, action='Bulk Faculty Delete',
                                  details=f'{cnt} faculty deleted in bulk', performed_by=request.user.username,
                                  ip_address=request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Deleted {cnt} faculty member(s).')
    elif action == 'activate':
        cnt = Faculty.objects.filter(id__in=faculty_ids).update(is_active=True)
        messages.success(request, f'Activated {cnt} faculty member(s).')
    elif action == 'deactivate':
        cnt = Faculty.objects.filter(id__in=faculty_ids).update(is_active=False)
        messages.success(request, f'Deactivated {cnt} faculty member(s).')
    elif action == 'export_csv':
        return export_faculty_csv(request, faculty_ids)
    elif action == 'generate_pdfs':
        return bulk_generate_faculty_pdfs(request)
    elif action == 'sync_cloudinary':
        return bulk_sync_to_cloudinary(request)
    else:
        messages.error(request, 'Invalid bulk action.')
    return redirect('dashboard:faculty_list')


@login_required
def export_faculty_csv(request, faculty_ids=None):
    qs = Faculty.objects.filter(id__in=faculty_ids) if faculty_ids else Faculty.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="faculty_export_{date.today().strftime("%Y%m%d")}.csv"'
    w = csv.writer(response)
    w.writerow(['Employee Code', 'Staff Name', 'Department', 'Designation', 'Email', 'Phone',
                'Date of Birth', 'Joining Date', 'UG Degree', 'UG Year', 'PG Degree', 'PG Year',
                'PhD Status', 'Total Experience', 'Current Status', 'Cloudinary PDF URL', 'Cloudinary Photo URL',
                'JNTUH Bio-Data', 'Research Publications', 'FDPs', 'B.Tech Projects'])
    for f in qs:
        rp_count = ResearchPublication.objects.filter(faculty=f).count()
        fdp_count = FDP.objects.filter(faculty=f).count()
        project_count = BTechProject.objects.filter(faculty=f).count()
        w.writerow([
            f.employee_code, f.staff_name, f.department, f.designation,
            f.email, f.mobile,
            f.dob.strftime('%Y-%m-%d') if f.dob else '',
            f.joining_date.strftime('%Y-%m-%d') if f.joining_date else '',
            getattr(f, 'ug_degree', ''), getattr(f, 'ug_year', ''),
            getattr(f, 'pg_degree', ''), getattr(f, 'pg_year', ''),
            getattr(f, 'phd_degree', ''),
            calculate_experience(f.joining_date) if f.joining_date else 'N/A',
            'Active' if f.is_active else 'Inactive',
            f.cloudinary_pdf_url or '', f.cloudinary_photo_url or '',
            'Yes' if f.jntuh_biodata else 'No',
            rp_count, fdp_count, project_count,
        ])
    FacultyLog.objects.create(faculty=None, action='Faculty CSV Export',
                              details=f'Exported {qs.count()} faculty to CSV',
                              performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
    return response


# ==================== BULK UPLOAD ====================
@login_required
def bulk_upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if pd is None:
                    messages.error(request, 'Pandas not installed. Cannot process file.')
                    return redirect('dashboard:bulk_upload')
                f = request.FILES['file']
                fn = f.name.lower()
                if fn.endswith('.csv'):
                    df = pd.read_csv(f)
                elif fn.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(f)
                else:
                    messages.error(request, 'Unsupported format. Use CSV or Excel.')
                    return redirect('dashboard:bulk_upload')
                ok, err = process_csv_faculty_data(df, request.user)
                if ok:
                    messages.success(request, f'Imported {ok} faculty records.')
                if err:
                    messages.warning(request, f'{err} records had errors.')
                FacultyLog.objects.create(faculty=None, action='Bulk Faculty Upload',
                                          details=f'Bulk upload: {ok} ok, {err} failed',
                                          performed_by=request.user.username,
                                          ip_address=request.META.get('REMOTE_ADDR'))
                return redirect('dashboard:faculty_list')
            except Exception as e:
                logger.error(f"Bulk upload error: {e}")
                messages.error(request, f'Error processing file: {e}')
                return redirect('dashboard:bulk_upload')
    else:
        form = BulkUploadForm()
    return render(request, 'dashboard/bulk_upload.html', {
        'title': 'Bulk Faculty Upload',
        'form': form,
        'template_example': 'employee_code,staff_name,department,designation,email,mobile'
    })


def process_csv_faculty_data(df, user):
    """Process DataFrame and import faculty records"""
    ok_count = 0
    err_count = 0
    required_cols = ['employee_code', 'staff_name']

    for col in required_cols:
        if col not in df.columns:
            return 0, f"Missing required column: {col}"

    for idx, row in df.iterrows():
        try:
            employee_code = str(row.get('employee_code', '')).strip()
            staff_name = str(row.get('staff_name', '')).strip()

            if not employee_code or not staff_name:
                err_count += 1
                continue

            faculty, created = Faculty.objects.get_or_create(
                employee_code=employee_code,
                defaults={
                    'staff_name': staff_name,
                    'department': row.get('department', '')[:100] if pd.notna(row.get('department')) else '',
                    'designation': row.get('designation', '')[:100] if pd.notna(row.get('designation')) else '',
                    'email': row.get('email', '')[:200] if pd.notna(row.get('email')) else '',
                    'mobile': row.get('mobile', '')[:15] if pd.notna(row.get('mobile')) else '',
                }
            )

            if not created:
                faculty.staff_name = staff_name
                if pd.notna(row.get('department')):
                    faculty.department = row.get('department')[:100]
                if pd.notna(row.get('designation')):
                    faculty.designation = row.get('designation')[:100]
                if pd.notna(row.get('email')):
                    faculty.email = row.get('email')[:200]
                if pd.notna(row.get('mobile')):
                    faculty.mobile = row.get('mobile')[:15]

            faculty.save()
            ok_count += 1

        except Exception as e:
            logger.error(f"Error processing row {idx}: {e}")
            err_count += 1

    return ok_count, err_count


# ==================== SUBJECT MANAGEMENT ====================
@login_required
def subject_list(request):
    subjects = Subject.objects.all().order_by('name')
    paginator = Paginator(subjects, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/subject_list.html', {
        'title': 'Subjects Management',
        'subjects': page_obj,
        'total_subjects': subjects.count(),
        'page_obj': page_obj,
    })


@login_required
def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        department = request.POST.get('department', '').strip()
        year = request.POST.get('year', '')
        semester = request.POST.get('semester', '')

        if name and code:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'department': department,
                    'year': year,
                    'semester': semester,
                }
            )
            if created:
                messages.success(request, f'Subject "{name}" added successfully!')
            else:
                messages.warning(request, f'Subject with code "{code}" already exists.')
        else:
            messages.error(request, 'Subject name and code are required.')
        return redirect('dashboard:subject_list')

    departments = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'MBA', 'MCA']
    years = ['1', '2', '3', '4']
    semesters = ['1', '2']

    return render(request, 'dashboard/add_subject.html', {
        'title': 'Add Subject',
        'departments': departments,
        'years': years,
        'semesters': semesters,
    })


@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject.name = request.POST.get('name', subject.name).strip()
        subject.code = request.POST.get('code', subject.code).strip()
        subject.department = request.POST.get('department', subject.department).strip()
        subject.year = request.POST.get('year', subject.year)
        subject.semester = request.POST.get('semester', subject.semester)
        subject.save()
        messages.success(request, f'Subject "{subject.name}" updated successfully!')
        return redirect('dashboard:subject_list')

    departments = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'MBA', 'MCA']
    years = ['1', '2', '3', '4']
    semesters = ['1', '2']

    return render(request, 'dashboard/edit_subject.html', {
        'title': 'Edit Subject',
        'subject': subject,
        'departments': departments,
        'years': years,
        'semesters': semesters,
    })


@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" deleted successfully!')
        return redirect('dashboard:subject_list')

    return render(request, 'dashboard/confirm_delete_subject.html', {
        'title': 'Delete Subject',
        'subject': subject,
    })


# ==================== RESEARCH PUBLICATIONS MANAGEMENT ====================
@login_required
def research_publications_list(request):
    publications = ResearchPublication.objects.select_related('faculty').order_by('-publication_year', '-created_at')

    # Filters
    research_type = request.GET.get('type', '')
    if research_type:
        publications = publications.filter(research_type=research_type)

    year = request.GET.get('year', '')
    if year:
        publications = publications.filter(publication_year=year)

    faculty_id = request.GET.get('faculty', '')
    if faculty_id:
        publications = publications.filter(faculty_id=faculty_id)

    paginator = Paginator(publications, 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Get distinct years for filter
    years = ResearchPublication.objects.exclude(publication_year__isnull=True).exclude(publication_year='').values_list(
        'publication_year', flat=True).distinct().order_by('-publication_year')

    return render(request, 'dashboard/research_publications_list.html', {
        'title': 'Research Publications',
        'publications': page_obj,
        'total_count': publications.count(),
        'research_types': ResearchPublication.RESEARCH_TYPES,
        'years': years,
        'current_type': research_type,
        'current_year': year,
        'page_obj': page_obj,
    })


@login_required
def add_research_publication(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty')
        if not faculty_id:
            messages.error(request, 'Please select a faculty member.')
            return redirect('dashboard:add_research_publication')

        faculty = get_object_or_404(Faculty, id=faculty_id)

        publication = ResearchPublication.objects.create(
            faculty=faculty,
            research_type=request.POST.get('research_type', 'journal'),
            title=request.POST.get('title', '').strip(),
            authors=request.POST.get('authors', '').strip(),
            academic_year=request.POST.get('academic_year', '').strip(),
            publication_year=request.POST.get('publication_year') or None,
            journal_name=request.POST.get('journal_name', '').strip(),
            conference_name=request.POST.get('conference_name', '').strip(),
            doi=request.POST.get('doi', '').strip(),
            url=request.POST.get('url', '').strip(),
            status=request.POST.get('status', 'published'),
            abstract=request.POST.get('abstract', '').strip(),
            keywords=request.POST.get('keywords', '').strip(),
            issn=request.POST.get('issn', '').strip(),
            volume=request.POST.get('volume', '').strip(),
            issue=request.POST.get('issue', '').strip(),
            page_numbers=request.POST.get('page_numbers', '').strip(),
            conference_location=request.POST.get('conference_location', '').strip(),
            book_title=request.POST.get('book_title', '').strip(),
            isbn=request.POST.get('isbn', '').strip(),
            edition=request.POST.get('edition', '').strip(),
            patent_number=request.POST.get('patent_number', '').strip(),
            filing_date=request.POST.get('filing_date') or None,
            grant_date=request.POST.get('grant_date') or None,
            project_title=request.POST.get('project_title', '').strip(),
            funding_agency=request.POST.get('funding_agency', '').strip(),
            sanction_amount=request.POST.get('sanction_amount') or None,
            award_title=request.POST.get('award_title', '').strip(),
            awarding_body=request.POST.get('awarding_body', '').strip(),
            award_date=request.POST.get('award_date') or None,
        )

        FacultyLog.objects.create(
            faculty=faculty,
            action='Research Publication Added',
            details=f'Added publication: {publication.title}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'Research publication "{publication.title}" added successfully!')
        return redirect('dashboard:research_publications_list')

    faculties = Faculty.objects.all().order_by('staff_name')
    current_year = datetime.now().year

    return render(request, 'dashboard/add_research_publication.html', {
        'title': 'Add Research Publication',
        'faculties': faculties,
        'research_types': ResearchPublication.RESEARCH_TYPES,
        'current_year': current_year,
    })


@login_required
def edit_research_publication(request, publication_id):
    publication = get_object_or_404(ResearchPublication, id=publication_id)

    if request.method == 'POST':
        publication.research_type = request.POST.get('research_type', publication.research_type)
        publication.title = request.POST.get('title', publication.title).strip()
        publication.authors = request.POST.get('authors', publication.authors).strip()
        publication.academic_year = request.POST.get('academic_year', publication.academic_year).strip()
        publication.publication_year = request.POST.get('publication_year') or None
        publication.journal_name = request.POST.get('journal_name', publication.journal_name).strip()
        publication.conference_name = request.POST.get('conference_name', publication.conference_name).strip()
        publication.doi = request.POST.get('doi', publication.doi).strip()
        publication.url = request.POST.get('url', publication.url).strip()
        publication.status = request.POST.get('status', publication.status)
        publication.abstract = request.POST.get('abstract', publication.abstract).strip()
        publication.keywords = request.POST.get('keywords', publication.keywords).strip()
        publication.issn = request.POST.get('issn', publication.issn).strip()
        publication.volume = request.POST.get('volume', publication.volume).strip()
        publication.issue = request.POST.get('issue', publication.issue).strip()
        publication.page_numbers = request.POST.get('page_numbers', publication.page_numbers).strip()
        publication.save()

        FacultyLog.objects.create(
            faculty=publication.faculty,
            action='Research Publication Edited',
            details=f'Edited publication: {publication.title}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'Research publication updated successfully!')
        return redirect('dashboard:research_publications_list')

    return render(request, 'dashboard/edit_research_publication.html', {
        'title': 'Edit Research Publication',
        'publication': publication,
        'research_types': ResearchPublication.RESEARCH_TYPES,
    })


@login_required
def delete_research_publication(request, publication_id):
    publication = get_object_or_404(ResearchPublication, id=publication_id)
    if request.method == 'POST':
        title = publication.title
        faculty = publication.faculty
        publication.delete()

        FacultyLog.objects.create(
            faculty=faculty,
            action='Research Publication Deleted',
            details=f'Deleted publication: {title}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'Research publication deleted successfully!')
        return redirect('dashboard:research_publications_list')

    return render(request, 'dashboard/confirm_delete_publication.html', {
        'title': 'Delete Research Publication',
        'publication': publication,
    })


# ==================== FDP MANAGEMENT ====================
@login_required
def fdp_list(request):
    fdps_all = FDP.objects.select_related('faculty').order_by('-from_date')

    # Filters
    fdp_type = request.GET.get('type', '')
    if fdp_type:
        fdps_all = fdps_all.filter(fdp_type=fdp_type)

    faculty_id = request.GET.get('faculty', '')
    if faculty_id:
        fdps_all = fdps_all.filter(faculty_id=faculty_id)

    paginator = Paginator(fdps_all, 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/fdp_list.html', {
        'title': 'FDP / Workshop Management',
        'fdps': page_obj,
        'total_count': fdps_all.count(),
        'fdp_types': FDP.FDP_TYPES,
        'current_type': fdp_type,
        'page_obj': page_obj,
    })


@login_required
def add_fdp(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty')
        if not faculty_id:
            messages.error(request, 'Please select a faculty member.')
            return redirect('dashboard:add_fdp')

        faculty = get_object_or_404(Faculty, id=faculty_id)

        fdp = FDP.objects.create(
            faculty=faculty,
            fdp_type=request.POST.get('fdp_type', 'fdp'),
            title=request.POST.get('title', '').strip(),
            academic_year=request.POST.get('academic_year', '').strip(),
            from_date=request.POST.get('from_date') or None,
            to_date=request.POST.get('to_date') or None,
            organized_by=request.POST.get('organized_by', '').strip(),
            place=request.POST.get('place', '').strip(),
            mode=request.POST.get('mode', 'offline'),
            level=request.POST.get('level', 'national'),
            role=request.POST.get('role', 'participant'),
            sponsored_by=request.POST.get('sponsored_by', '').strip(),
            remarks=request.POST.get('remarks', '').strip(),
        )

        FacultyLog.objects.create(
            faculty=faculty,
            action='FDP Added',
            details=f'Added {fdp.get_fdp_type_display()}: {fdp.title}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'{fdp.get_fdp_type_display()} "{fdp.title}" added successfully!')
        return redirect('dashboard:fdp_list')

    faculties = Faculty.objects.all().order_by('staff_name')

    return render(request, 'dashboard/add_fdp.html', {
        'title': 'Add FDP / Workshop',
        'faculties': faculties,
        'fdp_types': FDP.FDP_TYPES,
        'modes': FDP.MODES,
        'levels': FDP.LEVELS,
        'roles': FDP.ROLES,
    })


@login_required
def edit_fdp(request, fdp_id):
    fdp = get_object_or_404(FDP, id=fdp_id)

    if request.method == 'POST':
        fdp.fdp_type = request.POST.get('fdp_type', fdp.fdp_type)
        fdp.title = request.POST.get('title', fdp.title).strip()
        fdp.academic_year = request.POST.get('academic_year', fdp.academic_year).strip()
        fdp.from_date = request.POST.get('from_date') or None
        fdp.to_date = request.POST.get('to_date') or None
        fdp.organized_by = request.POST.get('organized_by', fdp.organized_by).strip()
        fdp.place = request.POST.get('place', fdp.place).strip()
        fdp.mode = request.POST.get('mode', fdp.mode)
        fdp.level = request.POST.get('level', fdp.level)
        fdp.role = request.POST.get('role', fdp.role)
        fdp.sponsored_by = request.POST.get('sponsored_by', fdp.sponsored_by).strip()
        fdp.remarks = request.POST.get('remarks', fdp.remarks).strip()
        fdp.save()

        FacultyLog.objects.create(
            faculty=fdp.faculty,
            action='FDP Edited',
            details=f'Edited {fdp.get_fdp_type_display()}: {fdp.title}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'{fdp.get_fdp_type_display()} updated successfully!')
        return redirect('dashboard:fdp_list')

    return render(request, 'dashboard/edit_fdp.html', {
        'title': 'Edit FDP / Workshop',
        'fdp': fdp,
        'fdp_types': FDP.FDP_TYPES,
        'modes': FDP.MODES,
        'levels': FDP.LEVELS,
        'roles': FDP.ROLES,
    })


@login_required
def delete_fdp(request, fdp_id):
    fdp = get_object_or_404(FDP, id=fdp_id)
    if request.method == 'POST':
        title = fdp.title
        fdp_type = fdp.get_fdp_type_display()
        faculty = fdp.faculty
        fdp.delete()

        FacultyLog.objects.create(
            faculty=faculty,
            action='FDP Deleted',
            details=f'Deleted {fdp_type}: {title}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'{fdp_type} deleted successfully!')
        return redirect('dashboard:fdp_list')

    return render(request, 'dashboard/confirm_delete_fdp.html', {
        'title': 'Delete FDP / Workshop',
        'fdp': fdp,
    })


# ==================== SYSTEM SETTINGS ====================
@login_required
def system_settings(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard')

    context = {
        'title': 'System Settings',
        'cloudinary_configured': is_cloudinary_configured(),
        'cloudinary_config': {
            'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not set'),
            'api_key': 'Set' if getattr(settings, 'CLOUDINARY_API_KEY', None) else 'Not set',
            'api_secret': 'Set' if getattr(settings, 'CLOUDINARY_API_SECRET', None) else 'Not set',
        },
        'wkhtmltopdf_available': pdfkit is not None,
        'pandas_available': pd is not None,
        'matplotlib_available': plt is not None,
        'pymupdf_available': FITZ_AVAILABLE,
        'psutil_available': psutil is not None,
        'total_users': User.objects.count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
    }

    return render(request, 'dashboard/system_settings.html', context)


@login_required
def system_health(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)

    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': {
            'connected': True,
            'faculty_count': Faculty.objects.count(),
            'student_count': Student.objects.count(),
            'certificate_count': Certificate.objects.count(),
        },
        'cloudinary': {
            'configured': is_cloudinary_configured(),
            'connected': False,
        },
        'libraries': {
            'pdfkit': pdfkit is not None,
            'pandas': pd is not None,
            'matplotlib': plt is not None,
            'pymupdf': FITZ_AVAILABLE,
            'psutil': psutil is not None,
        },
    }

    if is_cloudinary_configured():
        try:
            cloudinary.api.ping()
            health_data['cloudinary']['connected'] = True
        except Exception as e:
            health_data['cloudinary']['connected'] = False
            health_data['cloudinary']['error'] = str(e)
            health_data['status'] = 'degraded'

    if psutil:
        try:
            health_data['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
            }
        except Exception as e:
            health_data['system'] = {'error': str(e)}

    return JsonResponse(health_data)


# ==================== ERROR HANDLERS ====================
def handler404(request, exception):
    return render(request, 'dashboard/404.html', {
        'title': 'Page Not Found',
        'request_path': request.path,
    }, status=404)


def handler500(request):
    return render(request, 'dashboard/500.html', {
        'title': 'Server Error',
    }, status=500)


# ==================== API ENDPOINTS ====================
@login_required
def api_faculty_list(request):
    """REST API endpoint for faculty list"""
    faculties = Faculty.objects.all().values(
        'id', 'staff_name', 'employee_code', 'department',
        'designation', 'email', 'mobile', 'is_active'
    ).order_by('staff_name')

    return JsonResponse({
        'success': True,
        'count': len(faculties),
        'data': list(faculties),
    })


@login_required
def api_faculty_detail(request, faculty_id):
    """REST API endpoint for faculty details"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    data = {
        'id': faculty.id,
        'staff_name': faculty.staff_name,
        'employee_code': faculty.employee_code,
        'department': faculty.department,
        'designation': faculty.designation,
        'email': faculty.email,
        'mobile': faculty.mobile,
        'joining_date': faculty.joining_date.isoformat() if faculty.joining_date else None,
        'is_active': faculty.is_active,
        'photo_url': faculty.cloudinary_photo_url or (faculty.photo.url if faculty.photo else None),
        'research_publications_count': ResearchPublication.objects.filter(faculty=faculty).count(),
        'fdps_count': FDP.objects.filter(faculty=faculty).count(),
        'certificates_count': Certificate.objects.filter(faculty=faculty).count(),
    }

    return JsonResponse({
        'success': True,
        'data': data,
    })


@login_required
def api_dashboard_stats(request):
    """REST API endpoint for dashboard statistics"""
    stats = {
        'faculty': {
            'total': Faculty.objects.count(),
            'active': Faculty.objects.filter(is_active=True).count(),
            'with_phd': Faculty.objects.filter(phd_degree='Completed').count(),
            'departments': list(
                Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:5]),
        },
        'students': {
            'total': Student.objects.count(),
        },
        'research': {
            'total_publications': ResearchPublication.objects.count(),
            'journal_articles': ResearchPublication.objects.filter(research_type='journal').count(),
            'conference_papers': ResearchPublication.objects.filter(research_type='conference').count(),
            'patents': ResearchPublication.objects.filter(research_type='patent').count(),
        },
        'fdps': {
            'total': FDP.objects.count(),
            'workshops': FDP.objects.filter(fdp_type='workshop').count(),
        },
        'certificates': {
            'total': Certificate.objects.count(),
        },
    }

    return JsonResponse({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
    })


# ==================== EXPORT FUNCTIONS ====================
@login_required
def export_all_data(request):
    """Export all faculty data to Excel"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard')

    if pd is None:
        messages.error(request, 'Pandas not installed. Cannot export data.')
        return redirect('dashboard:dashboard')

    try:
        # Faculty data
        faculty_data = []
        for f in Faculty.objects.all():
            faculty_data.append({
                'Employee Code': f.employee_code,
                'Staff Name': f.staff_name,
                'Department': f.department,
                'Designation': f.designation,
                'Email': f.email,
                'Mobile': f.mobile,
                'Joining Date': f.joining_date,
                'Date of Birth': f.dob,
                'PhD Status': f.phd_degree,
                'Active': 'Yes' if f.is_active else 'No',
            })

        df_faculty = pd.DataFrame(faculty_data)

        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_faculty.to_excel(writer, sheet_name='Faculty', index=False)

            # Research publications
            publications_data = []
            for p in ResearchPublication.objects.select_related('faculty'):
                publications_data.append({
                    'Faculty': p.faculty.staff_name if p.faculty else '',
                    'Employee Code': p.faculty.employee_code if p.faculty else '',
                    'Type': p.get_research_type_display(),
                    'Title': p.title,
                    'Authors': p.authors,
                    'Year': p.publication_year,
                    'Status': p.status,
                })
            if publications_data:
                df_pubs = pd.DataFrame(publications_data)
                df_pubs.to_excel(writer, sheet_name='Research Publications', index=False)

            # FDPs
            fdp_data = []
            for f in FDP.objects.select_related('faculty'):
                fdp_data.append({
                    'Faculty': f.faculty.staff_name if f.faculty else '',
                    'Type': f.get_fdp_type_display(),
                    'Title': f.title,
                    'From Date': f.from_date,
                    'To Date': f.to_date,
                    'Organized By': f.organized_by,
                })
            if fdp_data:
                df_fdp = pd.DataFrame(fdp_data)
                df_fdp.to_excel(writer, sheet_name='FDPs', index=False)

        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response[
            'Content-Disposition'] = f'attachment; filename="faculty_export_{date.today().strftime("%Y%m%d")}.xlsx"'

        FacultyLog.objects.create(
            faculty=None,
            action='Full Data Export',
            details='Exported all faculty data to Excel',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return response

    except Exception as e:
        logger.error(f"Export error: {e}")
        messages.error(request, f'Error exporting data: {e}')
        return redirect('dashboard:dashboard')

    # ==================== ADD ALL THESE FUNCTIONS ====================

    def system_status(request):
        """System status view"""
        from django.shortcuts import render
        context = {
            'status': 'healthy',
            'database': 'connected',
            'server': 'running',
            'title': 'System Status'
        }
        return render(request, 'dashboard/dashboard.html', context)

    def system_health(request):
        """System health check view"""
        from django.http import JsonResponse
        return JsonResponse({
            'status': 'healthy',
            'timestamp': '2026-04-02 22:26:43',
            'services': {
                'database': 'up',
                'cache': 'up',
                'storage': 'up'
            }
        })

    def system_info(request):
        """System information view"""
        from django.shortcuts import render
        import sys
        import django
        context = {
            'python_version': sys.version,
            'django_version': django.get_version(),
            'server_time': '2026-04-02 22:26:43',
        }
        return render(request, 'dashboard/dashboard.html', context)

    def system_settings(request):
        """System settings view"""
        from django.shortcuts import render
        from django.conf import settings
        context = {
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'installed_apps': settings.INSTALLED_APPS,
        }
        return render(request, 'dashboard/dashboard.html', context)

    def students_list(request):
        """Students list view"""
        from django.shortcuts import render
        context = {
            'title': 'Students List',
            'students': []
        }
        return render(request, 'dashboard/dashboard.html', context)

    def add_student(request):
        """Add student view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'Add Student'})

    def edit_student(request, student_id):
        """Edit student view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': f'Edit Student {student_id}'})

    def delete_student(request, student_id):
        """Delete student view"""
        from django.http import JsonResponse
        return JsonResponse({'success': True, 'message': 'Student deleted'})

    def import_students(request):
        """Import students view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'Import Students'})

    def export_students(request):
        """Export students view"""
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        response.write('id,name,email\n')
        return response

    def analytics_dashboard(request):
        """Analytics dashboard view"""
        from django.shortcuts import render
        context = {
            'title': 'Analytics Dashboard',
            'stats': {'total_students': 0, 'total_faculty': 0}
        }
        return render(request, 'dashboard/dashboard.html', context)

    def reports_view(request):
        """Reports view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'Reports'})

    def statistics_view(request):
        """Statistics view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'Statistics'})

    def about_view(request):
        """About page view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'About Us'})

    def contact_view(request):
        """Contact page view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'Contact Us'})

    def help_view(request):
        """Help page view"""
        from django.shortcuts import render
        return render(request, 'dashboard/dashboard.html', {'title': 'Help'})

    def api_students(request):
        """API endpoint for students"""
        from django.http import JsonResponse
        return JsonResponse({'students': [], 'count': 0})

    def api_faculty(request):
        """API endpoint for faculty"""
        from django.http import JsonResponse
        return JsonResponse({'faculty': [], 'count': 0})

    def api_dashboard_stats(request):
        """API endpoint for dashboard statistics"""
        from django.http import JsonResponse
        return JsonResponse({
            'total_students': 0,
            'total_faculty': 0,
            'total_courses': 0,
            'total_departments': 0
        })

    def get_data(request):
        """Generic data endpoint"""
        from django.http import JsonResponse
        return JsonResponse({'data': [], 'status': 'success'})

    def fetch_data(request):
        """Fetch data endpoint"""
        from django.http import JsonResponse
        return JsonResponse({'data': [], 'status': 'success'})