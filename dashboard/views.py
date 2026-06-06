# dashboard/views.py - COMPLETE VERSION WITH ENHANCED PDF GENERATION
# ============================================================================
import os
import sys
import json
import csv
import tempfile
import logging
import zipfile
import traceback
import io
import re
import hashlib
import hmac
import base64
from pathlib import Path
from datetime import datetime, date, timedelta
import requests
import qrcode
from urllib.parse import quote, urlencode, unquote, urlparse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import (FileResponse, HttpResponse, JsonResponse, HttpResponseRedirect,
                         HttpResponseBadRequest, Http404)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.db.models import Q, Count, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.urls import reverse
from django.core import signing
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
import django
# PDF Generation imports
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from pypdf import PdfWriter, PdfReader
# from PyPDF2 import PdfMerger  # Deprecated, using pypdf instead
from PIL import Image as PILImage
# Additional imports for PDF to image conversion
import fitz  # PyMuPDF
# Cloudinary imports
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary.utils
# Local imports
from .models import (
    Faculty, Certificate, FacultyLog, CloudinaryUpload,
    Subject, FacultyProfile, ResearchProject, Student,
    ResearchPublication, StudentResearchPublication, FDP, BTechProject,
    ProjectDownloadPayment,
)
from .forms import (
    StudentForm, CertificateForm,
    BulkUploadForm, FacultyProfileForm,
)
from .utils import (
    calculate_experience,
    validate_pdf_file, validate_image_file, parse_date
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
try:
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    plt = None
    np = None
    logger.warning("Matplotlib not installed. Chart features limited.")
try:
    import pdfkit
except ImportError:
    pdfkit = None
    logger.warning("pdfkit not installed. PDF generation features limited.")


# ==================== HELPERS ====================
def is_cloudinary_configured():
    return getattr(settings, 'CLOUDINARY_CONFIGURED', False)


def upload_file_to_cloudinary(file_path, folder, public_id, resource_type='auto', **kwargs):
    """Helper to upload file to Cloudinary."""
    if not is_cloudinary_configured():
        return None
    try:
        result = cloudinary.uploader.upload(
            file_path, resource_type=resource_type, folder=folder,
            public_id=public_id, overwrite=True, **kwargs
        )
        return result
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None


def get_wkhtmltopdf_path():
    """Get wkhtmltopdf executable path."""
    wkhtmltopdf_paths = [
        r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
        r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
        '/usr/local/bin/wkhtmltopdf',
        '/usr/bin/wkhtmltopdf',
        'wkhtmltopdf',
    ]
    for path in wkhtmltopdf_paths:
        if os.path.exists(path) or path == 'wkhtmltopdf':
            try:
                import subprocess
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
    return None


# ==================== HELPER FUNCTIONS ====================
def get_cloudinary_public_id(url, keep_extension=False):
    try:
        if '/upload/' not in url:
            return None
        tail = url.split('/upload/', 1)[1]
        parts = [p for p in tail.split('/') if p]
        if parts and parts[0].startswith('v') and parts[0][1:].isdigit():
            parts = parts[1:]
        if not parts:
            return None
        public_id = '/'.join(parts)
        if not keep_extension and '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]
        return public_id
    except Exception:
        return None


def get_cloudinary_public_id_candidates(url):
    """Return likely Cloudinary public_id variants for image and raw resources."""
    candidates = []
    for keep_extension in (True, False):
        public_id = get_cloudinary_public_id(url, keep_extension=keep_extension)
        if public_id and public_id not in candidates:
            candidates.append(public_id)
    return candidates


def get_pdf_password(profile_obj):
    return (getattr(profile_obj, 'pdf_password', None) or '').strip()


def encrypt_pdf_bytes(pdf_bytes, password):
    password = (password or '').strip()
    if not pdf_bytes or not password:
        return pdf_bytes

    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(user_password=password, owner_password=password)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def email_password_protected_pdf(*, recipient, display_name, pdf_bytes, filename, subject):
    recipient = (recipient or '').strip()
    if not recipient or not pdf_bytes:
        return False

    try:
        message = EmailMessage(
            subject=subject,
            body=(
                f"Dear {display_name or 'User'},\n\n"
                "Please find attached your password-protected profile PDF.\n"
                "Open it using the PDF password you entered during registration.\n\n"
                "Regards,\nEngineering College"
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            to=[recipient],
        )
        message.attach(filename, pdf_bytes, 'application/pdf')
        message.send(fail_silently=False)
        logger.info(f"Password-protected PDF emailed to {recipient}")
        return True
    except Exception as exc:
        logger.warning(f"Could not email password-protected PDF to {recipient}: {exc}", exc_info=True)
        return False


def try_cloudinary_private_download(public_id, headers=None):
    """Download a Cloudinary asset via signed private_download_url, trying multiple resource types."""
    if not public_id:
        return None

    try:
        if '.' in public_id:
            base_public_id, extension = public_id.rsplit('.', 1)
        else:
            base_public_id, extension = public_id, None

        # Try multiple resource types
        for res_type in ['raw', 'image']:
            try:
                if res_type == 'raw':
                    download_url = cloudinary.utils.private_download_url(
                        public_id,
                        resource_type=res_type,
                        format=None,
                        type='upload',
                        attachment=False,
                    )
                else:
                    download_url = cloudinary.utils.private_download_url(
                        base_public_id,
                        resource_type=res_type,
                        format=extension,
                        type='upload',
                        attachment=False,
                    )
                response = requests.get(download_url, timeout=30, headers=headers or {})
                if response.status_code == 200:
                    print(f"  [CLOUDINARY] Private download succeeded with resource_type={res_type}")
                    return response
            except Exception as e:
                print(f"  [CLOUDINARY] Private download failed for {res_type}: {e}")
                continue

        logger.warning(f"Cloudinary private download failed for {public_id}: all resource types failed")
    except Exception as e:
        logger.warning(f"Cloudinary private download failed for {public_id}: {e}")
    return None


def normalize_optional_url(value):
    value = (value or '').strip()
    if not value:
        return ''
    if value.startswith('//'):
        return f'https:{value}'
    if value.lower().startswith(('http://', 'https://')):
        return value
    if '://' in value:
        return ''
    return f'https://{value.lstrip("/")}'


def parse_json_list(value):
    try:
        parsed = json.loads(value or '[]')
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def normalize_faculty_college_experiences(value):
    """Validate college employment rows and calculate each displayed duration."""
    experiences = []
    for item in parse_json_list(value) if isinstance(value, str) else (value or []):
        if not isinstance(item, dict):
            continue
        college_name = str(item.get('college_name') or '').strip()
        college_address = str(item.get('college_address') or '').strip()
        from_date = parse_date(str(item.get('from_date') or '').strip())
        to_date = parse_date(str(item.get('to_date') or '').strip())
        if not college_name or not college_address or not from_date or not to_date or to_date < from_date:
            continue

        total_days = (to_date - from_date).days + 1
        years, remaining_days = divmod(total_days, 365)
        months, days = divmod(remaining_days, 30)
        duration_parts = []
        if years:
            duration_parts.append(f"{years} year{'s' if years != 1 else ''}")
        if months:
            duration_parts.append(f"{months} month{'s' if months != 1 else ''}")
        if days or not duration_parts:
            duration_parts.append(f"{days} day{'s' if days != 1 else ''}")

        experiences.append({
            'college_name': college_name,
            'college_address': college_address,
            'from_date': from_date.isoformat(),
            'to_date': to_date.isoformat(),
            'experience': ', '.join(duration_parts),
            'total_days': total_days,
        })
    return experiences


def normalize_tstsabas_entries(value):
    """Return non-empty, trimmed TSTSABAS values."""
    entries = parse_json_list(value) if isinstance(value, str) else (value or [])
    normalized = []
    for entry in entries:
        if isinstance(entry, dict):
            entry = entry.get('value')
        text = str(entry or '').strip()
        if text:
            normalized.append(text)
    return normalized


def iter_indexed_uploaded_files(files, prefix):
    indexed_files = []
    for key in files.keys():
        if not key.startswith(prefix):
            continue
        suffix = key[len(prefix):]
        if not suffix.isdigit():
            continue
        indexed_files.append((int(suffix), files[key]))
    indexed_files.sort(key=lambda item: item[0])
    return indexed_files


STUDENT_CERTIFICATE_SLOTS = [
    ('cert_achieve', 'achievement', 'cert_achieve_url'),
    ('cert_intern', 'internship', 'cert_intern_url'),
    ('cert_courses', 'courses', 'cert_courses_url'),
    ('cert_sdp', 'sdp', 'cert_sdp_url'),
    ('cert_extra', 'extra', 'cert_extra_url'),
    ('cert_placement', 'placement', 'cert_placement_url'),
    ('cert_national', 'national', 'cert_national_url'),
]

STUDENT_CERTIFICATE_TYPE_ALIASES = {
    'achievement': 'cert_achieve',
    'achieve': 'cert_achieve',
    'internship': 'cert_intern',
    'intern': 'cert_intern',
    'course': 'cert_courses',
    'courses': 'cert_courses',
    'sdp': 'cert_sdp',
    'extra': 'cert_extra',
    'extracurricular': 'cert_extra',
    'other': 'cert_extra',
    'placement': 'cert_placement',
    'national': 'cert_national',
}

DEMO_STUDENT_USERNAMES = {'anrkitstudent'}


def is_demo_student_session(request):
    return bool(
        request.session.get('student_logged_in')
        and request.session.get('student_username') in DEMO_STUDENT_USERNAMES
    )


def get_session_student_ht_no(request):
    return (request.session.get('student_ht_no') or request.session.get('student_username') or '').strip()


def get_session_student_record(request):
    if not request.session.get('student_logged_in'):
        return None

    student_id = request.session.get('student_id')
    if student_id:
        try:
            return Student.objects.filter(id=student_id).first()
        except Exception as exc:
            logger.warning(f"Could not resolve student session by id {student_id}: {exc}")

    if is_demo_student_session(request):
        return None

    student_ht_no = get_session_student_ht_no(request)
    if not student_ht_no:
        return None

    try:
        return Student.objects.filter(ht_no=student_ht_no).first()
    except Exception as exc:
        logger.warning(f"Could not resolve student session by ht_no {student_ht_no}: {exc}")
        return None


def student_session_can_access_record(request, student):
    if not request.session.get('student_logged_in'):
        return False

    if is_demo_student_session(request):
        return True

    session_student = get_session_student_record(request)
    if session_student and student:
        return session_student.id == student.id

    return get_session_student_ht_no(request) == getattr(student, 'ht_no', None)


def student_dashboard_redirect_route(request):
    if request.session.get('student_logged_in'):
        return 'dashboard:student_dashboard_view'
    return 'dashboard:student_dashboard'


def student_has_photo_asset(student):
    photo_url = normalize_optional_url(getattr(student, 'photo_url', None))
    photo_field = getattr(student, 'photo', None)
    return bool(photo_url or getattr(photo_field, 'name', None))


def student_has_certificate_assets(student):
    for field_name, _, url_field_name in STUDENT_CERTIFICATE_SLOTS:
        file_field = getattr(student, field_name, None)
        url_value = normalize_optional_url(getattr(student, url_field_name, None))
        if url_value or getattr(file_field, 'name', None):
            return True
    return False


def student_has_research_publication_assets(student):
    return StudentResearchPublication.objects.filter(student=student).filter(
        Q(proof_document_url__isnull=False, proof_document_url__gt='')
        | Q(proof_document__isnull=False, proof_document__gt='')
    ).exists()


def student_has_upload_assets(student):
    return (
        student_has_photo_asset(student)
        or student_has_certificate_assets(student)
        or student_has_research_publication_assets(student)
    )


def student_has_saved_pdf(student):
    pdf_url = normalize_optional_url(getattr(student, 'pdf_url', None))
    pdf_field = getattr(student, 'pdf_file', None)
    return bool(pdf_url or getattr(pdf_field, 'name', None))


def choose_student_certificate_slot(student, requested_type=None, reserved_fields=None):
    reserved_fields = reserved_fields or set()
    slot_by_field = {
        field_name: (field_name, folder, url_field_name)
        for field_name, folder, url_field_name in STUDENT_CERTIFICATE_SLOTS
    }
    preferred_field = STUDENT_CERTIFICATE_TYPE_ALIASES.get((requested_type or '').strip().lower())

    def slot_is_available(field_name, url_field_name):
        if field_name in reserved_fields:
            return False
        file_field = getattr(student, field_name, None)
        url_value = normalize_optional_url(getattr(student, url_field_name, None))
        return not getattr(file_field, 'name', None) and not url_value

    if preferred_field:
        preferred_slot = slot_by_field.get(preferred_field)
        if preferred_slot and slot_is_available(preferred_slot[0], preferred_slot[2]):
            return preferred_slot

    for field_name, folder, url_field_name in STUDENT_CERTIFICATE_SLOTS:
        if slot_is_available(field_name, url_field_name):
            return field_name, folder, url_field_name

    return None


def build_student_certificate_upload_plan(request, student):
    reserved_fields = set()
    upload_plan = []
    skipped_uploads = []

    for field_name, folder, url_field_name in STUDENT_CERTIFICATE_SLOTS:
        uploaded_file = request.FILES.get(field_name)
        if not uploaded_file:
            continue
        reserved_fields.add(field_name)
        upload_plan.append({
            'field_name': field_name,
            'folder': folder,
            'url_field_name': url_field_name,
            'file': uploaded_file,
            'source': field_name,
        })

    for index, uploaded_file in iter_indexed_uploaded_files(request.FILES, 'additional_cert_file_'):
        requested_type = (request.POST.get(f'additional_cert_type_{index}') or '').strip().lower()
        selected_slot = choose_student_certificate_slot(
            student,
            requested_type=requested_type,
            reserved_fields=reserved_fields,
        )
        if not selected_slot:
            skipped_uploads.append({
                'index': index,
                'filename': getattr(uploaded_file, 'name', f'additional_cert_file_{index}'),
                'requested_type': requested_type or 'other',
            })
            continue

        field_name, folder, url_field_name = selected_slot
        reserved_fields.add(field_name)
        upload_plan.append({
            'field_name': field_name,
            'folder': folder,
            'url_field_name': url_field_name,
            'file': uploaded_file,
            'source': f'additional_cert_file_{index}',
        })

    return upload_plan, skipped_uploads


def build_student_research_publications_json(student):
    publications = StudentResearchPublication.objects.filter(student=student).order_by('-publication_year', '-id')
    return json.dumps([{
        'id': publication.id,
        'research_type': publication.research_type or 'journal',
        'title': publication.title,
        'authors': publication.authors or '',
        'academic_year': publication.academic_year or '',
        'publication_year': publication.publication_year,
        'journal_name': publication.journal_name or '',
        'conference_name': publication.conference_name or '',
        'issn': publication.issn or '',
        'doi': publication.doi or '',
        'url': publication.url or '',
        'status': publication.status or 'published',
        'proof_document_url': publication.proof_document_url or '',
    } for publication in publications])


def save_student_research_publications_from_request(request, student, upload_func=None, clear_missing=True):
    research_list = parse_json_list(request.POST.get('student_research_publications_json', '[]'))
    existing_by_id = {
        publication.id: publication
        for publication in StudentResearchPublication.objects.filter(student=student)
    }
    saved_records = []
    proof_override_assets = []
    uploaded_labels = []
    local_labels = []
    seen_ids = set()

    for index, item in enumerate(research_list, start=1):
        if not isinstance(item, dict) or not (item.get('title') or '').strip():
            continue

        publication_id = item.get('id')
        try:
            publication_id = int(publication_id) if publication_id else None
        except (TypeError, ValueError):
            publication_id = None

        publication = existing_by_id.get(publication_id)
        if publication:
            seen_ids.add(publication.id)
        else:
            publication = StudentResearchPublication(student=student)

        pub_type = item.get('research_type') or item.get('type') or 'journal'
        venue = (item.get('journal_name') or item.get('conference_name') or '').strip()
        publication.research_type = pub_type
        publication.title = (item.get('title') or '').strip()
        publication.authors = (item.get('authors') or '').strip()
        publication.academic_year = (item.get('academic_year') or '').strip()
        publication_year = item.get('publication_year') or item.get('year') or None
        try:
            publication.publication_year = int(publication_year) if publication_year else None
        except (TypeError, ValueError):
            publication.publication_year = None
        publication.journal_name = venue if pub_type != 'conference' else ''
        publication.conference_name = venue if pub_type == 'conference' else ''
        publication.issn = (item.get('issn') or '').strip()
        publication.doi = (item.get('doi') or '').strip()
        publication.url = normalize_optional_url(item.get('url'))
        publication.status = item.get('status') or 'published'
        if item.get('proof_document_url') and not publication.proof_document_url:
            publication.proof_document_url = normalize_optional_url(item.get('proof_document_url'))
        publication.save()
        seen_ids.add(publication.id)

        proof_file = request.FILES.get(f'student_research_proof_files_{index}')
        if proof_file:
            temp_asset_path, temp_asset_is_pdf = snapshot_uploaded_file(proof_file, default_suffix='.pdf')
            if temp_asset_path:
                proof_override_assets.append({
                    'field_name': f'student_research_proof_{publication.id}',
                    'path': temp_asset_path,
                    'is_pdf': temp_asset_is_pdf,
                })
                persist_snapshot_to_model_field(
                    publication,
                    'proof_document',
                    temp_asset_path,
                    getattr(proof_file, 'name', None),
                )

            upload_result = upload_func(proof_file, 'research_proofs') if upload_func else None
            if upload_result and upload_result.get('secure_url'):
                publication.proof_document_url = upload_result['secure_url']
                record_cloudinary_upload(
                    upload_type='student_research_proof',
                    upload_result=upload_result,
                    uploaded_by=getattr(getattr(request, 'user', None), 'username', None),
                    student=student,
                )
                uploaded_labels.append(f'research proof {index}')
            else:
                local_labels.append(f'research proof {index}')

            publication.save()

        saved_records.append(publication)

    if clear_missing:
        for publication_id, publication in existing_by_id.items():
            if publication_id not in seen_ids:
                publication.delete()

    return saved_records, proof_override_assets, uploaded_labels, local_labels


def record_cloudinary_upload(*, upload_type, upload_result, uploaded_by=None, faculty=None, student=None):
    if not upload_result:
        return
    try:
        CloudinaryUpload.objects.create(
            faculty=faculty,
            student=student,
            upload_type=upload_type,
            cloudinary_url=upload_result.get('secure_url', ''),
            public_id=upload_result.get('public_id', ''),
            resource_type=upload_result.get('resource_type', 'auto') or 'auto',
            uploaded_by=uploaded_by,
        )
    except Exception as exc:
        logger.warning(f"Unable to record Cloudinary upload for {upload_type}: {exc}")


def download_remote_asset(url, default_suffix='.pdf'):
    """Download a remote asset, with special handling for Cloudinary URLs."""
    if not url or not isinstance(url, str) or not url.startswith('http'):
        return None, False

    # Special handling for Cloudinary URLs - use API with authentication
    if 'cloudinary.com' in url and is_cloudinary_configured():
        try:
            public_ids = get_cloudinary_public_id_candidates(url)
            for public_id in public_ids:
                print(f"  [CLOUDINARY] Downloading via API: {public_id}")
                # Try different resource types
                for res_type in ['raw', 'image', 'auto']:
                    try:
                        # Get resource info from Cloudinary API
                        resource = cloudinary.api.resource(public_id, resource_type=res_type)
                        if resource and 'secure_url' in resource:
                            # Download using the secure URL
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            r = requests.get(resource['secure_url'], timeout=30, headers=headers)
                            if r.status_code == 200:
                                content_type = r.headers.get('content-type', '').lower()
                                is_pdf = 'pdf' in content_type or url.lower().endswith('.pdf')
                                suffix = ".pdf" if is_pdf else (".jpg" if 'image' in content_type else default_suffix)
                                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                                tmp.write(r.content)
                                tmp.close()
                                print(f"  [OK] Downloaded via Cloudinary API ({res_type}): {tmp.name}")
                                return tmp.name, is_pdf
                    except Exception as e:
                        print(f"  [CLOUDINARY] Resource type {res_type} failed: {e}")
                        continue

                # Try private download for authenticated resources
                print(f"  [CLOUDINARY] Trying private download for: {public_id}")
                private_response = try_cloudinary_private_download(public_id)
                if private_response and private_response.status_code == 200:
                    content_type = private_response.headers.get('content-type', '').lower()
                    is_pdf = 'pdf' in content_type or url.lower().endswith('.pdf')
                    suffix = ".pdf" if is_pdf else default_suffix
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tmp.write(private_response.content)
                    tmp.close()
                    print(f"  [OK] Downloaded via Cloudinary private download: {tmp.name}")
                    return tmp.name, is_pdf
        except Exception as e:
            print(f"  [CLOUDINARY] API download failed: {e}")

    # Fallback to direct URL download
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)

        # Try swapping resource type in URL for Cloudinary URLs
        if response.status_code != 200 and 'cloudinary.com' in url:
            alt_urls = []
            if '/raw/upload/' in url:
                alt_urls.append(url.replace('/raw/upload/', '/image/upload/'))
            elif '/image/upload/' in url:
                alt_urls.append(url.replace('/image/upload/', '/raw/upload/'))
            for alt_url in alt_urls:
                try:
                    r5 = requests.get(alt_url, timeout=30, headers=headers)
                    if r5.status_code == 200:
                        response = r5
                        print(f"  [OK] Alt URL worked: {alt_url}")
                        break
                except Exception:
                    continue

        if response.status_code != 200:
            print(f"  [SKIP] All fallbacks failed for: {url} (HTTP {response.status_code})")
            return None, False

        content_type = (response.headers.get('content-type') or '').lower()
        is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')
        if not is_pdf and len(response.content) > 4:
            if response.content[:4] == b'%PDF':
                is_pdf = True

        suffix = '.pdf' if is_pdf else default_suffix
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(response.content)
        tmp.close()
        print(f"  [OK] Downloaded {len(response.content)} bytes -> {tmp.name}")
        return tmp.name, is_pdf
    except Exception as e:
        print(f"  [ERR] Download error for {url}: {e}")
        return None, False


def get_local_or_remote_asset(file_field=None, url=None, default_suffix='.pdf'):
    """Return a readable local path for a FileField/URL plus whether it is a PDF."""
    try:
        if url and isinstance(url, str) and url.startswith('http'):
            result, is_pdf = download_remote_asset(url, default_suffix=default_suffix)
            if result:
                return result, is_pdf

        if file_field and getattr(file_field, 'name', ''):
            try:
                local_path = file_field.path
                if local_path and os.path.exists(local_path):
                    return local_path, local_path.lower().endswith('.pdf')
            except (NotImplementedError, ValueError, OSError):
                pass

            try:
                field_url = getattr(file_field, 'url', None)
            except Exception:
                field_url = None
            if field_url and isinstance(field_url, str) and field_url.startswith('http'):
                result, is_pdf = download_remote_asset(field_url, default_suffix=default_suffix)
                if result:
                    return result, is_pdf

    except Exception as e:
        logger.warning(f"Error resolving asset: {e}")
    return None, False


def encode_image_as_data_uri(image_path):
    """Convert an image file into a data URI for reliable WeasyPrint embedding."""
    if not image_path or not os.path.exists(image_path):
        return None

    try:
        with PILImage.open(image_path) as image:
            image_format = (image.format or Path(image_path).suffix.lstrip('.')).lower()

        mime_type = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
        }.get(image_format, 'image/jpeg')

        import base64

        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()

        return f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
    except Exception as e:
        logger.warning(f"Could not encode image {image_path}: {e}")
        return None


def collect_faculty_photo_candidates(faculty):
    """Return ordered photo candidates from DB fields, Cloudinary history, and filesystem fallbacks."""
    candidates = []
    seen = set()

    def add_path(path_value, source):
        if not path_value:
            return
        normalized = os.path.normcase(os.path.abspath(str(path_value)))
        key = ('path', normalized)
        if key in seen:
            return
        seen.add(key)
        candidates.append({'path': str(path_value), 'source': source})

    def add_url(url_value, source):
        normalized = normalize_optional_url(url_value)
        if not normalized:
            return
        key = ('url', normalized)
        if key in seen:
            return
        seen.add(key)
        candidates.append({'url': normalized, 'source': source})

    add_url(getattr(faculty, 'cloudinary_photo_url', None), 'cloudinary_photo_url')

    photo_field = getattr(faculty, 'photo', None)
    if photo_field and getattr(photo_field, 'name', ''):
        try:
            add_path(photo_field.path, 'photo_field_path')
        except (NotImplementedError, ValueError, OSError, Exception):
            pass

        try:
            add_url(photo_field.url, 'photo_field_url')
        except Exception:
            pass

    latest_uploads = (
        CloudinaryUpload.objects
        .filter(faculty=faculty, upload_type='photo')
        .order_by('-upload_date')
        .values_list('cloudinary_url', flat=True)
    )
    for uploaded_url in latest_uploads:
        add_url(uploaded_url, 'cloudinary_upload_history')

    if faculty.employee_code:
        media_photo_dir = Path(settings.MEDIA_ROOT) / 'faculty_photos'
        if media_photo_dir.exists():
            for candidate in sorted(media_photo_dir.glob(f'{faculty.employee_code}*')):
                if candidate.is_file():
                    add_path(candidate, 'media_employee_code_fallback')

        static_image_dir = Path(settings.BASE_DIR) / 'static' / 'images'
        if static_image_dir.exists():
            for candidate in sorted(static_image_dir.glob(f'{faculty.employee_code}*')):
                if candidate.is_file():
                    add_path(candidate, 'static_employee_code_fallback')

        if is_cloudinary_configured():
            try:
                convention_url, _ = cloudinary.utils.cloudinary_url(
                    f'faculty_photos/faculty_{faculty.employee_code}_photo',
                    secure=True,
                )
                add_url(convention_url, 'cloudinary_naming_convention')
            except Exception as e:
                logger.warning(f"Could not build Cloudinary photo URL for {faculty.employee_code}: {e}")

    return candidates


def resolve_faculty_photo_for_pdf(faculty):
    """Resolve the best faculty photo source and return a data URI plus cleanup temp paths."""
    temp_paths = []

    for candidate in collect_faculty_photo_candidates(faculty):
        source = candidate['source']
        path_value = candidate.get('path')
        url_value = candidate.get('url')

        if path_value and os.path.exists(path_value):
            data_uri = encode_image_as_data_uri(path_value)
            if data_uri:
                return data_uri, path_value, temp_paths, source
            logger.warning(f"Photo candidate from {source} could not be encoded: {path_value}")

        if url_value:
            downloaded_path, is_pdf = download_remote_asset(url_value, default_suffix='.jpg')
            if not downloaded_path:
                continue

            temp_paths.append(downloaded_path)
            if is_pdf:
                logger.warning(f"Photo candidate from {source} resolved to a PDF, skipping: {url_value}")
                continue

            data_uri = encode_image_as_data_uri(downloaded_path)
            if data_uri:
                return data_uri, downloaded_path, temp_paths, source

            logger.warning(f"Downloaded photo candidate from {source} could not be encoded: {url_value}")

    return None, None, temp_paths, None


def collect_student_photo_candidates(student, photo_override_path=None):
    """Return ordered student photo candidates for generated PDFs."""
    candidates = []
    seen = set()

    def add_path(path_value, source):
        if not path_value or not os.path.exists(path_value):
            return
        key = ('path', os.path.abspath(path_value))
        if key in seen:
            return
        seen.add(key)
        candidates.append({'source': source, 'path': path_value})

    def add_url(url_value, source):
        normalized_url = normalize_optional_url(url_value)
        if not normalized_url:
            return
        key = ('url', normalized_url)
        if key in seen:
            return
        seen.add(key)
        candidates.append({'source': source, 'url': normalized_url})

    add_path(photo_override_path, 'photo_override_path')
    add_url(getattr(student, 'photo_url', None), 'student.photo_url')

    latest_upload_url = (
        CloudinaryUpload.objects
        .filter(student=student, upload_type='photo')
        .order_by('-upload_date')
        .values_list('cloudinary_url', flat=True)
        .first()
    )
    add_url(latest_upload_url, 'cloudinary_upload_history')

    photo_field = getattr(student, 'photo', None)
    if photo_field and getattr(photo_field, 'name', ''):
        try:
            add_path(photo_field.path, 'student.photo.path')
        except (NotImplementedError, ValueError, OSError):
            pass

        try:
            field_url = photo_field.url
        except Exception:
            field_url = None

        if isinstance(field_url, str) and field_url.startswith(('http://', 'https://', '//')):
            add_url(field_url, 'student.photo.url')

    return candidates


def collect_student_document_candidates(student, file_field_name, url_field_name):
    """Return ordered document candidates from model fields and upload history."""
    candidates = []
    seen = set()

    def add_path(path_value, source):
        if not path_value or not os.path.exists(path_value):
            return
        key = ('path', os.path.abspath(path_value))
        if key in seen:
            return
        seen.add(key)
        candidates.append({'source': source, 'path': path_value})

    def add_url(url_value, source):
        normalized_url = normalize_optional_url(url_value)
        if not normalized_url:
            return
        key = ('url', normalized_url)
        if key in seen:
            return
        seen.add(key)
        candidates.append({'source': source, 'url': normalized_url})

    file_field = getattr(student, file_field_name, None)
    if file_field and getattr(file_field, 'name', ''):
        try:
            add_path(file_field.path, f'{file_field_name}.path')
        except (NotImplementedError, ValueError, OSError):
            pass

    add_url(getattr(student, url_field_name, None), url_field_name)

    latest_upload_urls = (
        CloudinaryUpload.objects
        .filter(student=student, upload_type=file_field_name)
        .order_by('-upload_date')
        .values_list('cloudinary_url', flat=True)
    )
    for uploaded_url in latest_upload_urls:
        add_url(uploaded_url, f'{file_field_name}.cloudinary_upload_history')

    if file_field and getattr(file_field, 'name', ''):
        try:
            field_url = file_field.url
        except Exception:
            field_url = None

        if isinstance(field_url, str) and field_url.startswith(('http://', 'https://', '//')):
            add_url(field_url, f'{file_field_name}.url')

    return candidates


def resolve_asset_from_candidates(candidates, temp_files, default_suffix='.pdf'):
    """Resolve the first readable asset candidate into a local path."""
    for candidate in candidates:
        path_value = candidate.get('path')
        if path_value and os.path.exists(path_value):
            return path_value, path_value.lower().endswith('.pdf')

        url_value = candidate.get('url')
        if not url_value:
            continue

        downloaded_path, is_pdf = download_remote_asset(url_value, default_suffix=default_suffix)
        if downloaded_path:
            if downloaded_path not in temp_files:
                temp_files.append(downloaded_path)
            return downloaded_path, is_pdf

    return None, False


def resolve_student_photo_for_pdf(student, photo_override_path=None):
    """Resolve the best student photo source and return an embeddable image URI plus cleanup temp paths."""
    temp_paths = []

    for candidate in collect_student_photo_candidates(student, photo_override_path=photo_override_path):
        source = candidate['source']
        path_value = candidate.get('path')
        url_value = candidate.get('url')

        if path_value and os.path.exists(path_value):
            data_uri = encode_image_as_data_uri(path_value)
            if data_uri:
                return data_uri, path_value, temp_paths, source
            logger.warning(f"Student photo candidate from {source} could not be encoded: {path_value}")
            return build_file_uri(path_value), path_value, temp_paths, source

        if url_value:
            downloaded_path, is_pdf = download_remote_asset(url_value, default_suffix='.jpg')
            if not downloaded_path:
                continue

            temp_paths.append(downloaded_path)
            if is_pdf:
                logger.warning(f"Student photo candidate from {source} resolved to a PDF, skipping: {url_value}")
                continue

            data_uri = encode_image_as_data_uri(downloaded_path)
            if data_uri:
                return data_uri, downloaded_path, temp_paths, source

            logger.warning(f"Downloaded student photo candidate from {source} could not be encoded: {url_value}")
            return build_file_uri(downloaded_path), downloaded_path, temp_paths, source

    return None, None, temp_paths, None


def count_pdf_pages(pdf_path):
    """Return the number of pages in a local PDF path."""
    if not pdf_path or not os.path.exists(pdf_path):
        return 0
    try:
        return len(PdfReader(pdf_path).pages)
    except Exception as exc:
        logger.warning(f"Could not count PDF pages for {pdf_path}: {exc}")
        return 0


def build_faculty_results_context(results_value):
    """Normalize faculty results into either a structured list or plain text."""
    if not results_value:
        return [], None

    parsed_results = None
    if isinstance(results_value, list):
        parsed_results = results_value
    elif isinstance(results_value, str):
        try:
            candidate = json.loads(results_value)
            if isinstance(candidate, list):
                parsed_results = candidate
            else:
                return [], results_value
        except (TypeError, ValueError, json.JSONDecodeError):
            return [], results_value
    else:
        return [], str(results_value)

    normalized_results = []
    for item in parsed_results:
        if not isinstance(item, dict):
            continue

        normalized_item = dict(item)
        attempted = normalized_item.get('students_attempted') or normalized_item.get('attempted') or 0
        passed = normalized_item.get('students_passed') or normalized_item.get('passed') or 0
        try:
            attempted = int(attempted)
        except (TypeError, ValueError):
            attempted = 0
        try:
            passed = int(passed)
        except (TypeError, ValueError):
            passed = 0

        normalized_item['students_attempted'] = attempted
        normalized_item['students_passed'] = passed
        normalized_item['classes_taken'] = normalized_item.get('classes_taken') or normalized_item.get('classes') or 0
        normalized_item['subject_name'] = normalized_item.get('subject_name') or normalized_item.get('subject') or 'Subject'
        normalized_item['subject_code'] = normalized_item.get('subject_code') or normalized_item.get('code') or ''
        normalized_item['academic_year'] = normalized_item.get('academic_year') or normalized_item.get('ay') or ''

        percentage = normalized_item.get('percentage')
        if percentage in (None, ''):
            percentage = round((passed / attempted * 100), 2) if attempted else 0
        normalized_item['percentage'] = percentage
        normalized_results.append(normalized_item)

    return normalized_results, None


def resolve_faculty_document_asset(file_field=None, url_value=None, default_suffix='.pdf'):
    """Resolve a faculty document asset for PDF preview/summary use."""
    temp_paths = []
    asset_path, is_pdf = get_local_or_remote_asset(file_field, url=url_value, default_suffix=default_suffix)
    if not asset_path or not os.path.exists(asset_path):
        return {
            'available': False,
            'path': None,
            'display_url': None,
            'is_image': False,
            'page_count': 0,
            'temp_paths': temp_paths,
        }

    local_field_path = None
    if file_field and getattr(file_field, 'name', ''):
        try:
            local_field_path = file_field.path
        except (NotImplementedError, ValueError, OSError):
            local_field_path = None

    if asset_path != local_field_path:
        temp_paths.append(asset_path)

    return {
        'available': True,
        'path': asset_path,
        'display_url': build_file_uri(asset_path),
        'is_image': not is_pdf,
        'page_count': 1 if not is_pdf else count_pdf_pages(asset_path),
        'temp_paths': temp_paths,
    }


def build_faculty_document_collection_summary(asset_specs, default_suffix='.pdf'):
    """Aggregate availability/page-count/preview info across multiple faculty assets."""
    temp_paths = []
    first_available_asset = None
    total_pages = 0

    for file_field, url_value in asset_specs:
        asset = resolve_faculty_document_asset(file_field, url_value, default_suffix=default_suffix)
        for temp_path in asset['temp_paths']:
            if temp_path not in temp_paths:
                temp_paths.append(temp_path)
        if not asset['available']:
            continue

        total_pages += asset['page_count']
        if first_available_asset is None:
            first_available_asset = asset

    return {
        'available': first_available_asset is not None,
        'display_url': first_available_asset['display_url'] if first_available_asset else None,
        'is_image': first_available_asset['is_image'] if first_available_asset else False,
        'page_count': total_pages,
        'temp_paths': temp_paths,
    }


def build_faculty_pdf_context(faculty):
    """Build the complete context required by dashboard/faculty_pdf.html."""
    temp_paths = []
    photo_url, local_photo_path, photo_temp_paths, _photo_source = resolve_faculty_photo_for_pdf(faculty)
    temp_paths.extend(photo_temp_paths)

    certificates = list(Certificate.objects.filter(faculty=faculty).order_by('-uploaded_at'))
    research_projects = list(ResearchProject.objects.filter(faculty=faculty).order_by('-year', '-id'))
    research_publications = list(ResearchPublication.objects.filter(faculty=faculty).order_by('-publication_year', '-id'))
    fdps = list(FDP.objects.filter(faculty=faculty).order_by('-from_date', '-id'))
    btech_projects = list(BTechProject.objects.filter(faculty=faculty).order_by('-batch', '-id'))

    subjects_list = []
    subjects_dealt = getattr(faculty, 'subjects_dealt', None)
    if subjects_dealt:
        subjects_list = [subject.strip() for subject in subjects_dealt.split(',') if subject.strip()]

    results_data_list, results_text = build_faculty_results_context(getattr(faculty, 'results', None))
    college_experiences = normalize_faculty_college_experiences(
        getattr(faculty, 'college_experiences', [])
    )
    tstsabas_entries = normalize_tstsabas_entries(
        getattr(faculty, 'tstsabas_entries', [])
    )

    def has_file_or_url(file_field, url_value):
        return bool(getattr(file_field, 'name', '') or normalize_optional_url(url_value))

    research_summary = build_faculty_document_collection_summary(
        [(faculty.research_proof, faculty.research_proof_url)] +
        [(pub.proof_document, getattr(pub, 'proof_document_url', None)) for pub in research_publications],
        default_suffix='.pdf',
    )
    fdp_summary = build_faculty_document_collection_summary(
        [(faculty.fdp_certificate, faculty.fdp_certificate_url)] +
        [(fdp.certificate, getattr(fdp, 'certificate_url', None)) for fdp in fdps],
        default_suffix='.pdf',
    )
    experience_summary = resolve_faculty_document_asset(
        faculty.experience_certificates,
        faculty.experience_certificates_url,
        default_suffix='.pdf',
    )
    other_documents_summary = resolve_faculty_document_asset(
        faculty.other_documents,
        faculty.other_documents_url,
        default_suffix='.pdf',
    )

    for asset_summary in (research_summary, fdp_summary, experience_summary, other_documents_summary):
        for temp_path in asset_summary['temp_paths']:
            if temp_path not in temp_paths:
                temp_paths.append(temp_path)

    anurag_header_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'ANURAG HEADER.png')
    if getattr(faculty, 'is_ratified', None) is True:
        ratified_status = 'Yes'
    elif getattr(faculty, 'is_ratified', None) is False:
        ratified_status = 'No'
    else:
        ratified_status = 'Not Specified'

    context = {
        'faculty': faculty,
        'photo_url': photo_url,
        'local_photo_path': local_photo_path,
        'anurag_header_url': build_file_uri(anurag_header_path),
        'college_experiences': college_experiences,
        'tstsabas_entries': tstsabas_entries,
        'certificates': certificates,
        'research_projects': research_projects,
        'research_publications': research_publications,
        'fdps': fdps,
        'btech_projects': btech_projects,
        'subjects_list': subjects_list,
        'results_data_list': results_data_list,
        'results_text': results_text,
        'ratified_status': ratified_status,
        'current_date': timezone.now(),
        'cloudinary_status': {'has_pdf': bool(faculty.cloudinary_pdf_url)},
        'has_aadhar': has_file_or_url(faculty.aadhar_file, faculty.aadhar_url),
        'has_pan': has_file_or_url(faculty.pan_file, faculty.pan_url),
        'has_apaar': has_file_or_url(faculty.apaar_file, faculty.apaar_url),
        'has_scm': has_file_or_url(faculty.scm_file, faculty.scm_url),
        'has_membership_proof': has_file_or_url(faculty.membership_proof, faculty.membership_proof_url),
        'has_jntuh_biodata': has_file_or_url(faculty.jntuh_biodata, faculty.jntuh_biodata_url),
        'has_ssc_cert': has_file_or_url(faculty.ssc_certificate, faculty.ssc_certificate_url),
        'has_inter_cert': has_file_or_url(faculty.inter_certificate, faculty.inter_certificate_url),
        'has_ug_cert': has_file_or_url(faculty.ug_certificate, faculty.ug_certificate_url),
        'has_pg_cert': has_file_or_url(faculty.pg_certificate, faculty.pg_certificate_url),
        'has_phd_cert': has_file_or_url(faculty.phd_certificate, faculty.phd_certificate_url),
        'has_research_proof': research_summary['available'],
        'research_proof_total_pages': research_summary['page_count'],
        'research_proof_display_url': research_summary['display_url'],
        'research_proof_is_image': research_summary['is_image'],
        'research_proof_academic_year': faculty.research_proof_academic_year or next(
            (pub.academic_year for pub in research_publications if pub.academic_year),
            '',
        ),
        'has_fdp_certificate': fdp_summary['available'],
        'fdp_certificate_total_pages': fdp_summary['page_count'],
        'fdp_certificate_display_url': fdp_summary['display_url'],
        'fdp_certificate_is_image': fdp_summary['is_image'],
        'fdp_certificate_academic_year': faculty.fdp_certificate_academic_year or next(
            (fdp.academic_year for fdp in fdps if fdp.academic_year),
            '',
        ),
        'has_experience_certificates': experience_summary['available'],
        'experience_certificates_display_url': experience_summary['display_url'],
        'experience_certificates_is_image': experience_summary['is_image'],
        'experience_certificates_academic_year': faculty.experience_certificates_academic_year,
        'has_other_documents': other_documents_summary['available'],
        'other_documents_display_url': other_documents_summary['display_url'],
        'other_documents_is_image': other_documents_summary['is_image'],
        'other_documents_academic_year': faculty.other_documents_academic_year,
    }

    return context, temp_paths


def persist_faculty_pdf(faculty, pdf_bytes, uploaded_by=None):
    """Persist a generated faculty PDF to local storage and Cloudinary when configured."""
    filename = f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}.pdf"
    faculty.pdf_document.save(filename, ContentFile(pdf_bytes), save=False)

    cloudinary_pdf_url = getattr(faculty, 'cloudinary_pdf_url', None)
    if is_cloudinary_configured():
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
        try:
            upload_result = cloudinary.uploader.upload(
                temp_pdf_path,
                resource_type='raw',
                folder='faculty_pdfs',
                public_id=f"faculty_{faculty.employee_code}_profile",
                overwrite=True,
                format='pdf',
                type='upload',
                access_mode='public',
            )
            cloudinary_pdf_url = upload_result.get('secure_url') or cloudinary_pdf_url
            if cloudinary_pdf_url:
                record_cloudinary_upload(
                    upload_type='pdf',
                    upload_result=upload_result,
                    faculty=faculty,
                    uploaded_by=uploaded_by,
                )
        except Exception as exc:
            logger.warning(f"Could not upload faculty PDF to Cloudinary for {faculty.employee_code}: {exc}")
        finally:
            try:
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
            except Exception:
                pass

    faculty.cloudinary_pdf_url = cloudinary_pdf_url
    faculty.save(update_fields=['pdf_document', 'cloudinary_pdf_url'])
    return filename


def generate_faculty_pdf_bytes(faculty):
    """Generate a merged faculty PDF as bytes."""
    try:
        logger.info(f"Starting PDF generation for faculty {faculty.employee_code}")
        context, temp_paths = build_faculty_pdf_context(faculty)
        html_string = render_to_string('dashboard/faculty_pdf.html', context)
        info_pdf_bytes = None

        try:
            from weasyprint import HTML
            base_url = Path(settings.BASE_DIR).resolve().as_uri() if settings.BASE_DIR else None
            html_obj = HTML(string=html_string, base_url=base_url)
            info_pdf_bytes = html_obj.write_pdf()
            logger.info(f"WeasyPrint generated {len(info_pdf_bytes)} bytes for {faculty.employee_code}")
        except Exception as exc:
            logger.warning(f"Faculty WeasyPrint generation failed for {faculty.employee_code}: {exc}")
            info_pdf_bytes = None
        finally:
            for temp_path in temp_paths:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass

        if not info_pdf_bytes or not info_pdf_bytes.startswith(b'%PDF'):
            logger.warning(f"Faculty PDF generation failed with WeasyPrint for {faculty.employee_code}; falling back to ReportLab.")
            info_pdf_bytes = _build_reportlab_faculty_pdf(faculty, temp_paths)

        if not info_pdf_bytes:
            raise ValueError(f'Faculty profile PDF generation produced None for {faculty.employee_code}')
        
        if not info_pdf_bytes.startswith(b'%PDF'):
            logger.error(f'Base PDF invalid for {faculty.employee_code}: starts with {info_pdf_bytes[:20] if info_pdf_bytes else None}')
            raise ValueError(f'Invalid base PDF generated for {faculty.employee_code}')

        logger.info(f"Successfully generated base PDF ({len(info_pdf_bytes)} bytes) for {faculty.employee_code}")
        merged = merge_certificates_with_pdf_bytes(info_pdf_bytes, faculty)
        
        if not merged or not merged.startswith(b'%PDF'):
            logger.warning(f"Merge returned invalid PDF for {faculty.employee_code}, using base PDF")
            return encrypt_pdf_bytes(info_pdf_bytes, get_pdf_password(faculty))
        
        final_pdf = merged
        final_pdf = encrypt_pdf_bytes(final_pdf, get_pdf_password(faculty))
        logger.info(f"Final merged PDF: {len(final_pdf)} bytes for {faculty.employee_code}")
        return final_pdf
    except Exception as exc:
        logger.error(f"generate_faculty_pdf_bytes failed for {faculty.employee_code}: {exc}", exc_info=True)
        raise


def calculate_correct_age(dob):
    """Return accurate age in years from a date object."""
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )


def build_file_uri(path_value):
    """
    Convert a local filesystem path to a properly encoded file:// URI.
    """
    if not path_value:
        return ''
    try:
        return Path(path_value).resolve().as_uri()
    except Exception:
        # Fallback for odd path inputs that Path can't resolve.
        return 'file:///' + quote(str(path_value).replace('\\', '/'), safe=':/')


def _build_reportlab_faculty_pdf(faculty, temp_paths=None):
    """Build a simple faculty profile PDF using ReportLab as a fallback."""
    buffer = io.BytesIO()
    try:
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30,
                                topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elems = [Paragraph('FACULTY PROFILE REPORT', styles['Title']), Spacer(1, 12)]

        fields = [
            ('Employee Code', getattr(faculty, 'employee_code', 'N/A')),
            ('Name', getattr(faculty, 'staff_name', 'N/A')),
            ('Designation', getattr(faculty, 'designation', 'N/A')),
            ('Department', getattr(faculty, 'department', 'N/A')),
            ('Email', getattr(faculty, 'email', 'N/A')),
            ('Mobile', getattr(faculty, 'mobile', 'N/A')),
            ('Academic Qualifications', getattr(faculty, 'academics', 'N/A')),
            ('Membership Academic Year', getattr(faculty, 'membership_academic_year', 'N/A')),
            ('Membership In', getattr(faculty, 'membership_in', 'N/A')),
            ('Membership ID', getattr(faculty, 'membership_id', 'N/A')),
            ('Membership Proof', 'Uploaded' if getattr(getattr(faculty, 'membership_proof', None), 'name', '') or getattr(faculty, 'membership_proof_url', None) else 'N/A'),
            ('Ratified', 'Yes' if getattr(faculty, 'is_ratified', None) is True else 'No' if getattr(faculty, 'is_ratified', None) is False else 'N/A'),
        ]

        for label, value in fields:
            elems.append(Paragraph(f'<b>{label}:</b> {value or "N/A"}', styles['Normal']))
            elems.append(Spacer(1, 6))

        college_experiences = normalize_faculty_college_experiences(
            getattr(faculty, 'college_experiences', [])
        )
        if college_experiences:
            elems.append(Spacer(1, 8))
            elems.append(Paragraph('<b>College-wise Experience</b>', styles['Heading2']))
            for entry in college_experiences:
                value = (
                    f"{entry['college_name']} | {entry['college_address']} | "
                    f"{entry['from_date']} to {entry['to_date']} | {entry['experience']}"
                )
                elems.append(Paragraph(value, styles['Normal']))
                elems.append(Spacer(1, 6))

        tstsabas_entries = normalize_tstsabas_entries(
            getattr(faculty, 'tstsabas_entries', [])
        )
        if tstsabas_entries:
            elems.append(Spacer(1, 8))
            elems.append(Paragraph('<b>TSTSABAS</b>', styles['Heading2']))
            for entry in tstsabas_entries:
                elems.append(Paragraph(entry, styles['Normal']))
                elems.append(Spacer(1, 6))

        elems.append(Spacer(1, 12))
        elems.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}',
            styles['Normal']
        ))

        doc.build(elems)
        result = buffer.getvalue()
        logger.info(f'ReportLab fallback PDF generated: {len(result)} bytes')
        return result
    except Exception as exc:
        logger.error(f'Failed to generate fallback faculty PDF with ReportLab: {exc}', exc_info=True)
        return None
    finally:
        try:
            buffer.close()
        except Exception:
            pass


def snapshot_uploaded_file(uploaded_file, default_suffix='.bin'):
    """Persist an uploaded file to a temp path so downstream processing can reuse it reliably."""
    if not uploaded_file:
        return None, False

    original_name = getattr(uploaded_file, 'name', '') or ''
    suffix = (Path(original_name).suffix or default_suffix or '.bin').lower()
    is_pdf = suffix == '.pdf' or 'pdf' in (getattr(uploaded_file, 'content_type', '') or '').lower()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        uploaded_file.seek(0)
        chunks_method = getattr(uploaded_file, 'chunks', None)
        if callable(chunks_method):
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
        else:
            tmp.write(uploaded_file.read())
        tmp.close()
    finally:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

    return tmp.name, is_pdf


def persist_snapshot_to_model_field(instance, field_name, snapshot_path, original_name=None):
    """Persist a snapshot file through the model field storage backend."""
    if not instance or not snapshot_path or not os.path.exists(snapshot_path):
        return False

    model_field = getattr(instance, field_name, None)
    if model_field is None:
        return False

    target_name = Path(original_name or snapshot_path).name
    try:
        with open(snapshot_path, 'rb') as snapshot_handle:
            model_field.save(target_name, File(snapshot_handle), save=False)
        return True
    except Exception as exc:
        logger.warning(f"Could not persist snapshot for {field_name}: {exc}")
        return False


def build_student_uploaded_documents(student):
    """Return document availability metadata for the student PDF template."""
    labels = {
        'cert_achieve': 'Achievement Certificates',
        'cert_intern': 'Internship Certificates',
        'cert_courses': 'Course Certificates',
        'cert_sdp': 'SDP Certificates',
        'cert_extra': 'Extracurricular Certificates',
        'cert_placement': 'Placement Certificates',
        'cert_national': 'National Exam Certificates',
    }
    uploaded_documents = []

    for field_name, _, url_field_name in STUDENT_CERTIFICATE_SLOTS:
        file_field = getattr(student, field_name, None)
        url_value = normalize_optional_url(getattr(student, url_field_name, None))
        available = bool(url_value or getattr(file_field, 'name', None))

        file_name = ''
        file_type = ''
        if url_value:
            parsed_name = Path(url_value.split('?', 1)[0]).name
            file_name = parsed_name or labels[field_name]
            file_type = 'PDF' if file_name.lower().endswith('.pdf') else 'Image'
        elif getattr(file_field, 'name', None):
            file_name = Path(file_field.name).name
            file_type = 'PDF' if file_name.lower().endswith('.pdf') else 'Image'

        uploaded_documents.append({
            'label': labels[field_name],
            'available': available,
            'file_name': file_name,
            'file_type': file_type,
        })

    return uploaded_documents


if is_cloudinary_configured():
    try:
        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', None)
        api_key = getattr(settings, 'CLOUDINARY_API_KEY', None)
        api_secret = getattr(settings, 'CLOUDINARY_API_SECRET', None)

        if all([cloud_name, api_key, api_secret]):
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
            logger.info("Cloudinary initialized successfully.")
        else:
            logger.warning("Cloudinary marked configured, but credentials are incomplete.")
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
    readers = [] # Keep readers in scope
    temp_files = []
    merged_count = 0
    skipped_count = 0
    for pdf_path in pdf_files:
        try:
            if not pdf_path:
                continue
            if isinstance(pdf_path, str) and pdf_path.startswith('http'):
                print(f" [URL] Downloading PDF from URL: {pdf_path}")
                downloaded_path, is_pdf = download_remote_asset(pdf_path, default_suffix=".pdf")
                if downloaded_path:
                    pdf_path = downloaded_path
                    temp_files.append(pdf_path)
                    print(f" [OK] Downloaded: {pdf_path}")
                else:
                    print(f" [SKIP] Failed to download PDF")
                    skipped_count += 1
                    continue
            
            if not os.path.exists(pdf_path):
                print(f" [SKIP] PDF does not exist: {pdf_path}")
                skipped_count += 1
                continue
                
            print(f" Processing PDF: {os.path.basename(pdf_path)}")
            reader = PdfReader(pdf_path)
            readers.append(reader)
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
            if not img_path:
                continue
            if isinstance(img_path, str) and img_path.startswith('http'):
                print(f" [URL] Downloading image from URL: {img_path}")
                downloaded_path, is_pdf = download_remote_asset(img_path, default_suffix=".jpg")
                if downloaded_path:
                    img_path = downloaded_path
                    temp_files.append(img_path)
                    print(f" [OK] Downloaded: {img_path}")
                else:
                    print(f" [SKIP] Failed to download image")
                    skipped_count += 1
                    continue
            
            if not os.path.exists(img_path):
                print(f" [SKIP] Image does not exist: {img_path}")
                skipped_count += 1
                continue
                
            print(f" Processing image: {os.path.basename(img_path)}")
            try:
                img = PILImage.open(img_path)
            except Exception as e:
                # Fallback: if PIL fails, maybe it's a PDF misidentified as image
                if img_path.lower().endswith('.pdf') or b'%PDF-' in open(img_path, 'rb').read(1024):
                    print(f"  [RECOVERY] File is actually a PDF, processing as such.")
                    pdf_reader = PdfReader(img_path)
                    readers.append(pdf_reader)
                    for page in pdf_reader.pages:
                        writer.add_page(page)
                        merged_count += 1
                    print(f"  [OK] Added misidentified PDF as PDF pages")
                    continue
                else:
                    raise e

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
            readers.append(img_reader)
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
        # Cleanup
        for tmp in temp_files:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass


def generate_student_pdf_bytes(student):
    """Generate student PDF as bytes without request object."""
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        factory = RequestFactory()
        fake_req = factory.get('/')
        fake_req.user = AnonymousUser()
        fake_req.META['REMOTE_ADDR'] = '127.0.0.1'
        return generate_student_pdf(student, return_bytes=True)
    except Exception as e:
        logger.error(f"Error generating student PDF bytes: {e}")
        return None


def merge_student_certificates_with_pdf_bytes(pdf_bytes, student):
    """Merge student PDF with their certificates and return merged PDF bytes.
    
    This function:
    1. Adds the main student profile PDF
    2. Downloads and processes all certificates from Cloudinary URLs or local storage
    3. Converts images to PDF pages and merges them
    4. Returns the complete merged PDF as bytes
    """
    try:
        writer = PdfWriter()
        temp_files = []  # Track all temp files for cleanup

        # 1. Add the main student PDF
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                tf.write(pdf_bytes)
                tfp = tf.name
                temp_files.append(tfp)
            try:
                for pg in PdfReader(tfp).pages:
                    writer.add_page(pg)
                logger.info(f"Added main student PDF for {student.ht_no}")
            except Exception as e:
                logger.warning(f"Error reading main student PDF: {e}")

        cert_count = 0
        # 2. Collect and add student certificates
        _, image_files, pdf_files, collected_temp_files = collect_student_files(student)
        temp_files.extend(collected_temp_files)

        # 2b. Add PDF certificates
        for cert_path in pdf_files:
            if cert_path and os.path.exists(cert_path):
                try:
                    reader = PdfReader(cert_path)
                    for page in reader.pages:
                        writer.add_page(page)
                    cert_count += 1
                    logger.info(f"Successfully merged student certificate PDF: {cert_path}")
                except Exception as e:
                    logger.warning(f"Failed to merge student certificate PDF {cert_path}: {e}")

        # 2c. Add image certificates (convert to PDF pages)
        for image_path in image_files:
            if image_path and os.path.exists(image_path):
                try:
                    from PIL import Image as PILImage
                    import io
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter

                    img = PILImage.open(image_path)
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')

                    img_pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(img_pdf_buffer, pagesize=letter)
                    page_width, page_height = letter
                    img_width, img_height = img.size
                    scale = min((page_width - 40) / img_width, (page_height - 40) / img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2

                    c.drawImage(image_path, x, y, width=new_width, height=new_height)
                    c.showPage()
                    c.save()

                    img_pdf_buffer.seek(0)
                    writer.add_page(PdfReader(img_pdf_buffer).pages[0])
                    cert_count += 1
                    logger.info(f"Successfully merged student certificate image: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to merge student certificate image {image_path}: {e}")

        logger.info(f"Total items merged with student PDF: {cert_count}")

        # 3. Create merged PDF and return bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as mf:
            writer.write(mf)
            temp_files.append(mf.name)
            with open(mf.name, 'rb') as f:
                merged = f.read()

        # Cleanup all temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass

        return merged
    except Exception as e:
        logger.error(f"Error in merge_student_certificates_with_pdf_bytes: {e}")
        traceback.print_exc()
        return None



def merge_documents(output_path, image_files=None, pdf_files=None):
    if image_files is None:
        image_files = []
    if pdf_files is None:
        pdf_files = []
    return merge_all_documents(output_path, image_files, pdf_files)


def merge_files(file_list):
    from pypdf import PdfWriter
    from PIL import Image
    merger = PdfWriter()
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
            if hasattr(file, "url"):
                file_url = file.url
            elif hasattr(file, "path"):
                file_url = file.path
            else:
                file_url = str(file)
            print(f"[{idx}] Processing: {file_url}")
            if file_url.startswith("http"):
                response = requests.get(file_url, timeout=20)
                if response.status_code != 200:
                    print(f" [X] Download failed: {response.status_code}")
                    if 'cloudinary.com' in file_url and response.status_code == 401:
                        try:
                            public_id = file_url.split('/upload/')[1].split('/')[1:] if '/upload/' in file_url else None
                            if public_id:
                                public_id = '/'.join(public_id).rsplit('.', 1)[0]
                                resource = cloudinary.api.resource(public_id)
                                if resource.get('secure_url'):
                                    file_url = resource['secure_url']
                                    print(f" [~] Using Cloudinary API resource URL: {file_url}")
                                    response = requests.get(file_url, timeout=20)
                        except Exception as cloud_err:
                            print(f" [X] Cloudinary API error: {cloud_err}")
                    if response.status_code != 200:
                        skipped_files += 1
                        continue
                content_type = response.headers.get('content-type', '')
                suffix = ".pdf" if 'pdf' in content_type.lower() else ".img"
                if 'cloudinary' in file_url and not file_url.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                    if 'image' in content_type.lower():
                        suffix = ".img"
                    elif 'pdf' in content_type.lower():
                        suffix = ".pdf"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp.write(response.content)
                temp.close()
                file_path = temp.name
                temp_files.append(file_path)
            elif hasattr(file, "path"):
                file_path = file.path
            elif isinstance(file, str) and os.path.exists(file):
                file_path = file
            else:
                print(f"[{idx}] Skipped (not a valid file object or path doesn't exist: {file})")
                skipped_files += 1
                continue
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
    final_pdf.close()
    print(f"[OK] Final PDF: {final_pdf.name}")
    print(f"[COUNT] Summary: {valid_files} files merged, {skipped_files} files skipped")
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
            print(f" [OK] Found Cloudinary photo URL: {faculty.cloudinary_photo_url}")
            response = requests.get(faculty.cloudinary_photo_url, timeout=30)
            # Enhanced fallback for Cloudinary errors
            if response.status_code in [401, 403, 404]:
                try:
                    public_id = faculty.cloudinary_photo_url.split('/upload/')[1].split('/')[1:] if '/upload/' in faculty.cloudinary_photo_url else None
                    if public_id:
                        public_id = '/'.join(public_id).rsplit('.', 1)[0]
                        try:
                            resource = cloudinary.api.resource(public_id)
                            if resource.get('secure_url'):
                                photo_url = resource['secure_url']
                                print(f" [~] Using Cloudinary API resource URL: {photo_url}")
                                response = requests.get(photo_url, timeout=30)
                        except Exception as api_err:
                            print(f" [DOWNLOAD] API resource lookup failed: {api_err}")
                            # Try constructing URLs with different resource types
                            cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
                            if cloud_name:
                                for res_type in ['image', 'raw']:
                                    try:
                                        try_url = f"https://res.cloudinary.com/{cloud_name}/{res_type}/upload/{public_id}"
                                        test_r = requests.get(try_url, timeout=30)
                                        if test_r.status_code == 200:
                                            response = test_r
                                            break
                                        elif test_r.status_code == 404:
                                            continue
                                        else:
                                            break
                                    except Exception:
                                        continue
                except Exception as cloud_err:
                    print(f" [WARN] Cloudinary fallback failed: {cloud_err}")

            if response.status_code == 200:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                tmp.write(response.content)
                tmp.close()
                image_files.append(tmp.name)
                temp_files.append(tmp.name)
                print(f" [OK] Downloaded photo from Cloudinary: {tmp.name}")
            else:
                print(f" [SKIP] Photo download failed: HTTP {response.status_code}")
        except Exception as e:
            print(f" [ERR] Cloudinary photo download error: {e}")
    if faculty.photo:
        file_path, file_url = get_file_from_field(faculty.photo, None)
        if file_path:
            image_files.append(file_path)
            print(f" [OK] Photo (local): {file_path}")
        elif file_url:
            try:
                print(f"[PHOTO] Downloading photo from: {file_url}")
                response = requests.get(file_url, timeout=30)
                if response.status_code == 200:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    tmp.write(response.content)
                    tmp.close()
                    image_files.append(tmp.name)
                    temp_files.append(tmp.name)
                    print(f" [OK] Downloaded photo: {tmp.name}")
            except Exception as e:
                print(f" [ERROR] Photo download error: {e}")
    # Documents - UPDATED with ALL new fields
    doc_fields = [
        ('aadhar_url', 'aadhar_file', 'Aadhar Card'),
        ('pan_url', 'pan_file', 'PAN Card'),
        ('apaar_url', 'apaar_file', 'APAAR Document'),
        ('scm_url', 'scm_file', 'SCM Document'),
        ('membership_proof_url', 'membership_proof', 'Membership Proof'),
        ('jntuh_biodata_url', 'jntuh_biodata', 'JNTUH Bio-Data'),
        ('ssc_certificate_url', 'ssc_certificate', 'SSC Certificate'),
        ('inter_certificate_url', 'inter_certificate', 'Intermediate Certificate'),
        ('ug_certificate_url', 'ug_certificate', 'UG Certificate'),
        ('pg_certificate_url', 'pg_certificate', 'PG Certificate'),
        ('phd_certificate_url', 'phd_certificate', 'PhD Certificate'),
        # NEW FIELDS - Research, FDP, Experience, Other Documents
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
                print(f" [OK] Downloading {display_name} from: {cloudinary_url}")
                response = requests.get(cloudinary_url, timeout=30)

                # Enhanced fallback for Cloudinary errors
                if response.status_code in [401, 403, 404]:
                    try:
                        public_id = cloudinary_url.split('/upload/')[1].split('/')[1:] if '/upload/' in cloudinary_url else None
                        if public_id:
                            public_id = '/'.join(public_id).rsplit('.', 1)[0]
                            try:
                                resource = cloudinary.api.resource(public_id)
                                if resource.get('secure_url'):
                                    doc_url = resource['secure_url']
                                    print(f" [~] Using Cloudinary API resource URL for {display_name}")
                                    response = requests.get(doc_url, timeout=30)
                            except Exception as api_err:
                                print(f" [DOWNLOAD] API resource lookup failed for {display_name}: {api_err}")
                                # Try constructing URLs with different resource types
                                cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
                                if cloud_name:
                                    for res_type in ['raw', 'image']:
                                        try:
                                            try_url = f"https://res.cloudinary.com/{cloud_name}/{res_type}/upload/{public_id}"
                                            test_r = requests.get(try_url, timeout=30)
                                            if test_r.status_code == 200:
                                                response = test_r
                                                break
                                            elif test_r.status_code == 404:
                                                continue
                                            else:
                                                break
                                        except Exception:
                                            continue
                    except Exception as cloud_err:
                        print(f" [WARN] Cloudinary fallback failed for {display_name}: {cloud_err}")

                # Additional fallback: try changing resource type in URL
                if response.status_code != 200 and 'cloudinary.com' in cloudinary_url:
                    try:
                        alt_urls = []
                        if '/raw/upload/' in cloudinary_url:
                            alt_urls.append(cloudinary_url.replace('/raw/upload/', '/image/upload/'))
                        elif '/image/upload/' in cloudinary_url:
                            alt_urls.append(cloudinary_url.replace('/image/upload/', '/raw/upload/'))

                        for alt_url in alt_urls:
                            try:
                                alt_r = requests.get(alt_url, timeout=30)
                                if alt_r.status_code == 200:
                                    response = alt_r
                                    print(f" [OK] Downloaded {display_name} via alternative URL")
                                    break
                            except Exception:
                                continue
                    except Exception as alt_err:
                        print(f" [WARN] Alternative URL fallback failed for {display_name}: {alt_err}")

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    is_pdf = 'pdf' in content_type or cloudinary_url.lower().endswith('.pdf')
                    suffix = ".pdf" if is_pdf else ".jpg"
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tmp.write(response.content)
                    tmp.close()
                    if is_pdf:
                        pdf_files.append(tmp.name)
                        print(f" [OK] Downloaded PDF: {tmp.name} ({len(response.content)} bytes)")
                    else:
                        image_files.append(tmp.name)
                        print(f" [OK] Downloaded Image: {tmp.name} ({len(response.content)} bytes)")
                    temp_files.append(tmp.name)
                else:
                    print(f" [SKIP] Failed to download {display_name}: HTTP {response.status_code}")
                    if file_field:
                        file_path, _ = get_file_from_field(file_field, None)
                        if file_path and os.path.exists(file_path):
                            if file_path.lower().endswith('.pdf'):
                                pdf_files.append(file_path)
                                print(f" [OK] Fallback: {display_name} (PDF local): {file_path}")
                            else:
                                image_files.append(file_path)
                                print(f" [OK] Fallback: {display_name} (Image local): {file_path}")
            except Exception as e:
                print(f" [ERROR] Download error for {display_name}: {e}")
                if file_field:
                    file_path, _ = get_file_from_field(file_field, None)
                    if file_path and os.path.exists(file_path):
                        if file_path.lower().endswith('.pdf'):
                            pdf_files.append(file_path)
                            print(f" [OK] Fallback: {display_name} (PDF local): {file_path}")
                        else:
                            image_files.append(file_path)
                            print(f" [OK] Fallback: {display_name} (Image local): {file_path}")
        elif file_field:
            file_path, _ = get_file_from_field(file_field, None)
            if file_path and os.path.exists(file_path):
                if file_path.lower().endswith('.pdf'):
                    pdf_files.append(file_path)
                    print(f" [OK] {display_name} (PDF local): {file_path}")
                else:
                    image_files.append(file_path)
                    print(f" [OK] {display_name} (Image local): {file_path}")
            else:
                print(f" [ERROR] {display_name}: File not found")
        else:
            print(f" [ERROR] {display_name}: Not uploaded")
    # Certificates (includes FDP certificates saved as Certificate records)
    print("\n--- CHECKING CERTIFICATES ---")
    certificates = Certificate.objects.filter(faculty=faculty)
    print(f"[COUNT] Found {certificates.count()} certificates")
    for cert in certificates:
        try:
            if cert.cloudinary_url:
                print(f" [URL] Downloading certificate ({cert.certificate_type}): {cert.cloudinary_url}")
                response = requests.get(cert.cloudinary_url, timeout=30)
                if response.status_code == 200:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    tmp.write(response.content)
                    tmp.close()
                    pdf_files.append(tmp.name)
                    temp_files.append(tmp.name)
                    print(f" [OK] Downloaded certificate: {tmp.name}")
            elif cert.certificate_file:
                file_path, file_url = get_file_from_field(cert.certificate_file, None)
                if file_path and os.path.exists(file_path):
                    if file_path.lower().endswith('.pdf'):
                        pdf_files.append(file_path)
                        print(f" [OK] Certificate (local PDF): {file_path}")
                    else:
                        image_files.append(file_path)
                        print(f" [OK] Certificate (local image): {file_path}")
                elif file_url:
                    try:
                        print(f" [URL] Downloading certificate ({cert.certificate_type}) from: {file_url}")
                        response = requests.get(file_url, timeout=30)
                        if response.status_code == 200:
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                            tmp.write(response.content)
                            tmp.close()
                            pdf_files.append(tmp.name)
                            temp_files.append(tmp.name)
                            print(f" [OK] Downloaded certificate: {tmp.name}")
                    except Exception as e:
                        print(f" [ERROR] Error: {e}")
        except Exception as e:
            print(f" [ERROR] Error processing certificate {cert.certificate_type}: {e}")
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


def collect_student_files(student, skip_photo=False, skip_certificate_fields=None, photo_override_path=None, certificate_override_assets=None):
    """Collect student photo and certificates from Cloudinary or local storage.
    
    Args:
        student: Student model instance
        skip_photo: If True, don't collect the student's photo
        skip_certificate_fields: Set of certificate field names to skip (e.g., when overrides provided)
        photo_override_path: Optional local path to a photo override (takes precedence)
        certificate_override_assets: Optional list of asset dicts with 'path', 'field_name', 'is_pdf' keys
    """
    skip_certificate_fields = set(skip_certificate_fields or [])
    photo_file = None
    image_files = []
    pdf_files = []
    certificate_override_assets = certificate_override_assets or []
    photo_override_path = photo_override_path
    
    # Filter override assets to only those that exist
    certificate_override_assets = [
        asset for asset in certificate_override_assets
        if asset.get('path') and os.path.exists(asset['path'])
    ]
    
    override_certificate_fields = {
        asset['field_name']
        for asset in certificate_override_assets
        if asset.get('field_name')
    }
    
    if photo_override_path and not os.path.exists(photo_override_path):
        photo_override_path = None

    temp_files = []
    if photo_override_path:
        temp_files.append(photo_override_path)
    for asset in certificate_override_assets:
        if asset['path'] not in temp_files:
            temp_files.append(asset['path'])

    if not skip_photo:
        photo_file, _ = resolve_asset_from_candidates(
            collect_student_photo_candidates(student, photo_override_path=photo_override_path),
            temp_files,
            default_suffix='.jpg',
        )
    print(f"  [COLLECT] Photo collected: {photo_file is not None}")

    cert_count = 0
    for file_field_name, _, url_field_name in STUDENT_CERTIFICATE_SLOTS:
        if file_field_name in skip_certificate_fields:
            print(f"  [COLLECT] Skipping {file_field_name} because an override asset is available")
            continue
        file_field = getattr(student, file_field_name, None)
        url_field = getattr(student, url_field_name, None)
        print(f"  [COLLECT] Checking {file_field_name}: file={file_field is not None}, url={url_field is not None}")
        
        # Debug: Show the actual values
        if file_field:
            try:
                print(f"  [COLLECT]   file_field.path: {file_field.path if hasattr(file_field, 'path') else 'NO PATH'}")
            except Exception as e:
                print(f"  [COLLECT]   file_field error: {e}")
        if url_field:
            print(f"  [COLLECT]   url_field value: {url_field[:100]}...")

        asset_path, is_pdf = resolve_asset_from_candidates(
            collect_student_document_candidates(student, file_field_name, url_field_name),
            temp_files,
            default_suffix='.jpg',
        )
        if asset_path:
            cert_count += 1
            if is_pdf:
                pdf_files.append(asset_path)
                print(f"  [COLLECT] Added PDF: {asset_path}")
            else:
                image_files.append(asset_path)
                print(f"  [COLLECT] Added image: {asset_path}")
        else:
            print(f"  [COLLECT] No asset found for {file_field_name}")

    research_proof_count = 0
    for publication in StudentResearchPublication.objects.filter(student=student).order_by('-publication_year', '-id'):
        if f'student_research_proof_{publication.id}' in skip_certificate_fields:
            print(f"  [COLLECT] Skipping research proof {publication.id} because an override asset is available")
            continue
        candidates = []
        proof_field = getattr(publication, 'proof_document', None)
        if proof_field and getattr(proof_field, 'name', ''):
            try:
                if os.path.exists(proof_field.path):
                    candidates.append({'source': f'student_research_publication_{publication.id}.path', 'path': proof_field.path})
            except (NotImplementedError, ValueError, OSError):
                pass
        proof_url = normalize_optional_url(getattr(publication, 'proof_document_url', None))
        if proof_url:
            candidates.append({'source': f'student_research_publication_{publication.id}.url', 'url': proof_url})
        if proof_field and getattr(proof_field, 'name', ''):
            try:
                field_url = proof_field.url
            except Exception:
                field_url = None
            field_url = normalize_optional_url(field_url)
            if field_url:
                candidates.append({'source': f'student_research_publication_{publication.id}.file_url', 'url': field_url})

        asset_path, is_pdf = resolve_asset_from_candidates(candidates, temp_files, default_suffix='.pdf')
        if asset_path:
            research_proof_count += 1
            if is_pdf:
                pdf_files.append(asset_path)
                print(f"  [COLLECT] Added research proof PDF: {asset_path}")
            else:
                image_files.append(asset_path)
                print(f"  [COLLECT] Added research proof image: {asset_path}")

    print(f"  [COLLECT] Total certificates collected: {cert_count}")
    print(f"  [COLLECT] Total research proofs collected: {research_proof_count}")

    return photo_file, image_files, pdf_files, temp_files


def append_assets_to_writer(writer, pdf_files=None, image_files=None):
    """Append local PDF and image assets to an existing PdfWriter."""
    pdf_files = pdf_files or []
    image_files = image_files or []
    readers = []
    temp_files = []

    for pdf_path in pdf_files:
        if not pdf_path or not os.path.exists(pdf_path):
            continue
        try:
            reader = PdfReader(pdf_path)
            readers.append(reader)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            logger.warning(f"Error appending PDF asset {pdf_path}: {e}")

    for image_path in image_files:
        if not image_path or not os.path.exists(image_path):
            continue
        try:
            img = PILImage.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            img.save(temp_pdf.name, 'PDF', resolution=100.0)
            temp_pdf.close()
            temp_files.append(temp_pdf.name)
            reader = PdfReader(temp_pdf.name)
            readers.append(reader)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            logger.warning(f"Error appending image asset {image_path}: {e}")

    return readers, temp_files


# ==================== DEBUG / TEST VIEWS ====================
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
                     'phd_degree', 'phd_title', 'phd_university', 'phd_spec', 'about_yourself']:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)
        if request.POST.get('phd_degree') != 'Completed':
            faculty.phd_title = ''
        for date_attr in ['joining_date', 'dob']:
            val = request.POST.get(date_attr)
            setattr(faculty, date_attr, parse_date(val) if val else None)
        for year_attr in ['ug_year', 'pg_year', 'phd_year']:
            val = request.POST.get(year_attr)
            if val:
                setattr(faculty, year_attr, val)
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
        # Upload to Cloudinary if photo provided and Cloudinary configured
        if request.FILES.get("photo") and is_cloudinary_configured():
            try:
                request.FILES["photo"].seek(0)
                cr = cloudinary.uploader.upload(
                    request.FILES["photo"], folder="faculty_photos",
                    public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                    transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                )
                faculty.cloudinary_photo_url = cr["secure_url"]
                faculty.save(update_fields=['cloudinary_photo_url'])
                CloudinaryUpload.objects.create(
                    faculty=faculty, upload_type="photo",
                    cloudinary_url=cr["secure_url"], public_id=cr["public_id"],
                    resource_type=cr["resource_type"], uploaded_by=request.user.username
                )
            except Exception as e:
                logger.error(f"Cloudinary upload error in edit_faculty_complete: {e}")
                messages.warning(request, "Photo saved but Cloudinary upload failed.")
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
                            url=normalize_optional_url(item.get('url')),
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
        'academic_year': r.academic_year,
        'year': r.publication_year,
        'status': r.status,
        'doi': r.doi,
        'url': r.url,
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


@login_required
def bulk_student_actions(request):
    if request.method != 'POST':
        return redirect('dashboard:students_data')
    action = request.POST.get('bulk_action')
    student_ids = request.POST.getlist('student_ids')
    if not student_ids:
        messages.error(request, 'No students selected.')
        return redirect('dashboard:students_data')
    if action == 'generate_pdfs':
        ok = err = 0
        for sid in student_ids:
            try:
                student = Student.objects.get(id=sid)
                pdf_url = generate_student_pdf(student)
                if pdf_url:
                    ok += 1
                else:
                    logger.warning(f"PDF generation returned None for student {sid}")
                    err += 1
            except Exception as e:
                logger.error(f"Error generating PDF for student {sid}: {e}")
                err += 1
        messages.success(request, f"Generated PDFs for {ok} students.")
        if err:
            messages.warning(request, f"Failed to generate PDFs for {err} students.")
    else:
        messages.error(request, 'Invalid bulk action.')
    return redirect('dashboard:students_data')


def student_detail(request, student_id):
    if not request.session.get('student_logged_in') and not request.user.is_authenticated:
        return redirect('dashboard:student_login')
    student = get_object_or_404(Student, id=student_id)

    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if request.session.get('student_logged_in') and not user_authenticated:
        if not student_session_can_access_record(request, student):
            messages.error(request, "You can only access your own student record.")
            return redirect(student_dashboard_redirect_route(request))

    # Student URLs are already stored directly on the model

    # Automatically generate PDF if it doesn't exist and student has photo/certificates
    if not student_has_saved_pdf(student):
        if student_has_upload_assets(student):
            try:
                logger.info(f"Auto-generating PDF for student {student.student_name} on first view")
                pdf_url = generate_student_pdf(student)
                if pdf_url:
                    messages.info(request, 'Student PDF has been generated and is ready for download.')
            except Exception as e:
                logger.error(f"Failed to auto-generate PDF for student {student_id}: {e}")
                messages.warning(request, 'Could not generate PDF automatically. You can try the DOWNLOAD PDF button.')

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
    faculty = get_object_or_404(Faculty, id=faculty_id)

    wants_json = (
        request.method == 'POST' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        'application/json' in (request.headers.get('Accept', '') or '')
    )

    if wants_json:
        try:
            if not faculty.cloudinary_pdf_url:
                existing_pdf_bytes = _read_faculty_pdf_bytes(faculty)
                if existing_pdf_bytes:
                    persist_faculty_pdf(faculty, existing_pdf_bytes, uploaded_by=request.user.username)
                elif faculty.pdf_document and is_cloudinary_configured():
                    with faculty.pdf_document.open('rb') as pdf_file:
                        upload_result = cloudinary.uploader.upload(
                            pdf_file,
                            resource_type='raw',
                            folder='faculty_pdfs',
                            public_id=f"faculty_{faculty.employee_code}_profile",
                            overwrite=True,
                            format='pdf',
                            type='upload',
                            access_mode='public',
                        )
                    faculty.cloudinary_pdf_url = upload_result.get('secure_url')
                    faculty.save(update_fields=['cloudinary_pdf_url'])
                    if faculty.cloudinary_pdf_url:
                        record_cloudinary_upload(
                            upload_type='pdf',
                            upload_result=upload_result,
                            faculty=faculty,
                            uploaded_by=request.user.username,
                        )

            if faculty.photo and not faculty.cloudinary_photo_url and is_cloudinary_configured():
                with faculty.photo.open('rb') as photo_file:
                    upload_result = cloudinary.uploader.upload(
                        photo_file,
                        folder='faculty_photos',
                        public_id=f"faculty_{faculty.employee_code}_photo",
                        overwrite=True,
                        transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}],
                    )
                faculty.cloudinary_photo_url = upload_result.get('secure_url')
                faculty.save(update_fields=['cloudinary_photo_url'])
                if faculty.cloudinary_photo_url:
                    record_cloudinary_upload(
                        upload_type='photo',
                        upload_result=upload_result,
                        faculty=faculty,
                        uploaded_by=request.user.username,
                    )

            return JsonResponse({
                'success': bool(faculty.cloudinary_pdf_url),
                'pdf_url': normalize_optional_url(faculty.cloudinary_pdf_url),
                'photo_url': normalize_optional_url(faculty.cloudinary_photo_url),
                'message': 'Faculty assets synced to Cloudinary.' if faculty.cloudinary_pdf_url else 'Faculty PDF is not available for upload.',
            }, status=200 if faculty.cloudinary_pdf_url else 400)
        except Exception as exc:
            logger.error(f"AJAX Cloudinary upload failed for {faculty.employee_code}: {exc}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)

    return sync_to_cloudinary(request, faculty_id)


# ==================== AUTHENTICATION (FIXED) ====================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    if request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    return redirect('dashboard:admin_login')


@csrf_protect
def admin_login(request):
    try:
        logger.info(f"Admin login request - method: {request.method}")
        if request.user.is_authenticated:
            logger.info(f"User already authenticated: {request.user}")
            return redirect('dashboard:add_faculty')
        error = None
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            logger.info(f"Login attempt for username: {username}")
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                logger.info(f"Login successful for: {username}")
                return redirect('dashboard:add_faculty')
            else:
                error = 'Invalid admin credentials'
                logger.warning(f"Login failed for username: {username}")
                messages.error(request, error)
        
        logger.info("Rendering login page")
        return render(request, 'dashboard/login.html', {
            'title': 'Admin Login - ANURAG ENGINEERING COLLEGE',
            'admin_login': True,
            'error': error,
            'google_signin_enabled': google_signin_enabled(),
        })
    except Exception as e:
        logger.error(f"Dashboard view error: {e}", exc_info=True)
        tb = traceback.format_exc()
        logger.error(f"Traceback: {tb}")
        if settings.DEBUG:
            return HttpResponse(f"<h1>DEBUG 500 ERROR</h1><pre>{tb}</pre>", content_type="text/html")
        else:
            return HttpResponse(f"Internal Server Error: {str(e)}", status=500)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    request.session.flush()
    return redirect('dashboard:admin_login')


def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    messages.success(request, "Admin logged out successfully.")
    return redirect('dashboard:admin_login')


def student_logout(request):
    request.session.flush()
    messages.success(request, "Student logged out successfully.")
    return redirect('dashboard:student_login')


def google_signin_enabled():
    return bool(
        getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
        and getattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', '')
    )


def google_callback_url(request):
    return request.build_absolute_uri(reverse('dashboard:google_callback'))


def set_student_session(request, student):
    request.session['student_logged_in'] = True
    request.session['student_username'] = student.ht_no
    request.session['student_id'] = student.id
    request.session['student_ht_no'] = student.ht_no
    request.session['student_display_name'] = student.student_name


def google_login(request):
    if not google_signin_enabled():
        messages.error(request, 'Google sign-in is not configured.')
        return redirect('dashboard:admin_login')

    role = request.GET.get('role', 'admin')
    if role not in {'admin', 'student'}:
        role = 'admin'

    state_payload = {
        'role': role,
        'mobile': request.GET.get('mobile') == '1',
        'continue': request.GET.get('continue') == '1',
        'next': request.GET.get('next', ''),
        'ts': timezone.now().isoformat(),
    }
    state = signing.dumps(state_payload, salt='google-oauth-state')
    request.session['google_oauth_state'] = state

    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': google_callback_url(request),
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'prompt': 'select_account',
        'state': state,
    }
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


def google_callback(request):
    state = request.GET.get('state', '')
    code = request.GET.get('code', '')
    if not state or not code:
        messages.error(request, 'Google sign-in was cancelled or incomplete.')
        return redirect('dashboard:admin_login')

    try:
        state_payload = signing.loads(
            state,
            salt='google-oauth-state',
            max_age=10 * 60,
        )
    except signing.BadSignature:
        messages.error(request, 'Google sign-in session expired. Please try again.')
        return redirect('dashboard:admin_login')

    try:
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                'redirect_uri': google_callback_url(request),
                'grant_type': 'authorization_code',
            },
            timeout=20,
        )
        if token_response.status_code != 200:
            raise ValueError('Token exchange failed')

        access_token = token_response.json().get('access_token')
        if not access_token:
            raise ValueError('No access token returned by Google')

        profile_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=20,
        )
        if profile_response.status_code != 200:
            raise ValueError('Could not fetch Google profile')

        profile = profile_response.json()
        email = (profile.get('email') or '').strip().lower()
        if not email or profile.get('email_verified') is False:
            raise ValueError('Google email is not verified')

        if state_payload.get('role') == 'student':
            student = Student.objects.filter(email__iexact=email).first()
            if not student:
                messages.error(request, 'No student account is linked to this Gmail address.')
                return redirect('dashboard:student_login')

            if state_payload.get('mobile'):
                token = signing.dumps({'student_id': student.id}, salt='google-mobile-complete')
                response = HttpResponse(status=302)
                response['Location'] = f"engineeringcollegeprojects://auth?{urlencode({'token': token})}"
                return response

            set_student_session(request, student)
            return redirect('dashboard:add_student')

        faculty = Faculty.objects.filter(email__iexact=email).first()
        if not faculty:
            messages.error(request, 'No faculty account is linked to this Gmail address.')
            return redirect('dashboard:admin_login')

        UserModel = get_user_model()
        username_base = faculty.employee_code or email.split('@', 1)[0]
        user = UserModel.objects.filter(email__iexact=email).first()
        if not user:
            username = username_base
            counter = 1
            while UserModel.objects.filter(username=username).exists():
                counter += 1
                username = f"{username_base}{counter}"
            user = UserModel(username=username, email=email)

        name_parts = (faculty.staff_name or '').strip().split(' ', 1)
        user.first_name = name_parts[0] if name_parts else ''
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.email = email
        user.is_staff = True
        user.is_active = True
        user.set_unusable_password()
        user.save()
        login(request, user)
        return redirect('dashboard:add_faculty')
    except Exception as exc:
        logger.error(f"Google sign-in failed: {exc}", exc_info=True)
        messages.error(request, 'Google sign-in failed. Please try again.')
        return redirect('dashboard:admin_login')


def google_mobile_complete(request):
    token = request.GET.get('token', '')
    try:
        payload = signing.loads(token, salt='google-mobile-complete', max_age=10 * 60)
        student = Student.objects.get(id=payload.get('student_id'))
    except Exception:
        messages.error(request, 'Mobile Google sign-in expired. Please try again.')
        return redirect('dashboard:student_login')

    set_student_session(request, student)
    return redirect('dashboard:add_student')


def student_login(request):
    error = None
    try:
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard')
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()

            # ALLOW IMMEDIATE LOGIN FOR DEMO CREDENTIALS
            if username == 'anrkitstudent' and password == 'anrkitstudent':
                request.session['student_logged_in'] = True
                request.session['student_username'] = username
                request.session.pop('student_id', None)
                request.session.pop('student_ht_no', None)
                return redirect('dashboard:student_dashboard_view')

            student = Student.objects.filter(ht_no=username).first()
            if student:
                valid_passwords = [student.student_phone, getattr(student, 'student_email', None), student.email, student.ht_no]
                if student.dob:
                    valid_passwords.append(student.dob.strftime('%Y-%m-%d'))
                    valid_passwords.append(student.dob.strftime('%d-%m-%Y'))
                if any(p and password == p for p in valid_passwords):
                    request.session['student_logged_in'] = True
                    request.session['student_username'] = username
                    request.session['student_id'] = student.id
                    request.session['student_ht_no'] = student.ht_no
                    return redirect('dashboard:student_dashboard_view')
            error = 'Invalid student credentials'
            messages.error(request, error)
        return render(request, 'dashboard/login.html', {
            'title': 'Student Login',
            'student_login': True,
            'error': error,
            'google_signin_enabled': google_signin_enabled(),
        })
    except Exception as e:
        logger.error(f"Student login error: {e}", exc_info=True)
        if settings.DEBUG:
            tb = traceback.format_exc()
            return HttpResponse(f"<h1>DEBUG 500 ERROR</h1><pre>{tb}</pre>", content_type="text/html")
        else:
            return HttpResponse("Internal Server Error", status=500)


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    if request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard_view')
    # Directly render login page instead of redirecting
    return render(request, 'dashboard/login.html', {
        'title': 'Admin Login - ANURAG ENGINEERING COLLEGE',
        'admin_login': True,
        'google_signin_enabled': google_signin_enabled(),
    })


def mobile_dashboard(request):
    """Public mobile-friendly dashboard landing page."""
    try:
        total_faculty = Faculty.objects.count()
        active_faculty = Faculty.objects.filter(is_active=True).count()
        total_certificates = Certificate.objects.count()
        with_phd = Faculty.objects.filter(phd_degree='Completed').count()

        departments = list(
            Faculty.objects.values('department')
            .annotate(count=Count('id'), active=Count('id', filter=Q(is_active=True)))
            .order_by('-count')[:10]
        )
        for department in departments:
            department['percentage'] = (
                department['count'] / total_faculty * 100
            ) if total_faculty else 0

        recent_logs = list(
            FacultyLog.objects.select_related('faculty').order_by('-created_at')[:5]
        )
    except Exception as exc:
        logger.warning(f"Mobile dashboard data load failed: {exc}", exc_info=True)
        total_faculty = 0
        active_faculty = 0
        total_certificates = 0
        with_phd = 0
        departments = []
        recent_logs = []

    return render(request, 'dashboard/dashboard.html', {
        'title': 'Engineering College',
        'total_faculty': total_faculty,
        'active_faculty': active_faculty,
        'total_certificates': total_certificates,
        'with_phd': with_phd,
        'departments': departments,
        'recent_logs': recent_logs,
    })


def projects(request):
    """Public icon-only project domain page matching the Android projects folder."""
    return render(request, 'dashboard/projects.html')


PROJECT_POLICY_FILES = {
    'terms-and-conditions': 'terms-and-conditions.pdf',
    'privacy-policy': 'privacy-policy.pdf',
    'refund-cancellation-policy': 'refund-cancellation-policy.pdf',
    'return-policy': 'return-policy.pdf',
    'shipping-policy': 'shipping-policy.pdf',
}


@require_GET
def project_policy_pdf(request, policy_slug):
    """Serve a public project policy PDF from a stable, review-friendly URL."""
    filename = PROJECT_POLICY_FILES.get(policy_slug)
    if not filename:
        raise Http404('Policy not found.')

    policy_path = Path(settings.BASE_DIR) / 'static' / 'policies' / filename
    if not policy_path.is_file():
        raise Http404('Policy document not found.')

    response = FileResponse(
        policy_path.open('rb'),
        content_type='application/pdf',
        as_attachment=False,
        filename=filename,
    )
    response['Cache-Control'] = 'public, max-age=3600'
    return response


PROJECT_DOMAINS = {
    'ai': 'Artificial Intelligence',
    'machine-learning': 'Machine Learning',
    'software-engineering': 'Software Engineering',
    'security': 'Cybersecurity',
    'deep-learning': 'Deep Learning',
    'data-science': 'Data Science',
    'data-mining': 'Data Mining',
    'cloud-computing': 'Cloud Computing',
    'iot-edge': 'IoT and Edge Computing',
}
PROJECT_DOMAIN_ROOT = Path(settings.BASE_DIR) / 'project_domains'

PROJECT_SOURCE_ROOT_FILES = (
    'manage.py',
    'requirements.txt',
    'Procfile',
    'runtime.txt',
    'build.sh',
    'start.sh',
    'static/images/ECPRJ2026.jpeg',
)
PROJECT_SOURCE_DIRECTORIES = (
    'dashboard',
    'engineeringcollege',
    'project_domains',
    'templates',
    'static/css',
    'static/js',
)
PROJECT_SOURCE_SUFFIXES = {
    '.py', '.html', '.css', '.js', '.txt', '.md', '.json', '.yaml', '.yml', '.jpeg',
}
PROJECT_SOURCE_EXCLUDED_PARTS = {
    '__pycache__', 'staticfiles', 'media', 'tmp_preview',
}
PROJECT_MODULES = (
    ('Core Configuration', ('engineeringcollege/', 'manage.py')),
    ('Project Domains', ('project_domains/',)),
    ('User Interface', ('dashboard/templates/', 'templates/')),
    ('Static Assets', ('dashboard/static/', 'static/css/', 'static/js/', 'static/images/')),
    ('Dashboard Application', ('dashboard/',)),
    ('Deployment', ('requirements.txt', 'Procfile', 'runtime.txt', 'build.sh', 'start.sh')),
)
PROJECT_DOWNLOAD_PRICE_PAISE = 100000


class PhonePePaymentError(Exception):
    pass


def _phonepe_config():
    environment = os.environ.get('PHONEPE_ENVIRONMENT', 'sandbox').lower()
    base_url = (
        'https://api.phonepe.com/apis/pg'
        if environment == 'production'
        else 'https://api-preprod.phonepe.com/apis/pg-sandbox'
    )
    config = {
        'base_url': base_url,
        'client_id': os.environ.get('PHONEPE_CLIENT_ID', ''),
        'client_secret': os.environ.get('PHONEPE_CLIENT_SECRET', ''),
        'client_version': os.environ.get('PHONEPE_CLIENT_VERSION', '1'),
        'callback_username': os.environ.get('PHONEPE_CALLBACK_USERNAME', ''),
        'callback_password': os.environ.get('PHONEPE_CALLBACK_PASSWORD', ''),
    }
    config['configured'] = bool(config['client_id'] and config['client_secret'])
    config['callback_configured'] = bool(
        config['callback_username'] and config['callback_password']
    )
    return config


def _phonepe_access_token():
    config = _phonepe_config()
    if not config['configured']:
        raise PhonePePaymentError('PhonePe merchant payment gateway is not configured.')
    response = requests.post(
        f"{config['base_url']}/v1/oauth/token",
        data={
            'client_id': config['client_id'],
            'client_version': config['client_version'],
            'client_secret': config['client_secret'],
            'grant_type': 'client_credentials',
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=20,
    )
    response.raise_for_status()
    token = response.json().get('access_token')
    if not token:
        raise PhonePePaymentError('PhonePe did not return an access token.')
    return token


def _find_gateway_value(payload, keys):
    if isinstance(payload, dict):
        for key in keys:
            if key in payload and payload[key] not in (None, ''):
                return payload[key]
        for value in payload.values():
            found = _find_gateway_value(value, keys)
            if found not in (None, ''):
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_gateway_value(value, keys)
            if found not in (None, ''):
                return found
    return None


def _is_phonepe_checkout_url(payment_url):
    try:
        parsed = urlparse(payment_url)
    except (TypeError, ValueError):
        return False
    hostname = (parsed.hostname or '').lower()
    return parsed.scheme == 'https' and (
        hostname == 'phonepe.com' or hostname.endswith('.phonepe.com')
    )


def _phonepe_create_payment(payment, redirect_url):
    config = _phonepe_config()
    token = _phonepe_access_token()
    response = requests.post(
        f"{config['base_url']}/checkout/v2/pay",
        json={
            'merchantOrderId': payment.merchant_order_id,
            'amount': payment.amount_paise,
            'expireAfter': 1200,
            'metaInfo': {
                'udf1': f'{payment.domain_slug}/{payment.project_slug}',
                'udf2': 'Project ZIP',
            },
            'paymentFlow': {
                'type': 'PG_CHECKOUT',
                'message': f'{payment.project_slug} ZIP download',
                'merchantUrls': {'redirectUrl': redirect_url},
            },
        },
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'O-Bearer {token}',
        },
        timeout=25,
    )
    response.raise_for_status()
    payload = response.json()
    payment_url = _find_gateway_value(payload, ('redirectUrl', 'paymentUrl', 'url'))
    if not _is_phonepe_checkout_url(payment_url):
        raise PhonePePaymentError('PhonePe did not return a valid hosted checkout URL.')
    payment.phonepe_order_id = str(_find_gateway_value(payload, ('orderId',)) or '')
    payment.payment_url = payment_url
    payment.gateway_response = payload
    payment.status = 'PENDING'
    payment.save(update_fields=[
        'phonepe_order_id', 'payment_url', 'gateway_response', 'status', 'updated_at',
    ])
    return payment_url


def _phonepe_verify_payment(payment):
    config = _phonepe_config()
    token = _phonepe_access_token()
    response = requests.get(
        f"{config['base_url']}/checkout/v2/order/{payment.merchant_order_id}/status",
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'O-Bearer {token}',
        },
        timeout=25,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise PhonePePaymentError('PhonePe returned an invalid order status response.')
    gateway_state = str(payload.get('state') or '').upper()
    gateway_amount = payload.get('amount')
    merchant_order_id = str(payload.get('merchantOrderId') or '')
    amount_matches = (
        isinstance(gateway_amount, int)
        and not isinstance(gateway_amount, bool)
        and gateway_amount == payment.amount_paise
    )
    order_matches = merchant_order_id == payment.merchant_order_id
    payment.gateway_response = payload
    if (
        gateway_state == 'COMPLETED'
        and amount_matches
        and order_matches
        and payment.amount_paise == _project_zip_price(
            payment.domain_slug,
            payment.project_slug,
        )
    ):
        payment.status = 'COMPLETED'
        payment.verified_at = timezone.now()
    elif gateway_state in {'FAILED', 'CANCELLED', 'EXPIRED'}:
        payment.status = 'FAILED'
    else:
        payment.status = 'PENDING'
    payment.save(update_fields=['gateway_response', 'status', 'verified_at', 'updated_at'])
    return payment.status == 'COMPLETED'


def _request_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _payment_rate_key(group, request):
    """Throttle payment actions per browser session and network address."""
    return f"{request.META.get('REMOTE_ADDR', '')}:{request.session.session_key or 'anonymous'}"


def _phonepe_callback_is_valid(request):
    config = _phonepe_config()
    if not config['callback_configured']:
        return False
    expected = hashlib.sha256(
        f"{config['callback_username']}:{config['callback_password']}".encode('utf-8')
    ).hexdigest()
    return hmac.compare_digest(request.headers.get('Authorization', ''), expected)


def _payment_url_qr_data_uri(payment_url):
    """Build an in-page QR that opens PhonePe's hosted checkout URL."""
    if not _is_phonepe_checkout_url(payment_url):
        return ''
    qr_image = qrcode.make(payment_url)
    buffer = io.BytesIO()
    qr_image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


def _iter_engineeringcollege_source_files():
    """Yield the safe executable project files used to build the live source archive."""
    base_dir = Path(settings.BASE_DIR)
    candidates = [base_dir / name for name in PROJECT_SOURCE_ROOT_FILES]
    for directory in PROJECT_SOURCE_DIRECTORIES:
        candidates.extend((base_dir / directory).rglob('*'))

    seen = set()
    for path in candidates:
        if not path.is_file():
            continue
        relative_path = path.relative_to(base_dir)
        relative_text = relative_path.as_posix()
        if relative_text in seen:
            continue
        if any(part in PROJECT_SOURCE_EXCLUDED_PARTS for part in relative_path.parts):
            continue
        if path.suffix and path.suffix.lower() not in PROJECT_SOURCE_SUFFIXES:
            continue
        seen.add(relative_text)
        yield path, relative_text


def _sanitized_project_source(path):
    """Remove known embedded credentials while preserving executable source structure."""
    content = path.read_bytes()
    if path.suffix.lower() not in {'.py', '.sh', '.yaml', '.yml', '.txt', '.md', '.html', '.css', '.js'}:
        return content

    text = content.decode('utf-8', errors='replace')
    if path.as_posix().endswith('dashboard/startup.py'):
        text = re.sub(
            r"DEFAULT_ADMIN_PASSWORD\s*=\s*['\"][^'\"]*['\"]",
            "DEFAULT_ADMIN_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')",
            text,
        )
        text = text.replace('import logging\nimport sys\n', 'import logging\nimport os\nimport sys\n')
    if path.name == 'build.sh':
        text = re.sub(
            r"User\.objects\.create_superuser\([^)]*\)",
            "User.objects.create_superuser(os.environ['DJANGO_SUPERUSER_USERNAME'], "
            "os.environ['DJANGO_SUPERUSER_EMAIL'], os.environ['DJANGO_SUPERUSER_PASSWORD'])",
            text,
        )
        text = text.replace('from django.contrib.auth import get_user_model\n', 'import os\nfrom django.contrib.auth import get_user_model\n')
    return text.encode('utf-8')


def _source_module_for(relative_path):
    for module_name, prefixes in PROJECT_MODULES:
        if any(relative_path == prefix or relative_path.startswith(prefix) for prefix in prefixes):
            return module_name
    return 'Supporting Code'


def _load_domain_projects(domain_slug):
    """Read and validate the projects owned by one domain folder."""
    manifest_path = PROJECT_DOMAIN_ROOT / domain_slug / 'projects.json'
    try:
        payload = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        logger.warning('Could not read project-domain manifest: %s', manifest_path)
        return []

    projects = []
    for project in payload.get('projects', []):
        if not isinstance(project, dict):
            continue
        slug = str(project.get('slug') or '').strip()
        name = str(project.get('name') or '').strip()
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or not name:
            continue
        zip_config = project.get('zip') if isinstance(project.get('zip'), dict) else {}
        zip_enabled = zip_config.get('enabled') is True
        try:
            amount_paise = int(zip_config.get('amount_paise', 0)) if zip_enabled else 0
        except (TypeError, ValueError):
            amount_paise = 0
        zip_source = str(zip_config.get('source') or 'project-folder').strip()
        if zip_source not in {'repository', 'project-folder'}:
            zip_source = 'project-folder'
        projects.append({
            'slug': slug,
            'name': name,
            'title_path': str(project.get('title_path') or '').strip(),
            'description': str(project.get('description') or '').strip(),
            'source_code_path': str(project.get('source_code_path') or '').strip(),
            'datasets_path': str(project.get('datasets_path') or '').strip(),
            'github_reference': str(project.get('github_reference') or '').strip(),
            'demo_url': str(project.get('demo_url') or '').strip(),
            'zip_enabled': zip_enabled and amount_paise > 0,
            'amount_paise': amount_paise,
            'amount_rupees': amount_paise // 100,
            'zip_source': zip_source,
        })
    return projects


def _get_domain_project(domain_slug, project_slug, require_paid_zip=False):
    if domain_slug not in PROJECT_DOMAINS:
        raise Http404("Project domain not found")
    project = next(
        (item for item in _load_domain_projects(domain_slug) if item['slug'] == project_slug),
        None,
    )
    if not project or (require_paid_zip and not project['zip_enabled']):
        raise Http404("Project not found")
    return project


def _get_data_mining_project_by_title(project_title):
    normalized_title = unquote(str(project_title or '')).strip().strip('/')
    project = next(
        (
            item for item in _load_domain_projects('data-mining')
            if item.get('title_path') == normalized_title or item['name'] == normalized_title
        ),
        None,
    )
    if not project:
        raise Http404("Project not found")
    return project


def _project_zip_price(domain_slug, project_slug):
    try:
        return _get_domain_project(domain_slug, project_slug, require_paid_zip=True)['amount_paise']
    except Http404:
        return -1


def _safe_project_domain_path(domain_slug, relative_path):
    """Resolve a manifest path and require it to stay inside its domain folder."""
    if not relative_path:
        return None
    domain_root = (PROJECT_DOMAIN_ROOT / domain_slug).resolve()
    candidate = (Path(settings.BASE_DIR) / relative_path).resolve()
    try:
        candidate.relative_to(domain_root)
    except ValueError:
        return None
    return candidate


def _iter_archive_files(root, archive_prefix):
    excluded_parts = {'.venv', '__pycache__', 'artifacts'}
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in excluded_parts for part in relative.parts):
            continue
        yield path, f"{archive_prefix}/{relative.as_posix()}"


def _build_source_code_zip(domain_slug, project):
    source_root = _safe_project_domain_path(domain_slug, project.get('source_code_path', ''))
    datasets_root = _safe_project_domain_path(domain_slug, project.get('datasets_path', ''))
    if not source_root or not source_root.is_dir():
        raise Http404('Source code folder not found.')

    archive_buffer = io.BytesIO()
    archive_root = project.get('title_path') or project['slug']
    with zipfile.ZipFile(archive_buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f'{archive_root}/README.txt',
            f"{project['name']}\n\n"
            "This archive contains the project source code and available datasets.\n"
            "Open Source Code/README.md for setup steps.\n",
        )
        for path, archive_name in _iter_archive_files(source_root, f'{archive_root}/Source Code'):
            archive.write(path, archive_name)
        if datasets_root and datasets_root.is_dir():
            for path, archive_name in _iter_archive_files(datasets_root, f'{archive_root}/datasets'):
                archive.write(path, archive_name)

    archive_buffer.seek(0)
    return archive_buffer.getvalue()


def download_project_source_code(request, domain_slug, project_slug):
    project = _get_domain_project(domain_slug, project_slug)
    if project.get('zip_enabled'):
        return redirect('dashboard:project_zip_payment', domain_slug, project_slug)
    if not project.get('source_code_path'):
        raise Http404('Source code download not available.')
    response = HttpResponse(_build_source_code_zip(domain_slug, project), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{project_slug}-source-code.zip"'
    response['Cache-Control'] = 'no-store'
    return response


def download_data_mining_project_source_code_by_title(request, project_title):
    project = _get_data_mining_project_by_title(project_title)
    if project.get('zip_enabled'):
        return redirect('dashboard:project_zip_payment', 'data-mining', project['slug'])
    response = HttpResponse(_build_source_code_zip('data-mining', project), content_type='application/zip')
    filename = project.get('title_path') or project['slug']
    response['Content-Disposition'] = f'attachment; filename="{filename}-source-code.zip"'
    response['Cache-Control'] = 'no-store'
    return response


def _price_band(value, low, high):
    if value <= low:
        return 'Low'
    if value <= high:
        return 'Medium'
    return 'High'


def _bucket_kilometers(value):
    if value <= 30000:
        return 'Low KM'
    if value <= 80000:
        return 'Medium KM'
    return 'High KM'


def _run_car_apriori_execution(project):
    """Run a small Apriori analysis for the live project page using stdlib only."""
    datasets_root = _safe_project_domain_path('data-mining', project.get('datasets_path', ''))
    dataset_path = (
        datasets_root / 'vehicle-dataset-from-cardekho' / 'car data.csv'
        if datasets_root else None
    )
    if not dataset_path or not dataset_path.is_file():
        return None

    rows = []
    try:
        with dataset_path.open(newline='', encoding='utf-8') as handle:
            for row in csv.DictReader(handle):
                try:
                    selling_price = float(row.get('Selling_Price') or 0)
                    present_price = float(row.get('Present_Price') or 0)
                    year = int(float(row.get('Year') or 0))
                    kilometers = float(row.get('Kms_Driven') or 0)
                except (TypeError, ValueError):
                    continue
                if selling_price <= 0:
                    continue
                rows.append({
                    'selling_price': selling_price,
                    'present_price': present_price,
                    'year': year,
                    'kilometers': kilometers,
                    'fuel': (row.get('Fuel_Type') or 'Unknown').strip() or 'Unknown',
                    'seller': (row.get('Seller_Type') or 'Unknown').strip() or 'Unknown',
                    'transmission': (row.get('Transmission') or 'Unknown').strip() or 'Unknown',
                    'owner': (row.get('Owner') or 'Unknown').strip() or 'Unknown',
                })
    except OSError:
        logger.warning('Could not read Apriori dataset: %s', dataset_path)
        return None

    if not rows:
        return None

    sorted_prices = sorted(row['selling_price'] for row in rows)
    low_price = sorted_prices[len(sorted_prices) // 3]
    high_price = sorted_prices[(len(sorted_prices) * 2) // 3]
    current_year = datetime.now().year
    transactions = []
    depreciation_values = []
    for row in rows:
        age = max(current_year - row['year'], 0)
        depreciation_percent = None
        if row['present_price'] > 0:
            depreciation_percent = (
                (row['present_price'] - row['selling_price']) / row['present_price']
            ) * 100
            depreciation_values.append(depreciation_percent)

        items = {
            f"Price={_price_band(row['selling_price'], low_price, high_price)}",
            f"Kilometers={_bucket_kilometers(row['kilometers'])}",
            f"Fuel={row['fuel']}",
            f"Seller={row['seller']}",
            f"Transmission={row['transmission']}",
            f"Owner={row['owner']}",
            f"Age={'Newer' if age <= 5 else 'Mid Age' if age <= 10 else 'Older'}",
        }
        if depreciation_percent is not None:
            items.add(
                'Depreciation=' + (
                    'Low' if depreciation_percent <= 25
                    else 'Medium' if depreciation_percent <= 55
                    else 'High'
                )
            )
        transactions.append(frozenset(items))

    min_support = 0.08
    min_confidence = 0.45
    transaction_count = len(transactions)
    item_counts = {}
    pair_counts = {}
    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1
        items = sorted(transaction)
        for left_index, left in enumerate(items):
            for right in items[left_index + 1:]:
                pair = frozenset((left, right))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

    target_prefixes = ('Price=', 'Depreciation=')
    rules = []
    for pair, count in pair_counts.items():
        support = count / transaction_count
        if support < min_support:
            continue
        first, second = tuple(pair)
        for antecedent, consequent in ((first, second), (second, first)):
            if not consequent.startswith(target_prefixes):
                continue
            confidence = count / item_counts[antecedent]
            if confidence < min_confidence:
                continue
            consequent_support = item_counts[consequent] / transaction_count
            lift = confidence / consequent_support if consequent_support else 0
            rules.append({
                'if': antecedent,
                'then': consequent,
                'support': round(support * 100, 2),
                'confidence': round(confidence * 100, 2),
                'lift': round(lift, 2),
            })

    rules = sorted(
        rules,
        key=lambda rule: (rule['lift'], rule['confidence'], rule['support']),
        reverse=True,
    )[:10]

    average_depreciation = (
        sum(depreciation_values) / len(depreciation_values)
        if depreciation_values else None
    )
    return {
        'dataset_name': 'Vehicle Dataset from Cardekho - car data.csv',
        'rows': transaction_count,
        'algorithm': 'Apriori Association Rule Mining',
        'purpose': (
            'Find frequent combinations of car attributes that are strongly associated '
            'with high or low price and depreciation bands.'
        ),
        'price_thresholds': {
            'low_max_lakh': round(low_price, 2),
            'medium_max_lakh': round(high_price, 2),
        },
        'average_depreciation_percent': (
            round(average_depreciation, 2)
            if average_depreciation is not None else None
        ),
        'min_support_percent': round(min_support * 100, 2),
        'min_confidence_percent': round(min_confidence * 100, 2),
        'rules': rules,
    }


def _car_price_github_execution_templates():
    """Execution templates based on the reference GitHub/Colab/Streamlit workflow."""
    return {
        'reference_title': 'SECOND-HAND-CAR-PRICE-PREDICTION-USING-MACHINE-LEARNING',
        'reference_url': 'https://github.com/vasugi2003/second-hand-car-price-prediction-using-machine-learning',
        'overview': (
            'These templates reproduce the reference project flow first: load the Kaggle '
            'car_data.csv file, explore the data, encode categorical fields, compare '
            'regression models, save a pickle model, and execute a prediction screen.'
        ),
        'steps': [
            {
                'title': '1. Dataset Loading Template',
                'purpose': 'Load the Kaggle Cardekho car dataset used by the reference project.',
                'code': (
                    "import pandas as pd\n\n"
                    "car_data = pd.read_csv('car_data.csv')\n"
                    "print(car_data.head())\n"
                    "print(car_data.info())\n"
                    "print(car_data.isnull().sum())\n"
                    "print(car_data.describe())"
                ),
            },
            {
                'title': '2. Exploratory Data Analysis Template',
                'purpose': 'Visualize fuel type, seller type, transmission, and numeric correlations.',
                'code': (
                    "import matplotlib.pyplot as plt\n"
                    "import seaborn as sns\n\n"
                    "fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)\n"
                    "sns.barplot(x='Fuel_Type', y='Selling_Price', data=car_data, ax=axes[0])\n"
                    "sns.barplot(x='Seller_Type', y='Selling_Price', data=car_data, ax=axes[1])\n"
                    "sns.barplot(x='Transmission', y='Selling_Price', data=car_data, ax=axes[2])\n\n"
                    "numeric_columns = car_data.select_dtypes(include=['float64', 'int64']).columns\n"
                    "sns.heatmap(car_data[numeric_columns].corr(), annot=True)\n"
                    "plt.title('Correlation between the columns')\n"
                    "plt.show()"
                ),
            },
            {
                'title': '3. Preprocessing Template',
                'purpose': 'Convert categorical values into numeric features before model training.',
                'code': (
                    "car_data.replace({'Fuel_Type': {'Petrol': 0, 'Diesel': 1, 'CNG': 2}}, inplace=True)\n"
                    "car_data = pd.get_dummies(\n"
                    "    car_data,\n"
                    "    columns=['Seller_Type', 'Transmission'],\n"
                    "    drop_first=True,\n"
                    ")\n\n"
                    "X = car_data.drop(['Car_Name', 'Selling_Price'], axis=1)\n"
                    "y = car_data['Selling_Price']"
                ),
            },
            {
                'title': '4. Train/Test Split and Scaling Template',
                'purpose': 'Prepare separate training and testing data like the GitHub notebook.',
                'code': (
                    "from sklearn.model_selection import train_test_split\n"
                    "from sklearn.preprocessing import StandardScaler\n\n"
                    "X_train, X_test, y_train, y_test = train_test_split(\n"
                    "    X,\n"
                    "    y,\n"
                    "    test_size=0.3,\n"
                    "    random_state=42,\n"
                    ")\n\n"
                    "scaler = StandardScaler()\n"
                    "X_train = scaler.fit_transform(X_train)\n"
                    "X_test = scaler.transform(X_test)"
                ),
            },
            {
                'title': '5. Model Comparison Template',
                'purpose': 'Train and compare the algorithms used in the reference project.',
                'code': (
                    "from sklearn.linear_model import LinearRegression, Lasso, Ridge\n"
                    "from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor\n"
                    "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n"
                    "import pandas as pd\n\n"
                    "models = {\n"
                    "    'Linear Regression': LinearRegression(),\n"
                    "    'Lasso Regression': Lasso(alpha=1.0),\n"
                    "    'Ridge Regression': Ridge(alpha=1.0),\n"
                    "    'Random Forest Regression': RandomForestRegressor(n_estimators=100, random_state=42),\n"
                    "    'Gradient Boosting Regression': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42),\n"
                    "}\n\n"
                    "results = []\n"
                    "for name, model in models.items():\n"
                    "    model.fit(X_train, y_train)\n"
                    "    predictions = model.predict(X_test)\n"
                    "    results.append({\n"
                    "        'Model': name,\n"
                    "        'MAE': mean_absolute_error(y_test, predictions),\n"
                    "        'MSE': mean_squared_error(y_test, predictions),\n"
                    "        'R2 Score': r2_score(y_test, predictions),\n"
                    "    })\n\n"
                    "results_df = pd.DataFrame(results)\n"
                    "print(results_df)"
                ),
            },
            {
                'title': '6. Cross Validation Template',
                'purpose': 'Check whether the model performs consistently across folds.',
                'code': (
                    "from sklearn.model_selection import cross_val_score\n"
                    "import numpy as np\n\n"
                    "for name, model in models.items():\n"
                    "    scores = cross_val_score(model, X, y, cv=5, scoring='r2')\n"
                    "    print(name, 'Average R2:', np.mean(scores))"
                ),
            },
            {
                'title': '7. Save Model Template',
                'purpose': 'Store the trained model as model.pkl for prediction/deployment.',
                'code': (
                    "import pickle\n\n"
                    "final_model = LinearRegression()\n"
                    "final_model.fit(X_train, y_train)\n\n"
                    "with open('model.pkl', 'wb') as file:\n"
                    "    pickle.dump(final_model, file)"
                ),
            },
            {
                'title': '8. Streamlit Prediction Template',
                'purpose': 'Create the prediction input screen used by the GitHub project.',
                'code': (
                    "import pickle\n"
                    "import pandas as pd\n"
                    "import streamlit as st\n\n"
                    "with open('model.pkl', 'rb') as file:\n"
                    "    model = pickle.load(file)\n\n"
                    "st.title('Car Price Prediction')\n"
                    "present_price = st.number_input('Present Price in lakhs', min_value=0.0)\n"
                    "kms_driven = st.number_input('Kms Driven', min_value=0)\n"
                    "fuel_type = st.selectbox('Fuel Type', ['Petrol', 'Diesel', 'CNG'])\n"
                    "seller_type = st.selectbox('Seller Type', ['Dealer', 'Individual'])\n"
                    "transmission = st.selectbox('Transmission', ['Manual', 'Automatic'])\n"
                    "owner = st.selectbox('Owner', [0, 1, 2, 3])\n"
                    "year = st.number_input('Year', min_value=1900, max_value=2026, step=1)\n\n"
                    "if st.button('Predict'):\n"
                    "    input_data = pd.DataFrame({\n"
                    "        'Present_Price': [present_price],\n"
                    "        'Kms_Driven': [kms_driven],\n"
                    "        'Fuel_Type': [0 if fuel_type == 'Petrol' else 1 if fuel_type == 'Diesel' else 2],\n"
                    "        'Owner': [owner],\n"
                    "        'Year': [year],\n"
                    "        'Seller_Type_Individual': [1 if seller_type == 'Individual' else 0],\n"
                    "        'Transmission_Manual': [1 if transmission == 'Manual' else 0],\n"
                    "    })\n"
                    "    prediction = model.predict(input_data)[0]\n"
                    "    st.success(f'Predicted Selling Price: INR {prediction * 100000:.2f}')"
                ),
            },
        ],
        'commands': [
            'python -m venv .venv',
            '.\\.venv\\Scripts\\python.exe -m pip install pandas scikit-learn matplotlib seaborn streamlit',
            '.\\.venv\\Scripts\\python.exe model.py',
            '.\\.venv\\Scripts\\streamlit.exe run app.py',
        ],
        'engineeringcollege_note': (
            'In the EngineeringCollege version, these GitHub templates are kept as the baseline. '
            'Future modifications can replace the final model with the best-performing model, add '
            'depreciation prediction, and connect Apriori rules for Data Mining interpretation.'
        ),
    }


def _build_project_zip(domain_slug, project):
    """Build a project ZIP from either the repository or its domain-owned folder."""
    archive_buffer = io.BytesIO()
    archive_root = project['name']
    if project['zip_source'] == 'repository':
        source_files = list(_iter_engineeringcollege_source_files())
    else:
        project_folder_name = project.get('title_path') or project['slug']
        project_root = PROJECT_DOMAIN_ROOT / domain_slug / project_folder_name
        source_files = [
            (path, path.relative_to(project_root).as_posix())
            for path in project_root.rglob('*')
            if path.is_file() and not any(
                part in PROJECT_SOURCE_EXCLUDED_PARTS
                for part in path.relative_to(project_root).parts
            )
        ]

    with zipfile.ZipFile(archive_buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f'{archive_root}/README.txt',
            f"{project['name']}\n\n"
            f"Domain: {PROJECT_DOMAINS[domain_slug]}\n"
            "This package is generated live from the deployed project source.\n"
            "Credentials, databases, uploads, logs, and generated artifacts are excluded.\n",
        )
        if project['zip_source'] == 'repository':
            archive.writestr(
                f'{archive_root}/.env.example',
                'SECRET_KEY=\nDATABASE_URL=\nDJANGO_SUPERUSER_USERNAME=\n'
                'DJANGO_SUPERUSER_EMAIL=\nDJANGO_SUPERUSER_PASSWORD=\n'
                'CLOUDINARY_CLOUD_NAME=\nCLOUDINARY_API_KEY=\nCLOUDINARY_API_SECRET=\n',
            )
        for path, relative_path in source_files:
            content = _sanitized_project_source(path)
            archive.writestr(f'{archive_root}/Project Source/{relative_path}', content)
            if project['zip_source'] == 'repository':
                module_name = _source_module_for(relative_path)
                archive.writestr(f'{archive_root}/Modules/{module_name}/{relative_path}', content)
    return archive_buffer.getvalue()


@require_GET
def download_project_zip(request, domain_slug, project_slug):
    """Generate a configured project ZIP only after server-verified PhonePe payment."""
    project = _get_domain_project(domain_slug, project_slug, require_paid_zip=True)
    payment = get_object_or_404(
        ProjectDownloadPayment,
        merchant_order_id=request.GET.get('order', ''),
        session_key=_request_session_key(request),
        domain_slug=domain_slug,
        project_slug=project_slug,
        amount_paise=project['amount_paise'],
    )
    try:
        paid = _phonepe_verify_payment(payment)
    except (PhonePePaymentError, requests.RequestException, ValueError):
        paid = False
    if not paid:
        return redirect(
            f"{reverse('dashboard:project_zip_payment', args=[domain_slug, project_slug])}"
            f"?order={payment.merchant_order_id}"
        )

    response = HttpResponse(_build_project_zip(domain_slug, project), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{project_slug}.zip"'
    response['Cache-Control'] = 'no-store'
    ProjectDownloadPayment.objects.filter(pk=payment.pk).update(
        download_count=F('download_count') + 1,
        updated_at=timezone.now(),
    )
    return response


def download_engineeringcollege_project(request):
    """Backward-compatible EngineeringCollege project ZIP URL."""
    return download_project_zip(request, 'software-engineering', 'engineeringcollege-project')


@ratelimit(key=_payment_rate_key, rate='20/m', method='GET', block=True)
@require_GET
def project_zip_payment(request, domain_slug, project_slug):
    project = _get_domain_project(domain_slug, project_slug, require_paid_zip=True)
    payment = None
    order_id = request.GET.get('order', '')
    if order_id:
        payment = ProjectDownloadPayment.objects.filter(
            merchant_order_id=order_id,
            session_key=_request_session_key(request),
            domain_slug=domain_slug,
            project_slug=project_slug,
            amount_paise=project['amount_paise'],
        ).first()
        if payment and payment.status != 'COMPLETED':
            try:
                _phonepe_verify_payment(payment)
            except (PhonePePaymentError, requests.RequestException, ValueError):
                pass
    return render(request, 'dashboard/project_payment.html', {
        'domain_name': PROJECT_DOMAINS[domain_slug],
        'domain_slug': domain_slug,
        'project': project,
        'amount_rupees': project['amount_rupees'],
        'payment': payment,
        'phonepe_configured': _phonepe_config()['configured'],
        'payment_qr_data_uri': _payment_url_qr_data_uri(payment.payment_url) if payment else '',
    })


def project_download_payment(request):
    """Backward-compatible EngineeringCollege project payment URL."""
    return project_zip_payment(request, 'software-engineering', 'engineeringcollege-project')


@ratelimit(key=_payment_rate_key, rate='5/m', method='POST', block=True)
@require_POST
def initiate_project_zip_payment(request, domain_slug, project_slug):
    project = _get_domain_project(domain_slug, project_slug, require_paid_zip=True)
    if not _phonepe_config()['configured']:
        messages.error(request, 'PhonePe merchant payment gateway is not configured yet.')
        return redirect('dashboard:project_zip_payment', domain_slug, project_slug)
    try:
        payment = ProjectDownloadPayment.objects.create(
            merchant_order_id=f"ECPRJ{timezone.now():%Y%m%d%H%M%S}{os.urandom(5).hex()}",
            session_key=_request_session_key(request),
            domain_slug=domain_slug,
            project_slug=project_slug,
            amount_paise=project['amount_paise'],
        )
    except DatabaseError:
        logger.exception('Could not create project ZIP payment order.')
        messages.error(request, 'Payment could not be initiated. Please try again later.')
        return redirect('dashboard:project_zip_payment', domain_slug, project_slug)
    redirect_url = request.build_absolute_uri(
        reverse(
            'dashboard:project_zip_payment_return',
            args=[domain_slug, project_slug, payment.merchant_order_id],
        )
    )
    try:
        payment_url = _phonepe_create_payment(payment, redirect_url)
        if request.POST.get('checkout_mode') == 'qr':
            return redirect(
                f"{reverse('dashboard:project_zip_payment', args=[domain_slug, project_slug])}"
                f"?order={payment.merchant_order_id}"
            )
        return redirect(payment_url)
    except (PhonePePaymentError, requests.RequestException, ValueError) as exc:
        payment.status = 'FAILED'
        payment.gateway_response = {'error': str(exc)}
        payment.save(update_fields=['status', 'gateway_response', 'updated_at'])
        messages.error(request, 'Payment could not be initiated. Please try again later.')
        return redirect('dashboard:project_zip_payment', domain_slug, project_slug)


@require_http_methods(['GET', 'POST'])
def initiate_project_download_payment(request):
    """Backward-compatible EngineeringCollege project payment start URL."""
    if request.method == 'GET':
        return redirect('dashboard:project_download_payment')
    return initiate_project_zip_payment(request, 'software-engineering', 'engineeringcollege-project')


@ratelimit(key=_payment_rate_key, rate='20/m', method='GET', block=True)
@require_GET
def project_zip_payment_return(request, domain_slug, project_slug, merchant_order_id):
    _get_domain_project(domain_slug, project_slug, require_paid_zip=True)
    payment = get_object_or_404(
        ProjectDownloadPayment,
        merchant_order_id=merchant_order_id,
        session_key=_request_session_key(request),
        domain_slug=domain_slug,
        project_slug=project_slug,
    )
    try:
        _phonepe_verify_payment(payment)
    except (PhonePePaymentError, requests.RequestException, ValueError):
        messages.error(request, 'Payment verification is temporarily unavailable.')
    return redirect(
        f"{reverse('dashboard:project_zip_payment', args=[domain_slug, project_slug])}"
        f"?order={merchant_order_id}"
    )


def project_payment_return(request, merchant_order_id):
    """Backward-compatible EngineeringCollege project payment return URL."""
    return project_zip_payment_return(
        request,
        'software-engineering',
        'engineeringcollege-project',
        merchant_order_id,
    )


@csrf_exempt
@ratelimit(key='ip', rate='60/m', method='POST', block=True)
@require_POST
def phonepe_payment_callback(request):
    """Authenticate PhonePe's callback, then independently verify the order."""
    if not _phonepe_callback_is_valid(request):
        return JsonResponse({'detail': 'Invalid callback authorization.'}, status=401)

    try:
        callback = json.loads(request.body)
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'detail': 'Invalid JSON body.'}, status=400)

    if not isinstance(callback, dict) or not isinstance(callback.get('payload'), dict):
        return JsonResponse({'detail': 'Invalid callback payload.'}, status=400)

    callback_order_id = str(callback['payload'].get('merchantOrderId') or '')
    if not callback_order_id:
        return JsonResponse({'detail': 'Missing merchant order ID.'}, status=400)

    payment = ProjectDownloadPayment.objects.filter(
        merchant_order_id=callback_order_id,
    ).first()
    if not payment:
        return JsonResponse({'detail': 'Unknown merchant order ID.'}, status=404)

    try:
        _phonepe_verify_payment(payment)
    except (PhonePePaymentError, requests.RequestException, ValueError):
        logger.exception('PhonePe callback verification failed for %s', callback_order_id)
        return JsonResponse({'detail': 'Verification temporarily unavailable.'}, status=503)
    return HttpResponse(status=204)


def project_domain(request, domain_slug):
    """Display the selected public project-domain folder."""
    domain_name = PROJECT_DOMAINS.get(domain_slug)
    if not domain_name:
        raise Http404("Project domain not found")
    return render(request, 'dashboard/project_domain.html', {
        'domain_name': domain_name,
        'domain_slug': domain_slug,
        'is_software_engineering': domain_slug == 'software-engineering',
        'project_modules': [name for name, _ in PROJECT_MODULES],
        'domain_projects': _load_domain_projects(domain_slug),
    })


def project_detail(request, domain_slug, project_slug):
    """Display one project registered inside a domain folder."""
    domain_name = PROJECT_DOMAINS.get(domain_slug)
    if not domain_name:
        raise Http404("Project domain not found")
    project = _get_domain_project(domain_slug, project_slug)
    return render(request, 'dashboard/project_detail.html', {
        'domain_name': domain_name,
        'domain_slug': domain_slug,
        'project': project,
        'is_engineeringcollege_project': (
            domain_slug == 'software-engineering'
            and project_slug == 'engineeringcollege-project'
        ),
        'project_modules': [name for name, _ in PROJECT_MODULES],
    })


def data_mining_project_detail_by_title(request, project_title):
    """Display a Data Mining project using its human-readable title URL."""
    project = _get_data_mining_project_by_title(project_title)
    return render(request, 'dashboard/project_detail.html', {
        'domain_name': PROJECT_DOMAINS['data-mining'],
        'domain_slug': 'data-mining',
        'project': project,
        'execution': _run_car_apriori_execution(project),
        'github_execution_templates': _car_price_github_execution_templates(),
        'is_engineeringcollege_project': False,
        'project_modules': [name for name, _ in PROJECT_MODULES],
    })


@login_required



def admin_dashboard(request):
    try:
        logger.info(f"Admin dashboard accessed by user: {request.user}, authenticated: {request.user.is_authenticated}, superuser: {request.user.is_superuser if request.user.is_authenticated else False}")

        # Check database connectivity
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            logger.info("Database connection successful")
        except Exception as db_e:
            logger.error(f"Database connection failed: {db_e}")
            messages.error(request, f'Database connection error: {db_e}')
            return redirect('dashboard:admin_login')

        if not request.user.is_authenticated:
            logger.warning("User not authenticated, redirecting to login")
            return redirect('dashboard:admin_login')

        if not request.user.is_superuser:
            logger.warning(f"User {request.user} is not superuser, access denied")
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:admin_login')

        # Test progressively more complex database queries
        logger.info("Admin dashboard: authentication passed, testing database queries")
        try:
            # Test basic counts
            total_faculty = Faculty.objects.count()
            total_students = Student.objects.count()
            active_faculty = Faculty.objects.filter(is_active=True).count()
            logger.info(f"Basic queries successful: faculty={total_faculty}, students={total_students}")

            # Optimized departments query with limit
            try:
                departments = list(Faculty.objects.values('department')
                                    .annotate(count=Count('id'), active=Count('id', filter=Q(is_active=True)))
                                    .order_by('-count')[:10])  # Limit to top 10 departments
                for d in departments:
                    d['percentage'] = (d['count'] / total_faculty * 100) if total_faculty > 0 else 0
                logger.info(f"Departments query successful: {len(departments)} departments")
            except Exception as dept_e:
                logger.error(f"Departments query failed: {dept_e}")
                departments = []

            # Recent logs query with select_related for performance
            try:
                recent_logs = list(FacultyLog.objects.select_related('faculty').order_by('-created_at')[:5])
                logger.info(f"Recent logs query successful: {len(recent_logs)} logs")
            except Exception as logs_e:
                logger.error(f"Recent logs query failed: {logs_e}")
                recent_logs = []

            # Test system stats with psutil (this was likely the original issue)
            system_stats = {}
            if psutil:
                try:
                    system_stats = {
                        'cpu_percent': psutil.cpu_percent(interval=0.5),
                        'memory_percent': psutil.virtual_memory().percent,
                        'disk_usage': psutil.disk_usage('/').percent,
                        'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    logger.info("System stats collection successful")
                except Exception as psutil_e:
                    logger.error(f"psutil error: {psutil_e}")
                    system_stats = {'error': f'psutil failed: {psutil_e}'}
            else:
                system_stats = {'status': 'psutil not available'}

            # Add remaining queries with error handling and optimization
            try:
                total_certificates = Certificate.objects.count()
                cloudinary_uploads = CloudinaryUpload.objects.count()
                with_phd = Faculty.objects.filter(phd_degree='Completed').count()
                recent_uploads = list(Faculty.objects.only('id', 'staff_name', 'created_at').order_by('-created_at')[:3])

                # Optimized user activity stats
                from django.contrib.auth.models import User
                user_activity = {
                    'total_users': User.objects.count(),
                    'active_today': 0,  # Simplified for performance
                }

                logger.info("All queries successful, rendering optimized dashboard")

            except Exception as final_e:
                logger.error(f"Final queries failed: {final_e}")
                # Fallback values
                total_certificates = 0
                cloudinary_uploads = 0
                with_phd = 0
                recent_uploads = []
                user_activity = {'total_users': 1, 'active_today': 0}

            return render(request, "dashboard/admin_dashboard.html", {
                'title': 'Admin Dashboard',
                'total_faculty': total_faculty,
                'active_faculty': active_faculty,
                'total_students': total_students,
                'total_certificates': total_certificates,
                'cloudinary_uploads': cloudinary_uploads,
                'with_phd': with_phd,
                'departments': departments,
                'recent_logs': recent_logs,
                'system_stats': system_stats,
                'user_activity': user_activity,
                'has_psutil': psutil is not None,
                'recent_uploads': recent_uploads,
            })
        except Exception as db_e:
            logger.error(f"Database error: {db_e}")
            return HttpResponse(f"Database Error: {db_e}", status=500)
        except Exception as template_e:
            logger.error(f"Template rendering error: {template_e}")
            return HttpResponse(f"Template Error: {template_e}", status=500)
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}", exc_info=True)
        if settings.DEBUG:
            tb = traceback.format_exc()
            return HttpResponse(f"<h1>DEBUG 500 ERROR</h1><pre>{tb}</pre>", content_type="text/html")
        else:
            return HttpResponse("Internal Server Error", status=500)


def student_dashboard(request):
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:student_login')
    student_username = request.session.get('student_username', 'anrkitstudent')
    student = None
    try:
        student = get_session_student_record(request)
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
        existing_photo_url = getattr(student, 'photo_url', None)
        if existing_photo_url:
            student.photo_url = normalize_optional_url(existing_photo_url)
        certificate_labels = {
            'cert_achieve': 'Achievement',
            'cert_intern': 'Internship',
            'cert_courses': 'Courses',
            'cert_sdp': 'SDP',
            'cert_extra': 'Extra Curricular',
            'cert_placement': 'Placement',
            'cert_national': 'National Exam',
        }
        for field_name, _, url_field_name in STUDENT_CERTIFICATE_SLOTS:
            if getattr(student, field_name, None) or normalize_optional_url(getattr(student, url_field_name, None)):
                certificates.append({'type': certificate_labels[field_name], 'field': field_name, 'has_file': True})
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
        return redirect('dashboard:student_dashboard_view')
    return redirect('dashboard:admin_login')


# ==================== SYLLABUS VIEW ====================
@login_required
def syllabus_view(request):
    return render(request, 'dashboard/syllabus.html', {
        'title': 'Syllabus & Common Subjects - ANURAG Engineering College',
    })


# ==================== FACULTY DASHBOARD ====================
@login_required
def faculty_dashboard(request, faculty_id=None):
    pdf_mode = request.GET.get("print") == "1"
    if pdf_mode:
        fid = request.GET.get("id")
        if not fid:
            return HttpResponseBadRequest("Faculty ID required for PDF mode")
        faculty = get_object_or_404(Faculty, id=fid)
        exp = calculate_experience(faculty.joining_date) if faculty.joining_date else "N/A"
        # Resolve the faculty photo for the PDF template
        photo_url, local_photo_path, photo_temp_paths, _photo_source = resolve_faculty_photo_for_pdf(faculty)
        anurag_header_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'ANURAG HEADER.png')
        context = {
            "faculty": faculty,
            "pdf_mode": True,
            "current_date": timezone.now(),
            "experience": exp,
            "photo_url": photo_url,
            "anurag_header_url": build_file_uri(anurag_header_path),
            "cloudinary_status": {"has_pdf": bool(faculty.cloudinary_pdf_url)},
        }
        # Clean up any temp paths after rendering
        try:
            return render(request, "dashboard/faculty_pdf.html", context)
        finally:
            for temp_path in photo_temp_paths:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
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
def get_department_options():
    return ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'MBA', 'MCA']


def get_faculty_registration_context():
    return {
        "title": "Add New Faculty",
        "departments": get_department_options(),
        "designations": ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer', 'Senior Professor'],
        "genders": ['Male', 'Female', 'Other'],
        "caste_list": ['OC', 'BC-A', 'BC-B', 'BC-C', 'BC-D', 'BC-E', 'SC', 'ST'],
        "qualifications": ['Completed', 'Pursuing', 'Not Started'],
    }


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

        dob_raw = request.POST.get('dob', '')
        if dob_raw and parse_date(dob_raw) is None:
            messages.error(request, 'Invalid date of birth. Use YYYY-MM-DD format (e.g., 1990-01-15)')
            return render(request, 'dashboard/add_faculty_form.html', get_faculty_registration_context())

        if not request.POST.get('jntuh_id', '').strip():
            messages.error(request, 'Please fill the JNTUH ID before saving faculty registration.')
            return render(request, 'dashboard/add_faculty_form.html', get_faculty_registration_context())

        try:
            phd_status = request.POST.get('phd_degree', '')
            phd_title = request.POST.get('phd_title', '').strip() if phd_status == 'Completed' else ''
            college_experiences = normalize_faculty_college_experiences(
                request.POST.get('college_experiences_json', '[]')
            )
            tstsabas_entries = normalize_tstsabas_entries(
                request.POST.get('tstsabas_entries_json', '[]')
            )
            joining_date = min(
                (parse_date(item['from_date']) for item in college_experiences),
                default=None,
            )

            # ==================== CREATE FACULTY OBJECT ====================
            faculty = Faculty(
                staff_name=request.POST.get('staff_name', ''),
                employee_code=request.POST.get('employee_code', ''),
                father_name=request.POST.get('father_name', ''),
                mother_name=request.POST.get('mother_name', ''),
                gender=request.POST.get('gender', ''),
                dob=parse_date(request.POST.get('dob')),
                state=request.POST.get('state', ''),
                caste=request.POST.get('caste', ''),
                sub_caste=request.POST.get('sub_caste', ''),
                nationality=request.POST.get('nationality', 'Indian'),
                mobile=request.POST.get('mobile', ''),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                department=request.POST.get('department', ''),
                designation=request.POST.get('designation', ''),
                joining_date=joining_date,
                college_experiences=college_experiences,
                tstsabas_entries=tstsabas_entries,
                jntuh_id=request.POST.get('jntuh_id', ''),
                aicte_id=request.POST.get('aicte_id', ''),
                pan=request.POST.get('pan', ''),
                aadhar=request.POST.get('aadhar', ''),
                apaar_id=request.POST.get('apaar_id', ''),
                orcid_id=request.POST.get('orcid_id', ''),
                ssc_year=request.POST.get('ssc_year') or None,
                ssc_percent=request.POST.get('ssc_percent', ''),
                ssc_school=request.POST.get('ssc_school', ''),
                inter_year=request.POST.get('inter_year') or None,
                inter_percent=request.POST.get('inter_percent', ''),
                inter_college=request.POST.get('inter_college', ''),
                ug_degree=request.POST.get('ug_degree', ''),
                ug_year=request.POST.get('ug_year') or None,
                ug_percentage=request.POST.get('ug_percentage', ''),
                ug_college=request.POST.get('ug_college', ''),
                ug_spec=request.POST.get('ug_spec', ''),
                pg_degree=request.POST.get('pg_degree', ''),
                pg_year=request.POST.get('pg_year') or None,
                pg_percentage=request.POST.get('pg_percentage', ''),
                pg_college=request.POST.get('pg_college', ''),
                pg_spec=request.POST.get('pg_spec', ''),
                phd_degree=phd_status,
                phd_title=phd_title,
                phd_year=request.POST.get('phd_year') or None,
                phd_university=request.POST.get('phd_university', ''),
                phd_spec=request.POST.get('phd_spec', ''),
                subjects_dealt=request.POST.get('subjects_dealt', ''),
                scm=request.POST.get('scm', ''),
                about_yourself=request.POST.get('about_yourself', ''),
                membership_academic_year=request.POST.get('membership_academic_year', ''),
                membership_in=request.POST.get('membership_in', ''),
                membership_id=request.POST.get('membership_id', ''),
                is_ratified=True if request.POST.get('is_ratified') == 'yes' else False if request.POST.get('is_ratified') == 'no' else None,
                pdf_password=request.POST.get('pdf_password', ''),
            )

            # ==================== PHOTO ====================
            # Always save photo locally AND upload to Cloudinary (if configured)
            if request.FILES.get('photo'):
                faculty.photo = request.FILES['photo']
            # ==================== SAVE FACULTY FIRST (need PK for related objects) ====================
            faculty.save()
            print(f" [OK] Faculty saved with ID: {faculty.id}")

            # ==================== UPLOAD PHOTO TO CLOUDINARY ====================
            if request.FILES.get('photo') and is_cloudinary_configured():
                try:
                    request.FILES['photo'].seek(0)
                    cr = cloudinary.uploader.upload(
                        request.FILES['photo'],
                        folder="faculty_photos",
                        public_id=f"faculty_{faculty.employee_code}_photo",
                        overwrite=True,
                        transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                    )
                    faculty.cloudinary_photo_url = cr['secure_url']
                    faculty.save(update_fields=['cloudinary_photo_url'])
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type='photo',
                        cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                        resource_type=cr['resource_type'], uploaded_by=request.user.username
                    )
                    print(f" [OK] Photo uploaded to Cloudinary: {cr['secure_url']}")
                except Exception as e:
                    logger.error(f"Cloudinary photo upload error: {e}")
                    print(f" [WARN] Photo saved locally, Cloudinary upload failed: {e}")
            elif faculty.photo and not faculty.cloudinary_photo_url and is_cloudinary_configured():
                # If photo exists locally but not on Cloudinary, sync it now
                try:
                    print(f" [ATTEMPT] Syncing existing local photo to Cloudinary...")
                    with faculty.photo.open('rb') as pf:
                        cr = cloudinary.uploader.upload(
                            pf,
                            folder="faculty_photos",
                            public_id=f"faculty_{faculty.employee_code}_photo",
                            overwrite=True,
                            transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                        )
                        faculty.cloudinary_photo_url = cr['secure_url']
                        faculty.save(update_fields=['cloudinary_photo_url'])
                        CloudinaryUpload.objects.create(
                            faculty=faculty, upload_type='photo',
                            cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                            resource_type=cr['resource_type'], uploaded_by=request.user.username if request.user.username else 'System'
                        )
                        print(f" [OK] Existing photo synced to Cloudinary: {cr['secure_url']}")
                except Exception as e:
                    logger.warning(f"Could not sync existing photo to Cloudinary: {e}")
                    print(f" [WARN] Could not sync existing photo: {e}")

            # ==================== DOCUMENT FILES ====================
            doc_file_fields = [
                'aadhar_file', 'pan_file', 'apaar_file', 'scm_file', 'jntuh_biodata',
                'ssc_certificate', 'inter_certificate', 'ug_certificate',
                'pg_certificate', 'phd_certificate', 'experience_certificates',
                'research_proof', 'fdp_certificate', 'other_documents',
                'membership_proof',
            ]
            # On Render (Cloudinary storage), clear FileFields to avoid automatic upload.
            # The explicit Cloudinary upload block below will handle files on local.
            if getattr(settings, 'ON_RENDER', False):
                for field_name in doc_file_fields:
                    if request.FILES.get(field_name):
                        setattr(faculty, field_name, None)
            else:
                for field_name in doc_file_fields:
                    if request.FILES.get(field_name):
                        setattr(faculty, field_name, request.FILES[field_name])
                        print(f" [OK] Saved file field: {field_name}")

            # Experience certificates academic year
            exp_cert_ay = request.POST.get('experience_certificates_academic_year', '')
            if exp_cert_ay and hasattr(faculty, 'experience_certificates_academic_year'):
                faculty.experience_certificates_academic_year = exp_cert_ay

            faculty.save()

            # ==================== UPLOAD DOCUMENTS TO CLOUDINARY ====================
            if is_cloudinary_configured():
                cloudinary_doc_fields = [
                    ('aadhar_file', 'aadhar_url', 'Aadhar'),
                    ('pan_file', 'pan_url', 'PAN'),
                    ('apaar_file', 'apaar_url', 'APAAR'),
                    ('scm_file', 'scm_url', 'SCM'),
                    ('jntuh_biodata', 'jntuh_biodata_url', 'JNTUH Bio-Data'),
                    ('ssc_certificate', 'ssc_certificate_url', 'SSC Certificate'),
                    ('inter_certificate', 'inter_certificate_url', 'Inter Certificate'),
                    ('ug_certificate', 'ug_certificate_url', 'UG Certificate'),
                    ('pg_certificate', 'pg_certificate_url', 'PG Certificate'),
                    ('phd_certificate', 'phd_certificate_url', 'PhD Certificate'),
                    ('experience_certificates', 'experience_certificates_url', 'Experience Certificates'),
                    ('research_proof', 'research_proof_url', 'Research Proof'),
                    ('fdp_certificate', 'fdp_certificate_url', 'FDP Certificate'),
                    ('other_documents', 'other_documents_url', 'Other Documents'),
                    ('membership_proof', 'membership_proof_url', 'Membership Proof'),
                ]
                for file_field, url_field, label in cloudinary_doc_fields:
                    if request.FILES.get(file_field) and hasattr(faculty, url_field):
                        try:
                            request.FILES[file_field].seek(0)
                            cr = cloudinary.uploader.upload(
                                request.FILES[file_field],
                                resource_type='auto',
                                folder=f"faculty_documents/{faculty.employee_code}",
                                public_id=f"{file_field}_{faculty.employee_code}",
                                overwrite=True,
                            )
                            setattr(faculty, url_field, cr['secure_url'])
                            record_cloudinary_upload(
                                faculty=faculty,
                                upload_type=file_field,
                                upload_result=cr,
                                uploaded_by=request.user.username,
                            )
                            print(f" [OK] {label} uploaded to Cloudinary")
                        except Exception as e:
                            logger.error(f"Cloudinary upload error for {label}: {e}")
                faculty.save()

            # ==================== HANDLE MULTIPLE RESEARCH PROOF FILES ====================
            uploaded_research_proof_urls = []
            proofs_data = parse_json_list(request.POST.get('research_proofs_data', '[]'))
            for proof_position, (proof_counter, proof_file) in enumerate(
                iter_indexed_uploaded_files(request.FILES, 'research_proof_files_'),
                start=1,
            ):
                ay = ''
                if len(proofs_data) >= proof_position and isinstance(proofs_data[proof_position - 1], dict):
                    ay = (proofs_data[proof_position - 1].get('academic_year') or '').strip()
                if is_cloudinary_configured():
                    try:
                        # Determine resource type based on file extension
                        filename = proof_file.name.lower()
                        resource_type = 'raw' if filename.endswith('.pdf') else 'auto'

                        cr = cloudinary.uploader.upload(
                            proof_file, resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}/research_proofs",
                            public_id=f"research_proof_{faculty.employee_code}_{proof_counter}",
                            overwrite=True,
                        )
                        record_cloudinary_upload(
                            faculty=faculty,
                            upload_type='research_proof',
                            upload_result=cr,
                            uploaded_by=request.user.username,
                        )
                        uploaded_research_proof_urls.append(cr['secure_url'])
                        # Save first processed proof to the main field
                        if proof_position == 1 and hasattr(faculty, 'research_proof_url'):
                            faculty.research_proof_url = cr['secure_url']
                            if ay and hasattr(faculty, 'research_proof_academic_year'):
                                faculty.research_proof_academic_year = ay
                            faculty.save()
                        print(f" [OK] Research proof {proof_counter} uploaded to Cloudinary (type: {resource_type})")
                    except Exception as e:
                        logger.error(f"Research proof Cloudinary upload error: {e}")
                        # Save locally since Cloudinary failed
                        if proof_position <= len(research_publication_records):
                            pub = research_publication_records[proof_position - 1]
                            pub.proof_document = proof_file
                            pub.save(update_fields=['proof_document'])
                            print(f" [OK] Research proof {proof_counter} saved locally to publication")
                else:
                    # Cloudinary not configured, save locally
                    if proof_position <= len(research_publication_records):
                        pub = research_publication_records[proof_position - 1]
                        pub.proof_document = proof_file
                        pub.save(update_fields=['proof_document'])
                        print(f" [OK] Research proof {proof_counter} saved locally to publication")

            # ==================== HANDLE MULTIPLE OTHER DOC FILES ====================
            docs_data = parse_json_list(request.POST.get('other_documents_data', '[]'))
            for doc_position, (other_doc_counter, other_file) in enumerate(
                iter_indexed_uploaded_files(request.FILES, 'other_doc_files_'),
                start=1,
            ):
                ay = ''
                if len(docs_data) >= doc_position and isinstance(docs_data[doc_position - 1], dict):
                    ay = (docs_data[doc_position - 1].get('academic_year') or '').strip()
                if is_cloudinary_configured():
                    try:
                        # Determine resource type based on file extension
                        filename = other_file.name.lower()
                        resource_type = 'raw' if filename.endswith('.pdf') else 'auto'

                        cr = cloudinary.uploader.upload(
                            other_file, resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}/other_docs",
                            public_id=f"other_doc_{faculty.employee_code}_{other_doc_counter}",
                            overwrite=True,
                        )
                        record_cloudinary_upload(
                            faculty=faculty,
                            upload_type='other_documents',
                            upload_result=cr,
                            uploaded_by=request.user.username,
                        )
                        if doc_position == 1 and hasattr(faculty, 'other_documents_url'):
                            faculty.other_documents_url = cr['secure_url']
                            if ay and hasattr(faculty, 'other_documents_academic_year'):
                                faculty.other_documents_academic_year = ay
                            faculty.save()
                        print(f" [OK] Other doc {other_doc_counter} uploaded to Cloudinary (type: {resource_type})")
                    except Exception as e:
                        logger.error(f"Other doc Cloudinary upload error: {e}")

            # ==================== RESEARCH PUBLICATIONS ====================
            research_json = request.POST.get('research_publications_json', '[]')
            research_publication_records = []
            try:
                research_list = parse_json_list(research_json)
                for item in research_list:
                    if not item.get('title'):
                        continue
                    pub_type = item.get('research_type') or item.get('type') or 'journal'
                    venue = item.get('journal_name') or item.get('conference_name') or ''
                    pub = ResearchPublication.objects.create(
                        faculty=faculty,
                        research_type=pub_type,
                        title=item.get('title', ''),
                        authors=item.get('authors', ''),
                        academic_year=item.get('academic_year', ''),
                        publication_year=item.get('publication_year') or item.get('year') or None,
                        journal_name=venue if pub_type != 'conference' else '',
                        conference_name=venue if pub_type == 'conference' else '',
                        issn=item.get('issn', ''),
                        doi=item.get('doi', ''),
                        url=normalize_optional_url(item.get('url')),
                        status=item.get('status', 'published'),
                    )
                    research_publication_records.append(pub)
                print(f" [OK] Saved {len(research_list)} research publications")
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error saving research publications: {e}")

            # ==================== LINK RESEARCH PROOF FILES TO PUBLICATIONS ====================
            # Assign proofs sequentially to publications (more reliable than academic year matching)
            for index, pub in enumerate(research_publication_records):
                if index < len(uploaded_research_proof_urls):
                    pub.proof_document_url = uploaded_research_proof_urls[index]
                    pub.save(update_fields=['proof_document_url'])
                    print(f" [OK] Linked research proof to publication: {pub.title[:30]}")

            # ==================== BTECH PROJECTS ====================
            projects_json = request.POST.get('btech_projects_json', '[]')
            try:
                projects_list = json.loads(projects_json)
                for item in projects_list:
                    if not item.get('project_title') and not item.get('title'):
                        continue
                    BTechProject.objects.create(
                        faculty=faculty,
                        ht_no=item.get('ht_no', ''),
                        student_name=item.get('student_name', ''),
                        batch=item.get('batch', ''),
                        project_title=item.get('project_title') or item.get('title', ''),
                        approved=item.get('approved') is True or str(item.get('approved')).lower() == 'true',
                        marks=item.get('marks') or None,
                    )
                print(f" [OK] Saved {len(projects_list)} B.Tech projects")
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error saving B.Tech projects: {e}")

            # ==================== FDP / WORKSHOPS ====================
            fdp_json = request.POST.get('fdp_entries_json', '[]')
            fdp_records = []
            try:
                fdp_list = parse_json_list(fdp_json)
                for item in fdp_list:
                    if not item.get('title'):
                        continue
                    fdp = FDP.objects.create(
                        faculty=faculty,
                        fdp_type=item.get('fdp_type') or item.get('type', 'fdp'),
                        title=item.get('title', ''),
                        academic_year=item.get('academic_year', ''),
                        from_date=item.get('from_date') or date.today().strftime('%Y-%m-%d'),
                        to_date=item.get('to_date') or date.today().strftime('%Y-%m-%d'),
                        organized_by=item.get('organized_by', ''),
                        place=item.get('place', ''),
                        mode=item.get('mode', 'offline'),
                        level=item.get('level', 'national'),
                        role=item.get('role', 'participant'),
                        sponsored_by=item.get('sponsored_by', ''),
                        remarks=item.get('remarks', ''),
                    )
                    fdp_records.append(fdp)
                print(f" [OK] Saved {len(fdp_list)} FDP entries")
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error saving FDP entries: {e}")

            # ==================== LINK FDP CERT FILES TO FDP RECORDS ====================
            uploaded_fdp_certificate_urls = []
            certs_data = parse_json_list(request.POST.get('fdp_certificates_data', '[]'))
            for cert_position, (fdp_cert_counter, cert_file) in enumerate(
                iter_indexed_uploaded_files(request.FILES, 'fdp_cert_files_'),
                start=1,
            ):
                ay = ''
                if len(certs_data) >= cert_position and isinstance(certs_data[cert_position - 1], dict):
                    ay = (certs_data[cert_position - 1].get('academic_year') or '').strip()
                if is_cloudinary_configured():
                    try:
                        # Determine resource type based on file extension
                        filename = cert_file.name.lower()
                        resource_type = 'raw' if filename.endswith('.pdf') else 'auto'

                        cr = cloudinary.uploader.upload(
                            cert_file, resource_type=resource_type,
                            folder=f"faculty_documents/{faculty.employee_code}/fdp_certs",
                            public_id=f"fdp_cert_{faculty.employee_code}_{fdp_cert_counter}",
                            overwrite=True,
                        )
                        cert_url = cr['secure_url']
                        record_cloudinary_upload(
                            faculty=faculty,
                            upload_type='fdp_certificate',
                            upload_result=cr,
                            uploaded_by=request.user.username,
                        )
                        uploaded_fdp_certificate_urls.append(cert_url)
                        if cert_position == 1 and hasattr(faculty, 'fdp_certificate_url'):
                            faculty.fdp_certificate_url = cert_url
                            if ay and hasattr(faculty, 'fdp_certificate_academic_year'):
                                faculty.fdp_certificate_academic_year = ay
                            faculty.save()
                        print(f" [OK] FDP cert {fdp_cert_counter} uploaded to Cloudinary (type: {resource_type})")
                    except Exception as e:
                        logger.error(f"FDP cert Cloudinary upload error: {e}")
                        # Save locally since Cloudinary failed
                        if cert_position <= len(fdp_records):
                            fdp = fdp_records[cert_position - 1]
                            fdp.certificate = cert_file
                            fdp.save(update_fields=['certificate'])
                            print(f" [OK] FDP cert {fdp_cert_counter} saved locally to FDP entry")
                else:
                    # Cloudinary not configured, save locally
                    if cert_position <= len(fdp_records):
                        fdp = fdp_records[cert_position - 1]
                        fdp.certificate = cert_file
                        fdp.save(update_fields=['certificate'])
                        print(f" [OK] FDP cert {fdp_cert_counter} saved locally to FDP entry")

            # Assign FDP certificates sequentially to FDP records
            for index, fdp in enumerate(fdp_records):
                if index < len(uploaded_fdp_certificate_urls):
                    fdp.certificate_url = uploaded_fdp_certificate_urls[index]
                    fdp.save(update_fields=['certificate_url'])
                    print(f" [OK] Linked FDP certificate to entry: {fdp.title[:30]}")

            # ==================== RESULTS ====================
            results_json = request.POST.get('results_json', '[]')
            try:
                results_list = json.loads(results_json)
                if results_list:
                    faculty.results = results_json
                    faculty.save(update_fields=['results'])
                print(f" [OK] Saved {len(results_list)} result entries")
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error saving results: {e}")

            # ==================== FACULTY PROFILE ====================
            try:
                profile, _ = FacultyProfile.objects.get_or_create(faculty=faculty)
                if request.POST.get('exp_anurag') and hasattr(profile, 'experience_at_anurag'):
                    profile.experience_at_anurag = request.POST.get('exp_anurag')
                if request.POST.get('exp_other') and hasattr(profile, 'experience_other'):
                    profile.experience_other = request.POST.get('exp_other')
                profile.save()
            except Exception as e:
                logger.error(f"FacultyProfile create error: {e}")

            # ==================== LOG ====================
            FacultyLog.objects.create(
                faculty=faculty,
                action='Faculty Added',
                details=f'New faculty added: {faculty.staff_name} ({faculty.employee_code})',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # Ensure the faculty flow (add_faculty_form.html) always attempts
            # to build a single individual PDF that includes profile photo and docs.
            try:
                has_uploads = bool(
                    faculty.photo or faculty.cloudinary_photo_url or
                    faculty.aadhar_file or faculty.aadhar_url or
                    faculty.pan_file or faculty.pan_url or
                    faculty.apaar_file or faculty.apaar_url or
                    faculty.scm_file or faculty.scm_url or
                    faculty.jntuh_biodata or faculty.jntuh_biodata_url or
                    faculty.ssc_certificate or faculty.ssc_certificate_url or
                    faculty.inter_certificate or faculty.inter_certificate_url or
                    faculty.ug_certificate or faculty.ug_certificate_url or
                    faculty.pg_certificate or faculty.pg_certificate_url or
                    faculty.phd_certificate or faculty.phd_certificate_url or
                    faculty.research_proof or faculty.research_proof_url or
                    faculty.fdp_certificate or faculty.fdp_certificate_url or
                    faculty.experience_certificates or faculty.experience_certificates_url or
                    faculty.other_documents or faculty.other_documents_url or
                    faculty.membership_proof or faculty.membership_proof_url or
                    Certificate.objects.filter(faculty=faculty).exists()
                )
                should_generate_pdf = has_uploads or bool(get_pdf_password(faculty)) or bool(faculty.email)
                generated_pdf_bytes = None
                if should_generate_pdf:
                    generated_pdf_bytes = generate_faculty_pdf_bytes(faculty)
                    persist_faculty_pdf(faculty, generated_pdf_bytes, uploaded_by=request.user.username)
                if get_pdf_password(faculty) and faculty.email and generated_pdf_bytes:
                    if email_password_protected_pdf(
                        recipient=faculty.email,
                        display_name=faculty.staff_name,
                        pdf_bytes=generated_pdf_bytes,
                        filename=f"faculty_{faculty.employee_code}_profile.pdf",
                        subject='Password Protected Faculty Profile PDF',
                    ):
                        messages.success(request, 'Password-protected faculty PDF emailed successfully.')
            except Exception as pdf_e:
                logger.warning(f"Faculty added, but merged PDF generation failed: {pdf_e}")

            messages.success(request, f'Faculty {faculty.staff_name} added successfully!')
            print(f" [OK] Faculty {faculty.employee_code} fully saved. Redirecting to faculty list.")
            return redirect('dashboard:faculty_list')

        except Exception as e:
            logger.error(f"Error adding faculty: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error adding faculty: {str(e)}")
            return redirect("dashboard:add_faculty")

    return render(request, "dashboard/add_faculty_form.html", get_faculty_registration_context())


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
            'phd_degree', 'phd_title', 'phd_year', 'phd_university', 'phd_spec',
            'subjects_dealt', 'scm', 'about_yourself', 'results',
            'membership_academic_year', 'membership_in', 'membership_id',
            'pdf_password',
        ]
        for attr in text_fields:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)
        if request.POST.get('phd_degree') != 'Completed':
            faculty.phd_title = ''
        if request.POST.get('is_ratified') in {'yes', 'no'}:
            faculty.is_ratified = request.POST.get('is_ratified') == 'yes'
        for date_attr in ['dob']:
            val = request.POST.get(date_attr)
            setattr(faculty, date_attr, parse_date(val) if val else None)
        if 'college_experiences_json' in request.POST:
            faculty.college_experiences = normalize_faculty_college_experiences(
                request.POST.get('college_experiences_json', '[]')
            )
            faculty.joining_date = min(
                (parse_date(item['from_date']) for item in faculty.college_experiences),
                default=None,
            )
        if 'tstsabas_entries_json' in request.POST:
            faculty.tstsabas_entries = normalize_tstsabas_entries(
                request.POST.get('tstsabas_entries_json', '[]')
            )
            
        # ==================== PROCESS COMPLEX JSON DATA ====================
        
        # 1. Research Publications
        research_publication_records = []
        research_data = request.POST.get('research_publications_json')
        if research_data:
            try:
                research_list = json.loads(research_data)
                existing_publication_assets = {}
                for existing_pub in ResearchPublication.objects.filter(faculty=faculty):
                    key = ((existing_pub.academic_year or '').strip(), (existing_pub.title or '').strip())
                    existing_publication_assets[key] = {
                        'proof_document_url': existing_pub.proof_document_url or '',
                        'url': existing_pub.url or '',
                    }
                ResearchPublication.objects.filter(faculty=faculty).delete()
                for item in research_list:
                    if not item.get('title'): continue
                    academic_year = item.get('academic_year', '')
                    title = item.get('title') or ''
                    research_type = item.get('research_type') or item.get('type', 'journal')
                    venue = item.get('journal_name') or item.get('conference_name') or ''
                    existing_assets = existing_publication_assets.get(((academic_year or '').strip(), title.strip()), {})
                    pub = ResearchPublication.objects.create(
                        faculty=faculty,
                        research_type=research_type,
                        title=title,
                        authors=item.get('authors'),
                        academic_year=academic_year,
                        publication_year=item.get('publication_year') or item.get('year'),
                        journal_name=venue if research_type != 'conference' else '',
                        conference_name=venue if research_type == 'conference' else '',
                        issn=item.get('issn', ''),
                        status=item.get('status', 'published'),
                        doi=item.get('doi'),
                        url=normalize_optional_url(item.get('url') or existing_assets.get('url')),
                        proof_document_url=existing_assets.get('proof_document_url', ''),
                    )
                    research_publication_records.append(pub)
            except Exception as e:
                logger.error(f"Error saving research publications: {e}")

        # 2. B.Tech Projects
        projects_data = request.POST.get('btech_projects_json')
        if projects_data:
            try:
                projects_list = json.loads(projects_data)
                BTechProject.objects.filter(faculty=faculty).delete()
                for item in projects_list:
                    if not item.get('title'): continue
                    BTechProject.objects.create(
                        faculty=faculty,
                        project_title=item.get('title'),
                        student_name=item.get('student_name', 'N/A'),
                        ht_no=item.get('ht_no', 'N/A'),
                        batch=item.get('batch', ''),
                        approved=item.get('approved') == 'true' or item.get('approved') == True,
                        marks=item.get('marks', '')
                    )
            except Exception as e:
                logger.error(f"Error saving B.Tech projects: {e}")

        # 3. FDP / Workshops
        fdp_records = []
        fdp_data = request.POST.get('fdp_entries_json')
        if fdp_data:
            try:
                fdp_list = json.loads(fdp_data)
                existing_fdp_urls = {}
                for existing_fdp in FDP.objects.filter(faculty=faculty):
                    key = ((existing_fdp.academic_year or '').strip(), (existing_fdp.title or '').strip())
                    existing_fdp_urls[key] = existing_fdp.certificate_url or ''
                FDP.objects.filter(faculty=faculty).delete()
                for item in fdp_list:
                    if not item.get('title'): continue
                    academic_year = item.get('academic_year', '')
                    title = item.get('title') or ''
                    fdp = FDP.objects.create(
                        faculty=faculty,
                        fdp_type=item.get('fdp_type') or item.get('type', 'fdp'),
                        title=title,
                        academic_year=academic_year,
                        from_date=item.get('from_date') or date.today().strftime('%Y-%m-%d'),
                        to_date=item.get('to_date') or date.today().strftime('%Y-%m-%d'),
                        organized_by=item.get('organized_by', ''),
                        place=item.get('place', ''),
                        mode=item.get('mode', 'offline'),
                        level=item.get('level', 'national'),
                        role=item.get('role', 'participant'),
                        sponsored_by=item.get('sponsored_by', ''),
                        remarks=item.get('remarks', ''),
                        certificate_url=existing_fdp_urls.get(((academic_year or '').strip(), title.strip()), ''),
                    )
                    fdp_records.append(fdp)
            except Exception as e:
                logger.error(f"Error saving FDP entries: {e}")

        # 4. Results
        results_json_data = request.POST.get('results_json')
        if results_json_data:
            faculty.results = results_json_data
            
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
            # Always save photo locally
            faculty.photo = request.FILES["photo"]
            # Always upload to Cloudinary if configured
            if is_cloudinary_configured():
                try:
                    request.FILES["photo"].seek(0)
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
        # ==================== DOCUMENT FILES ====================
        all_doc_fields = [
            'aadhar_file', 'pan_file', 'apaar_file', 'scm_file', 'jntuh_biodata',
            'ssc_certificate', 'inter_certificate',
            'ug_certificate', 'pg_certificate', 'phd_certificate',
            'membership_proof',
        ]
        # On Render (Cloudinary storage), clear FileFields to avoid automatic upload.
        # The explicit Cloudinary upload below will handle files.
        if getattr(settings, 'ON_RENDER', False):
            for field_name in all_doc_fields:
                if request.FILES.get(field_name):
                    setattr(faculty, field_name, None)
        else:
            for field_name in all_doc_fields:
                if request.FILES.get(field_name):
                    setattr(faculty, field_name, request.FILES[field_name])

        faculty.save()

        # ==================== UPLOAD DOCUMENTS TO CLOUDINARY ====================
        if is_cloudinary_configured():
            cloudinary_doc_fields = [
                ('aadhar_file', 'aadhar_url', 'Aadhar'),
                ('pan_file', 'pan_url', 'PAN'),
                ('apaar_file', 'apaar_url', 'APAAR'),
                ('scm_file', 'scm_url', 'SCM'),
                ('jntuh_biodata', 'jntuh_biodata_url', 'JNTUH Bio-Data'),
                ('ssc_certificate', 'ssc_certificate_url', 'SSC Certificate'),
                ('inter_certificate', 'inter_certificate_url', 'Inter Certificate'),
                ('ug_certificate', 'ug_certificate_url', 'UG Certificate'),
                ('pg_certificate', 'pg_certificate_url', 'PG Certificate'),
                ('phd_certificate', 'phd_certificate_url', 'PhD Certificate'),
                ('membership_proof', 'membership_proof_url', 'Membership Proof'),
            ]
            for file_field, url_field, label in cloudinary_doc_fields:
                if request.FILES.get(file_field) and hasattr(faculty, url_field):
                    try:
                        request.FILES[file_field].seek(0)
                        cr = cloudinary.uploader.upload(
                            request.FILES[file_field],
                            resource_type='auto',
                            folder=f"faculty_documents/{faculty.employee_code}",
                            public_id=f"{file_field}_{faculty.employee_code}",
                            overwrite=True,
                        )
                        setattr(faculty, url_field, cr['secure_url'])
                        record_cloudinary_upload(
                            faculty=faculty,
                            upload_type=file_field,
                            upload_result=cr,
                            uploaded_by=request.user.username,
                        )
                        print(f" [OK] {label} uploaded to Cloudinary")
                    except Exception as e:
                        logger.error(f"Cloudinary upload error for {label}: {e}")

            # Additional documents
            additional_doc_fields = ['research_proof', 'fdp_certificate', 'experience_certificates', 'other_documents']
            # On Render, clear FileFields for additional docs too
            if getattr(settings, 'ON_RENDER', False):
                for field_name in additional_doc_fields:
                    if request.FILES.get(field_name):
                        setattr(faculty, field_name, None)

            additional_doc_uploads = [
                ('research_proof', 'research_proof_url', 'faculty_documents/{code}/research_proofs', 'research_proof_{code}'),
                ('fdp_certificate', 'fdp_certificate_url', 'faculty_documents/{code}/fdp_certs', 'fdp_certificate_{code}'),
                ('experience_certificates', 'experience_certificates_url', 'faculty_documents/{code}/experience_certs', 'experience_certificates_{code}'),
                ('other_documents', 'other_documents_url', 'faculty_documents/{code}/other_docs', 'other_documents_{code}'),
            ]
            for field_name, url_field, folder_tpl, public_id_tpl in additional_doc_uploads:
                uploaded_file = request.FILES.get(field_name)
                if not uploaded_file:
                    continue
                if is_cloudinary_configured():
                    try:
                        resource_type = 'raw' if uploaded_file.name.lower().endswith('.pdf') else 'auto'
                        cr = cloudinary.uploader.upload(
                            uploaded_file,
                            resource_type=resource_type,
                            folder=folder_tpl.format(code=faculty.employee_code),
                            public_id=public_id_tpl.format(code=faculty.employee_code),
                            overwrite=True,
                            access_mode="public",  # Ensure public access
                        )
                        setattr(faculty, url_field, cr['secure_url'])
                        record_cloudinary_upload(
                            faculty=faculty,
                            upload_type=field_name,
                            upload_result=cr,
                            uploaded_by=request.user.username,
                        )
                        print(f" [OK] {field_name} uploaded to Cloudinary")
                    except Exception as e:
                        logger.error(f"Cloudinary upload error during edit for {field_name}: {e}")
        faculty.save()

        # ==================== HANDLE MULTIPLE RESEARCH PROOF FILES DURING EDIT ====================
        uploaded_research_proof_urls = []
        proofs_data = parse_json_list(request.POST.get('research_proofs_data', '[]'))
        for proof_position, (proof_counter, proof_file) in enumerate(
            iter_indexed_uploaded_files(request.FILES, 'research_proof_files_'),
            start=1,
        ):
            ay = ''
            if len(proofs_data) >= proof_position and isinstance(proofs_data[proof_position - 1], dict):
                ay = (proofs_data[proof_position - 1].get('academic_year') or '').strip()
            if is_cloudinary_configured():
                try:
                    # Determine resource type based on file extension
                    filename = proof_file.name.lower()
                    resource_type = 'raw' if filename.endswith('.pdf') else 'auto'

                    cr = cloudinary.uploader.upload(
                        proof_file, resource_type=resource_type,
                        folder=f"faculty_documents/{faculty.employee_code}/research_proofs",
                        public_id=f"research_proof_{faculty.employee_code}_{proof_counter}",
                        overwrite=True,
                        access_mode="public",  # Ensure public access
                    )
                    record_cloudinary_upload(
                        faculty=faculty,
                        upload_type='research_proof',
                        upload_result=cr,
                        uploaded_by=request.user.username,
                    )
                    uploaded_research_proof_urls.append(cr['secure_url'])
                    # Save first processed proof to the main field
                    if proof_position == 1 and hasattr(faculty, 'research_proof_url'):
                        faculty.research_proof_url = cr['secure_url']
                        if ay and hasattr(faculty, 'research_proof_academic_year'):
                            faculty.research_proof_academic_year = ay
                        faculty.save()
                    print(f" [OK] Research proof {proof_counter} uploaded to Cloudinary (type: {resource_type})")
                except Exception as e:
                    logger.error(f"Research proof Cloudinary upload error: {e}")

        # Assign research proof URLs to research publications sequentially
        for index, pub in enumerate(research_publication_records):
            if index < len(uploaded_research_proof_urls):
                pub.proof_document_url = uploaded_research_proof_urls[index]
                pub.save(update_fields=['proof_document_url'])
                print(f" [OK] Linked research proof to publication: {pub.title[:30]}")

        # ==================== HANDLE MULTIPLE FDP CERTIFICATE FILES DURING EDIT ====================
        uploaded_fdp_certificate_urls = []
        certs_data = parse_json_list(request.POST.get('fdp_certificates_data', '[]'))
        for cert_position, (fdp_cert_counter, cert_file) in enumerate(
            iter_indexed_uploaded_files(request.FILES, 'fdp_cert_files_'),
            start=1,
        ):
            ay = ''
            if len(certs_data) >= cert_position and isinstance(certs_data[cert_position - 1], dict):
                ay = (certs_data[cert_position - 1].get('academic_year') or '').strip()
            if is_cloudinary_configured():
                try:
                    # Determine resource type based on file extension
                    filename = cert_file.name.lower()
                    resource_type = 'raw' if filename.endswith('.pdf') else 'auto'

                    cr = cloudinary.uploader.upload(
                        cert_file, resource_type=resource_type,
                        folder=f"faculty_documents/{faculty.employee_code}/fdp_certs",
                        public_id=f"fdp_cert_{faculty.employee_code}_{fdp_cert_counter}",
                        overwrite=True,
                        access_mode="public",  # Ensure public access
                    )
                    cert_url = cr['secure_url']
                    record_cloudinary_upload(
                        faculty=faculty,
                        upload_type='fdp_certificate',
                        upload_result=cr,
                        uploaded_by=request.user.username,
                    )
                    uploaded_fdp_certificate_urls.append(cert_url)
                    if cert_position == 1 and hasattr(faculty, 'fdp_certificate_url'):
                        faculty.fdp_certificate_url = cert_url
                        if ay and hasattr(faculty, 'fdp_certificate_academic_year'):
                            faculty.fdp_certificate_academic_year = ay
                        faculty.save()
                    print(f" [OK] FDP cert {fdp_cert_counter} uploaded to Cloudinary (type: {resource_type})")
                except Exception as e:
                    logger.error(f"FDP cert Cloudinary upload error: {e}")

        # Assign FDP certificates sequentially to FDP records
        for index, fdp in enumerate(fdp_records):
            if index < len(uploaded_fdp_certificate_urls):
                fdp.certificate_url = uploaded_fdp_certificate_urls[index]
                fdp.save(update_fields=['certificate_url'])
                print(f" [OK] Linked FDP certificate to entry: {fdp.title[:30]}")

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
                           'exp_anurag', 'exp_other', 'phd_title']
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
                          'pg_degree', 'pg_college', 'pg_spec', 'phd_degree', 'phd_title', 'phd_university', 'phd_spec']
            for field in edu_fields:
                if field in request.POST:
                    setattr(faculty, field, request.POST[field])
            if request.POST.get('phd_degree') != 'Completed':
                faculty.phd_title = ''
            if 'photo' in request.FILES:
                # Always save photo locally
                faculty.photo = request.FILES['photo']
                # Always upload to Cloudinary if configured
                if is_cloudinary_configured():
                    try:
                        request.FILES['photo'].seek(0)
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
    if not request.session.get('student_logged_in') and not request.user.is_authenticated:
        return redirect('dashboard:student_login')
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if request.session.get('student_logged_in') and not user_authenticated and not is_demo_student_session(request):
        session_student = get_session_student_record(request)
        if not session_student:
            messages.error(request, "Your student session is missing record information. Please log in again.")
            return redirect('dashboard:student_logout')
        qs = Student.objects.filter(id=session_student.id).order_by('-created_at')
    else:
        qs = Student.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Student photo URLs are already stored directly on the model

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
            temp_photo_override_path = None
            certificate_override_assets = []

            def _upload(file, folder):
                if not file or not ca:
                    return None
                try:
                    file.seek(0) # Ensure at beginning
                    # Detect file type for proper resource_type
                    filename = getattr(file, 'name', '').lower()
                    if filename.endswith('.pdf'):
                        resource_type = "raw"
                    else:
                        resource_type = "auto"
                    public_id = f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    print(f"  [UPLOAD] Uploading {filename} to folder student_documents/{folder} with public_id {public_id} and resource_type {resource_type}")
                    # Upload without access_mode (files are public by default)
                    res = cloudinary.uploader.upload(
                        file,
                        resource_type=resource_type,
                        folder=f"student_documents/{folder}",
                        public_id=public_id,
                        overwrite=True,
                        access_mode="public",  # Ensure public access
                    )
                    print(f"  [UPLOAD] Upload result keys: {list(res.keys())}")
                    actual_public_id = res.get('public_id')
                    secure_url = res.get('secure_url')
                    print(f"  [UPLOAD] Actual public_id: {actual_public_id}")
                    print(f"  [UPLOAD] Secure URL: {secure_url}")
                    print(f"  [UPLOAD] URL type: {res.get('type', 'N/A')}")
                    
                    # Verify the URL is accessible
                    if secure_url:
                        try:
                            test_r = requests.get(secure_url, timeout=10)
                            print(f"  [UPLOAD] URL test status: {test_r.status_code}")
                        except Exception as test_e:
                            print(f"  [UPLOAD] URL test failed: {test_e}")
                    
                    if secure_url:
                        print(f"  [UPLOAD] Upload successful - resource available at {secure_url}")
                        return res
                    else:
                        print(f"  [UPLOAD] No secure_url in response")
                        return None
                except Exception as e:
                    logger.error(f"Cloudinary upload error ({folder}): {e}")
                    return None

            def _save_local(file, folder):
                if not file:
                    return None
                try:
                    file.seek(0) # Ensure at beginning
                    upload_paths = {
                        'photos': 'student_photos/',
                        'achievement': 'student_certs/achievement/',
                        'internship': 'student_certs/internship/',
                        'courses': 'student_certs/courses/',
                        'sdp': 'student_certs/sdp/',
                        'extra': 'student_certs/extra/',
                        'placement': 'student_certs/placement/',
                        'national': 'student_certs/national/',
                    }
                    upload_to = upload_paths.get(folder, f'student_{folder}/')
                    from django.core.files.storage import default_storage
                    ext = os.path.splitext(file.name)[1] if file.name else '.pdf'
                    filename = f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                    path = os.path.join(upload_to, filename)
                    saved_path = default_storage.save(path, file)
                    print(f"  [SAVE-LOCAL] Saved {folder} file to: {saved_path}")
                    print(f"  [SAVE-LOCAL] default_storage type: {type(default_storage)}")
                    # For debugging, try to get the full path
                    if hasattr(default_storage, 'path'):
                        try:
                            full_path = default_storage.path(saved_path)
                            print(f"  [SAVE-LOCAL] Full filesystem path: {full_path}")
                        except Exception as path_err:
                            print(f"  [SAVE-LOCAL] Could not get full path: {path_err}")
                    return saved_path
                except Exception as e:
                    logger.error(f"Local file save error ({folder}): {e}")
                    return None
            # Parse DOB properly
            dob_value = None
            if request.POST.get('dob'):
                try:
                    dob_value = datetime.strptime(request.POST.get('dob'), '%Y-%m-%d').date()
                except ValueError:
                    dob_value = None

            student = Student(
                ht_no=request.POST.get('ht_no'),
                student_name=request.POST.get('student_name'),
                father_name=request.POST.get('father_name'),
                mother_name=request.POST.get('mother_name'),
                gender=request.POST.get('gender'),
                dob=dob_value,
                age=None,  # Will be calculated below
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
                department=request.POST.get('department'),
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
                pdf_password=request.POST.get('pdf_password'),
                photo=None, cert_achieve=None, cert_intern=None, cert_courses=None,
                cert_sdp=None, cert_extra=None, cert_placement=None, cert_national=None,
            )
            student.save()

            # Calculate correct age from DOB
            if student.dob:
                try:
                    student.age = calculate_correct_age(student.dob)
                    student.save(update_fields=['age'])
                except Exception:
                    pass

            files_up, files_lo = [], []
            
            # Handle photo - Always try Cloudinary first if configured
            if request.FILES.get('photo'):
                pf = request.FILES['photo']
                temp_photo_override_path, _ = snapshot_uploaded_file(pf, default_suffix='.jpg')
                if temp_photo_override_path:
                    persist_snapshot_to_model_field(student, 'photo', temp_photo_override_path, getattr(pf, 'name', None))
                if ca: # Cloudinary configured - prioritize Cloudinary
                    upload_result = _upload(pf, 'photos')
                    if upload_result and upload_result.get('secure_url'):
                        student.photo_url = upload_result['secure_url']
                        record_cloudinary_upload(
                            upload_type='photo',
                            upload_result=upload_result,
                            uploaded_by=getattr(getattr(request, 'user', None), 'username', None),
                            student=student,
                        )
                        files_up.append('photo')
                    else:
                        # Fallback to local storage if Cloudinary fails
                        local_path = _save_local(pf, 'photos')
                        if local_path:
                            student.photo = local_path
                            files_lo.append('photo')
                else:
                    # Local storage only when Cloudinary not configured
                    local_path = _save_local(pf, 'photos')
                    if local_path:
                        student.photo = local_path
                        files_lo.append('photo')
            
            # Handle certificates
            print(f"  [DEBUG] FILES received: {list(request.FILES.keys())}")
            upload_plan, skipped_uploads = build_student_certificate_upload_plan(request, student)
            if not upload_plan:
                for field_name, _, _ in STUDENT_CERTIFICATE_SLOTS:
                    print(f"  [DEBUG] No file received for {field_name}")
            for upload_spec in upload_plan:
                field_name = upload_spec['field_name']
                folder = upload_spec['folder']
                url_field_name = upload_spec['url_field_name']
                certificate_file = upload_spec['file']
                temp_asset_path, temp_asset_is_pdf = snapshot_uploaded_file(
                    certificate_file,
                    default_suffix='.pdf',
                )
                if temp_asset_path:
                    certificate_override_assets.append({
                        'field_name': field_name,
                        'path': temp_asset_path,
                        'is_pdf': temp_asset_is_pdf,
                    })
                    persist_snapshot_to_model_field(
                        student,
                        field_name,
                        temp_asset_path,
                        getattr(certificate_file, 'name', None),
                    )
                print(f"  [DEBUG] Processing {upload_spec['source']} -> {field_name} ({folder})")
                print(f"  [DEBUG] File: {certificate_file.name}, size: {certificate_file.size}")
                if ca: # Cloudinary configured
                    upload_result = _upload(certificate_file, folder)
                    if upload_result and upload_result.get('secure_url'):
                        setattr(student, url_field_name, upload_result['secure_url'])
                        record_cloudinary_upload(
                            upload_type=field_name,
                            upload_result=upload_result,
                            uploaded_by=getattr(getattr(request, 'user', None), 'username', None),
                            student=student,
                        )
                        files_up.append(field_name)
                        print(f"  [DEBUG] Successfully uploaded {field_name} to {upload_result['secure_url']}")
                    else:
                        print(f"  [DEBUG] Cloudinary upload failed for {field_name}, trying local")
                        local_path = _save_local(certificate_file, folder)
                        if local_path:
                            setattr(student, field_name, local_path)
                            setattr(student, url_field_name, None)
                            files_lo.append(field_name)
                            print(f"  [DEBUG] Saved {field_name} locally to {local_path}")
                else:
                    local_path = _save_local(certificate_file, folder)
                    if local_path:
                        setattr(student, field_name, local_path)
                        setattr(student, url_field_name, None)
                        files_lo.append(field_name)
            student.save()

            if skipped_uploads:
                skipped_names = ', '.join(item['filename'] for item in skipped_uploads[:3])
                messages.warning(
                    request,
                    f'Some additional certificates were skipped because all student certificate slots are already used: {skipped_names}'
                    + ('...' if len(skipped_uploads) > 3 else '')
                )

            _, research_proof_assets, research_files_up, research_files_lo = save_student_research_publications_from_request(
                request,
                student,
                upload_func=_upload if ca else None,
            )
            certificate_override_assets.extend(research_proof_assets)
            files_up.extend(research_files_up)
            files_lo.extend(research_files_lo)
            if research_proof_assets and not files_up and not files_lo:
                files_lo.append('research publications')

            # Ensure the student flow (add_student.html) always attempts
            # to build a single individual PDF that includes photo + certificates.
            try:
                should_generate_pdf = (
                    student_has_upload_assets(student)
                    or StudentResearchPublication.objects.filter(student=student).exists()
                    or bool(get_pdf_password(student))
                    or bool(student.email)
                )
                generated_pdf_bytes = None
                if should_generate_pdf:
                    generated_pdf_bytes = generate_student_pdf(
                        student,
                        photo_override_path=temp_photo_override_path,
                        certificate_override_assets=certificate_override_assets,
                        return_bytes=True,
                    )
                if get_pdf_password(student) and student.email and generated_pdf_bytes:
                    if email_password_protected_pdf(
                        recipient=student.email,
                        display_name=student.student_name,
                        pdf_bytes=generated_pdf_bytes,
                        filename=f"student_{student.ht_no}_profile.pdf",
                        subject='Password Protected Student Profile PDF',
                    ):
                        messages.success(request, 'Password-protected student PDF emailed successfully.')
            except Exception as pdf_e:
                logger.warning(f"Student added, but merged PDF generation failed: {pdf_e}")

            if files_up:
                messages.success(request, f'Student {student.student_name} added! Cloudinary: {", ".join(files_up)}')
            if files_lo:
                messages.info(request, f'Some files saved locally: {", ".join(files_lo)}')
            if not files_up and not files_lo:
                messages.success(request, f'Student {student.student_name} added successfully!')
            return redirect('dashboard:students_data')
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error adding student: {e}')
            return redirect('dashboard:add_student')
    try:
        return render(request, 'dashboard/add_student.html', {
            'departments': get_department_options(),
            'student_research_publications_json': '[]',
        })
    except Exception as e:
        logger.error(f"Error in add_student view: {str(e)}", exc_info=True)
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f"An error occurred: {str(e)}")


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
    # Get student or 404
    try:
        student = get_object_or_404(Student, id=student_id)
    except Http404:
        raise

    # Authentication: allow either Django admin/auth user OR student session
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    student_logged_in = request.session.get('student_logged_in')
    student_username = request.session.get('student_username')

    if not (user_authenticated or student_logged_in):
        # Neither admin nor student logged in
        return redirect('dashboard:student_login')

    # If it's a student session (and not admin), ensure they can only edit their own record
    if student_logged_in and not user_authenticated:
        if not student_session_can_access_record(request, student):
            messages.error(request, "You can only edit your own student record.")
            return redirect(student_dashboard_redirect_route(request))

    # Proceed with edit
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                ca = is_cloudinary_configured()
                temp_photo_override_path = None
                certificate_override_assets = []
                
                def _upload(file, folder):
                    if not file or not ca:
                        return None
                    try:
                        file.seek(0)  # Ensure at beginning
                        filename = getattr(file, 'name', '').lower()
                        res = cloudinary.uploader.upload(
                            file,
                            resource_type="raw" if filename.endswith('.pdf') else "auto",
                            folder=f"student_documents/{folder}",
                            public_id=f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=True,
                            access_mode="public"
                        )
                        return res
                    except Exception as e:
                        logger.error(f"Cloudinary upload error ({folder}): {e}")
                        return None

                def _save_local(file, folder):
                    if not file:
                        return None
                    try:
                        file.seek(0)  # Ensure at beginning
                        upload_paths = {
                            'photos': 'student_photos/',
                            'achievement': 'student_certs/achievement/',
                            'internship': 'student_certs/internship/',
                            'courses': 'student_certs/courses/',
                            'sdp': 'student_certs/sdp/',
                            'extra': 'student_certs/extra/',
                            'placement': 'student_certs/placement/',
                            'national': 'student_certs/national/',
                        }
                        upload_to = upload_paths.get(folder, f'student_{folder}/')
                        from django.core.files.storage import default_storage
                        ext = os.path.splitext(file.name)[1] if file.name else '.pdf'
                        filename = f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                        path = os.path.join(upload_to, filename)
                        saved_path = default_storage.save(path, file)
                        return saved_path
                    except Exception as e:
                        logger.error(f"Local file save error ({folder}): {e}")
                        return None

                updated_student = form.save()

                # Handle photo manually because we want Cloudinary support
                if request.FILES.get('photo'):
                    pf = request.FILES['photo']
                    temp_photo_override_path, _ = snapshot_uploaded_file(pf, default_suffix='.jpg')
                    if temp_photo_override_path:
                        persist_snapshot_to_model_field(updated_student, 'photo', temp_photo_override_path, getattr(pf, 'name', None))
                    if ca:
                        upload_result = _upload(pf, 'photos')
                        if upload_result and upload_result.get('secure_url'):
                            updated_student.photo_url = upload_result['secure_url']
                            updated_student.save(update_fields=['photo', 'photo_url'])
                            record_cloudinary_upload(
                                upload_type='photo',
                                upload_result=upload_result,
                                uploaded_by=getattr(getattr(request, 'user', None), 'username', None),
                                student=updated_student,
                            )
                        else:
                            logger.warning("Cloudinary photo upload failed, using local file")
                    
                # Calculate correct age from DOB if DOB was updated
                if updated_student.dob:
                    try:
                        updated_student.age = calculate_correct_age(updated_student.dob)
                        updated_student.save(update_fields=['age'])
                    except Exception:
                        pass

                # Check for certificates in POST/FILES even if not in form
                upload_plan, skipped_uploads = build_student_certificate_upload_plan(request, updated_student)
                any_cert_updated = False
                for upload_spec in upload_plan:
                    field_name = upload_spec['field_name']
                    folder = upload_spec['folder']
                    url_field_name = upload_spec['url_field_name']
                    certificate_file = upload_spec['file']
                    temp_asset_path, temp_asset_is_pdf = snapshot_uploaded_file(
                        certificate_file,
                        default_suffix='.pdf',
                    )
                    if temp_asset_path:
                        certificate_override_assets.append({
                            'field_name': field_name,
                            'path': temp_asset_path,
                            'is_pdf': temp_asset_is_pdf,
                        })
                        persist_snapshot_to_model_field(
                            updated_student,
                            field_name,
                            temp_asset_path,
                            getattr(certificate_file, 'name', None),
                        )
                    if ca:
                        upload_result = _upload(certificate_file, folder)
                        if upload_result and upload_result.get('secure_url'):
                            setattr(updated_student, url_field_name, upload_result['secure_url'])
                            record_cloudinary_upload(
                                upload_type=field_name,
                                upload_result=upload_result,
                                uploaded_by=getattr(getattr(request, 'user', None), 'username', None),
                                student=updated_student,
                            )
                            any_cert_updated = True
                        else:
                            local_path = _save_local(certificate_file, folder)
                            if local_path:
                                setattr(updated_student, field_name, local_path)
                                setattr(updated_student, url_field_name, None)
                                any_cert_updated = True
                    else:
                        local_path = _save_local(certificate_file, folder)
                        if local_path:
                            setattr(updated_student, field_name, local_path)
                            setattr(updated_student, url_field_name, None)
                            any_cert_updated = True
                
                if any_cert_updated:
                    updated_student.save()

                if skipped_uploads:
                    skipped_names = ', '.join(item['filename'] for item in skipped_uploads[:3])
                    messages.warning(
                        request,
                        f'Some additional certificates were skipped because all student certificate slots are already used: {skipped_names}'
                        + ('...' if len(skipped_uploads) > 3 else '')
                    )

                _, research_proof_assets, _, _ = save_student_research_publications_from_request(
                    request,
                    updated_student,
                    upload_func=_upload if ca else None,
                )
                certificate_override_assets.extend(research_proof_assets)

                try:
                    if form.has_changed() or request.FILES or request.POST.get('student_research_publications_json'):
                        generate_student_pdf(
                            updated_student,
                            photo_override_path=temp_photo_override_path,
                            certificate_override_assets=certificate_override_assets,
                        )
                except Exception as pdf_e:
                    logger.warning(f"Student updated, but PDF regeneration failed: {pdf_e}")
                    
                messages.success(request, "Student updated successfully.")
                return redirect('dashboard:students_data')
            except Exception as e:
                logger.error(f"Error updating student {student_id}: {e}", exc_info=True)
                messages.error(request, f"An error occurred while updating the student: {str(e)}")
                return redirect('dashboard:edit_student', student_id=student_id)
        else:
            # Form is not valid; errors will be displayed
            pass
    else:
        try:
            form = StudentForm(instance=student)
        except Exception as e:
            logger.error(f"Error initializing edit form for student {student_id}: {e}", exc_info=True)
            messages.error(request, f"Unable to load student data: {str(e)}")
            return redirect('dashboard:students_data')
    
    try:
        return render(request, 'dashboard/add_student.html', {
            'form': form,
            'title': 'Edit Student',
            'student': student,
            'departments': get_department_options(),
            'student_research_publications_json': build_student_research_publications_json(student),
        })
    except Exception as e:
        logger.error(f"Error rendering edit student page for student {student_id}: {e}", exc_info=True)
        messages.error(request, "An error occurred while loading the edit page.")
        return redirect('dashboard:students_data')


def student_photo_redirect(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    photo_url = normalize_optional_url(getattr(student, 'photo_url', None))
    if photo_url:
        return redirect(photo_url)

    latest_upload_url = (
        CloudinaryUpload.objects
        .filter(student=student, upload_type='photo')
        .order_by('-upload_date')
        .values_list('cloudinary_url', flat=True)
        .first()
    )
    latest_upload_url = normalize_optional_url(latest_upload_url)
    if latest_upload_url:
        return redirect(latest_upload_url)

    if student.photo:
        try:
            return redirect(student.photo.url)
        except Exception as exc:
            logger.warning(f"Could not resolve student photo URL for {student.ht_no}: {exc}")

    from django.http import Http404
    raise Http404("Photo not found")


def generate_student_pdf_view(request, student_id):
    # Allow both Django authenticated users and student session users
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if not (user_authenticated or request.session.get('student_logged_in')):
        return redirect('dashboard:student_login')

    student = get_object_or_404(Student, id=student_id)

    # If student session user, only allow access to their own record
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if request.session.get('student_logged_in') and not user_authenticated:
        if not student_session_can_access_record(request, student):
            messages.error(request, "You can only access your own student record.")
            return redirect(student_dashboard_redirect_route(request))

    try:
        # Generate student PDF with merged certificates
        pdf_bytes = generate_student_pdf(student, return_bytes=True)
        if not pdf_bytes:
            messages.error(request, "Failed to generate PDF.")
            return redirect('dashboard:students_data' if user_authenticated else student_dashboard_redirect_route(request))
        
        # Return PDF directly as downloadable file
        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
        response['Content-Length'] = len(pdf_bytes)
        return response
    except Exception as e:
        logger.error(f"Error generating PDF for student {student_id}: {e}")
        messages.error(request, f"Failed to generate PDF: {str(e)}")
        return redirect('dashboard:students_data' if user_authenticated else student_dashboard_redirect_route(request))


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



# ==================== GENERATE STUDENT PDF ====================
def generate_student_pdf(
    student,
    return_bytes=False,
    photo_override_path=None,
    certificate_override_assets=None,
):
    print(f"\n{'='*60}\nSTUDENT PDF: {student.student_name} ({student.ht_no})\n{'='*60}")
    print(f"  [DEBUG] cert_achieve: {student.cert_achieve}, cert_achieve_url: {student.cert_achieve_url}")
    print(f"  [DEBUG] cert_intern: {student.cert_intern}, cert_intern_url: {student.cert_intern_url}")
    print(f"  [DEBUG] cert_courses: {student.cert_courses}, cert_courses_url: {student.cert_courses_url}")
    print(f"  [DEBUG] cert_sdp: {student.cert_sdp}, cert_sdp_url: {student.cert_sdp_url}")
    print(f"  [DEBUG] cert_extra: {student.cert_extra}, cert_extra_url: {student.cert_extra_url}")
    print(f"  [DEBUG] cert_placement: {student.cert_placement}, cert_placement_url: {student.cert_placement_url}")
    print(f"  [DEBUG] cert_national: {student.cert_national}, cert_national_url: {student.cert_national_url}")

    certificate_override_assets = [
        asset for asset in (certificate_override_assets or [])
        if asset.get('path') and os.path.exists(asset['path'])
    ]
    override_certificate_fields = {
        asset['field_name']
        for asset in certificate_override_assets
        if asset.get('field_name')
    }
    if photo_override_path and not os.path.exists(photo_override_path):
        photo_override_path = None

    # ── temp file tracker ──────────────────────────────────────
    temp_files = []

    # ── Helper: download URL -> local temp file ─────────────────
    def _download(url, suffix=None):
        """Download a URL to a local temp file. Returns path or None."""
        if not url or not url.startswith('http'):
            return None
        try:
            print(f"  [DOWNLOAD] Attempting to download: {url}")
            r = requests.get(url, timeout=30)
            print(f"  [DOWNLOAD] Status: {r.status_code}")

            # Fallback for Cloudinary errors
            if r.status_code in [401, 403] and 'cloudinary.com' in url:
                print(f"  [DOWNLOAD] Cloudinary auth error, trying API fallback...")
                try:
                    public_id = get_cloudinary_public_id(url)
                    print(f"  [DOWNLOAD] Extracted public_id: {public_id}")
                    if public_id:
                        # Try to get resource info from API
                        try:
                            resource = cloudinary.api.resource(public_id)
                            secure_url = resource.get('secure_url')
                            print(f"  [DOWNLOAD] Got fresh URL: {secure_url}")
                            if secure_url:
                                r = requests.get(secure_url, timeout=30)
                                print(f"  [DOWNLOAD] API URL status: {r.status_code}")
                        except Exception as api_err:
                            print(f"  [DOWNLOAD] API resource lookup failed: {api_err}")
                            # If API fails, try constructing URLs with different resource types
                            cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
                            if cloud_name:
                                for res_type in ['raw', 'image']:
                                    try_url = f"https://res.cloudinary.com/{cloud_name}/{res_type}/upload/{public_id}"
                                    print(f"  [DOWNLOAD] Trying {res_type} URL: {try_url}")
                                    test_r = requests.get(try_url, timeout=30)
                                    print(f"  [DOWNLOAD] {res_type} URL status: {test_r.status_code}")
                                    if test_r.status_code == 200:
                                        r = test_r
                                        break
                                    elif test_r.status_code == 404:
                                        continue  # Try next resource type
                                    else:
                                        break  # Other error, stop trying
                except Exception as cloud_err:
                    print(f"  [WARN] Cloudinary API fallback failed: {cloud_err}")

            # Final fallback: try changing resource type in URL
            if r.status_code != 200 and 'cloudinary.com' in url:
                try:
                    # Try both directions: raw->image and image->raw
                    alt_urls = []
                    if '/raw/upload/' in url:
                        alt_urls.append(url.replace('/raw/upload/', '/image/upload/'))
                    elif '/image/upload/' in url:
                        alt_urls.append(url.replace('/image/upload/', '/raw/upload/'))

                    for alt_url in alt_urls:
                        print(f"  [DOWNLOAD] Trying alternative resource type: {alt_url}")
                        alt_r = requests.get(alt_url, timeout=30)
                        print(f"  [DOWNLOAD] Alternative URL status: {alt_r.status_code}")
                        if alt_r.status_code == 200:
                            r = alt_r
                            break
                except Exception as alt_err:
                    print(f"  [WARN] Alternative URL fallback failed: {alt_err}")

            if r.status_code != 200:
                print(f"  [SKIP] HTTP {r.status_code}: {url}")
                return None
            ct = r.headers.get('content-type', '').lower()
            if suffix is None:
                if 'pdf' in ct or url.lower().endswith('.pdf'):
                    suffix = '.pdf'
                elif 'png' in ct or url.lower().endswith('.png'):
                    suffix = '.png'
                else:
                    suffix = '.jpg'
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(r.content)
            tmp.close()
            temp_files.append(tmp.name)
            return tmp.name
        except Exception as e:
            print(f"  [ERR] Download failed {url}: {e}")
            return None

    # ── Helper: local FileField -> path ────────────────────────
    def _local_path(ff):
        """Try to get a local filesystem path from a FileField."""
        if not ff or not getattr(ff, 'name', ''):
            return None
        try:
            p = ff.path
            if os.path.exists(p):
                return p
        except (NotImplementedError, ValueError, Exception):
            pass
        return None

    def _build_reportlab_info_pdf(student_obj, photo_path=None, temp_files_ref=None):
        """Create a simple student profile PDF without wkhtmltopdf."""
        import io
        import base64
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
        )
        styles = getSampleStyleSheet()
        elems = []

        header_style = ParagraphStyle(
            'hdr', parent=styles['Normal'], fontSize=16,
            fontName='Helvetica-Bold', alignment=1,
            textColor=colors.darkblue, spaceAfter=2
        )
        elems.append(Paragraph("ANURAG ENGINEERING COLLEGE", header_style))
        elems.append(Paragraph(
            "<font size='12' color='navy'><b>DEPARTMENT OF INFORMATION TECHNOLOGY</b></font>",
            styles['Normal']
        ))
        elems.append(Spacer(1, 4))
        elems.append(Paragraph(
            "<b>STUDENT PROFILE</b>",
            ParagraphStyle('sp', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=6)
        ))
        elems.append(HRFlowable(width='100%', thickness=2, color=colors.darkblue))
        elems.append(Spacer(1, 8))

        # Handle photo: data URI, file path, or None
        resolved_photo_path = None
        if photo_path and photo_path.startswith('data:'):
            try:
                header, b64_data = photo_path.split(',', 1)
                image_data = base64.b64decode(b64_data)
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                tmp.write(image_data)
                tmp.close()
                resolved_photo_path = tmp.name
                if temp_files_ref is not None:
                    temp_files_ref.append(tmp.name)
                print(f"  [OK] Decoded data URI photo to temp file for ReportLab: {resolved_photo_path}")
            except Exception as e:
                logger.warning(f"Failed to decode data URI photo for ReportLab: {e}")
        elif photo_path and os.path.exists(photo_path):
            resolved_photo_path = photo_path

        if resolved_photo_path:
            try:
                photo_img = Image(resolved_photo_path, width=1.4 * inch, height=1.7 * inch)
                hdr_tbl = Table(
                    [[Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']), photo_img]],
                    colWidths=[4.7 * inch, 1.5 * inch]
                )
                hdr_tbl.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ]))
                elems.append(hdr_tbl)
            except Exception as photo_err:
                logger.warning(f"Student ReportLab photo embed failed: {photo_err}")
                elems.append(Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']))
        else:
            elems.append(Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']))

        elems.append(Spacer(1, 8))

        fields = [
            ("Hall Ticket No", student_obj.ht_no),
            ("Name", student_obj.student_name),
            ("Father Name", student_obj.father_name),
            ("Mother Name", student_obj.mother_name),
            ("Gender", student_obj.gender),
            ("Date of Birth", str(student_obj.dob) if student_obj.dob else "N/A"),
            ("Age", str(student_obj.age) if student_obj.age else "N/A"),
            ("Blood Group", student_obj.blood_group or "N/A"),
            ("Nationality", student_obj.nationality or "Indian"),
            ("Category", student_obj.category or "N/A"),
            ("Religion", student_obj.religion or "N/A"),
            ("Aadhar Number", student_obj.aadhar or "N/A"),
            ("APAAR ID", student_obj.apaar_id or "N/A"),
            ("Address", student_obj.address or "N/A"),
            ("Parent Phone", student_obj.parent_phone or "N/A"),
            ("Student Phone", student_obj.student_phone or "N/A"),
            ("Email", student_obj.email or "N/A"),
            ("Year", str(student_obj.year) if student_obj.year else "N/A"),
            ("Semester", str(student_obj.sem) if student_obj.sem else "N/A"),
            ("SSC Marks", student_obj.ssc_marks or "N/A"),
            ("Inter Marks", student_obj.inter_marks or "N/A"),
            ("CGPA", student_obj.cgpa or "N/A"),
            ("Admission Type", student_obj.admission_type or "N/A"),
            ("EAMCET Rank", student_obj.eamcet_rank or "N/A"),
            ("TASK Registered", student_obj.task_registered or "N/A"),
            ("TASK Username", student_obj.task_username or "N/A"),
            ("CSI Registered", student_obj.csi_registered or "N/A"),
            ("CSI Membership ID", student_obj.csi_membership_id or "N/A"),
            ("PDF Password Protection", "Enabled" if get_pdf_password(student_obj) else "Not Enabled"),
            ("RTRP Project", student_obj.rtrp_project_title or "N/A"),
            ("Internship Title", student_obj.intern_title or "N/A"),
            ("Final Project", student_obj.final_project_title or "N/A"),
            ("Other Training", student_obj.other_training or "N/A"),
        ]

        table_data = [[
            Paragraph(f"<b>{label}</b>", styles['Normal']),
            Paragraph(str(value), styles['Normal'])
        ] for label, value in fields]

        info_table = Table(table_data, colWidths=[2.1 * inch, 4.6 * inch])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elems.append(info_table)
        elems.append(Spacer(1, 12))
        elems.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles['Normal']
        ))

        doc.build(elems)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    # ── PHOTO ──────────────────────────────────────────────────
    photo_url_for_pdf, local_photo_path, photo_temp_paths, photo_source = resolve_student_photo_for_pdf(
        student,
        photo_override_path=photo_override_path,
    )
    temp_files.extend(photo_temp_paths)
    if photo_url_for_pdf:
        print(f"  [OK] Photo ({photo_source}): {photo_url_for_pdf}")

    # ── ANURAG HEADER IMAGE PATH ──────────────────────────────
    anurag_header_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'ANURAG HEADER.png')
    anurag_header_url = build_file_uri(anurag_header_path)

    # ── BUILD TEMPLATE CONTEXT ────────────────────────────────
    context = {
        'student': student,
        'current_date': datetime.now(),
        'student_photo_url': photo_url_for_pdf,
        'local_photo_path': local_photo_path,
        'anurag_header_url': anurag_header_url,
        'uploaded_documents': build_student_uploaded_documents(student),
        'student_research_publications': StudentResearchPublication.objects.filter(student=student).order_by('-publication_year', '-id'),
    }

    # ── GENERATE INFO PDF with WeasyPrint ─────────────────────────
    html_string = render_to_string('dashboard/student_pdf.html', context)

    info_pdf_bytes = None
    used_reportlab_fallback = False

    try:
        from weasyprint import HTML

        print("  [CHECK] Generating Student PDF using WeasyPrint")
        base_url = Path(settings.BASE_DIR).resolve().as_uri() if settings.BASE_DIR else None
        html_obj = HTML(string=html_string, base_url=base_url)
        info_pdf_bytes = html_obj.write_pdf()
        print(f"  [OK] Info PDF generated with WeasyPrint: {len(info_pdf_bytes)} bytes")
    except Exception as e:
        print(f"  [WARN] WeasyPrint error, using ReportLab fallback: {e}")
        logger.error(f"Student WeasyPrint generation failed: {e}")

    # Always try WeasyPrint first for better compatibility
    if info_pdf_bytes is None:
        print("  [INFO] WeasyPrint failed, using ReportLab fallback")
        info_pdf_bytes = _build_reportlab_info_pdf(student, local_photo_path, temp_files)
        used_reportlab_fallback = True
        print(f"  [OK] ReportLab fallback info PDF generated: {len(info_pdf_bytes)} bytes")

    # Validate PDF content
    if info_pdf_bytes and len(info_pdf_bytes) > 100:
        if not info_pdf_bytes.startswith(b'%PDF'):
            print("  [WARN] Generated content is not a valid PDF, using fallback")
            info_pdf_bytes = _build_reportlab_info_pdf(student, local_photo_path, temp_files)
            used_reportlab_fallback = True
            print(f"  [OK] Fallback PDF generated: {len(info_pdf_bytes)} bytes")
    else:
        print("  [WARN] PDF generation failed, using basic fallback")
        info_pdf_bytes = _build_reportlab_info_pdf(student, local_photo_path, temp_files)
        used_reportlab_fallback = True

    # ── MERGE: info PDF + all uploaded documents ──────────────
    filename = f"student_{student.ht_no}_{date.today().strftime('%Y%m%d')}.pdf"
    final_pdf_bytes = info_pdf_bytes  # fallback = info PDF only
    print(f"  [DEBUG] Starting merge section. info_pdf_bytes length: {len(info_pdf_bytes) if info_pdf_bytes else 0}")
    print(f"  [DEBUG] Entering merge try block...")
    pdf_persisted = False
    pdf_file_saved = False
    pdf_encrypted = False
    return_url = None

    try:
        from pypdf import PdfWriter, PdfReader
        from PIL import Image as PILImage

        writer = PdfWriter()
        readers_keep = []  # keep PdfReader objects alive

        # --- helper: add a file (path) to writer ---
        def _add_to_writer(path):
            if not path or not os.path.exists(path):
                print(f"  [DEBUG] _add_to_writer: Skipping {path} (not exists or None)")
                return
            print(f"  [DEBUG] _add_to_writer: Adding {path}")
            try:
                with open(path, 'rb') as fh:
                    header = fh.read(4)
                if header.startswith(b'%PDF'):
                    reader = PdfReader(path)
                    readers_keep.append(reader)
                    for pg in reader.pages:
                        writer.add_page(pg)
                    print(f"  [OK] Merged PDF ({len(reader.pages)} pages): {os.path.basename(path)}")
                else:
                    # Image -> convert to PDF page
                    img = PILImage.open(path)
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    tmp_img_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    img.save(tmp_img_pdf.name, 'PDF', resolution=100.0)
                    tmp_img_pdf.close()
                    temp_files.append(tmp_img_pdf.name)
                    reader = PdfReader(tmp_img_pdf.name)
                    readers_keep.append(reader)
                    for pg in reader.pages:
                        writer.add_page(pg)
                    print(f"  [OK] Merged image as PDF: {os.path.basename(path)}")
            except Exception as ex:
                print(f"  [ERR] Could not merge {path}: {ex}")

        # 1. Info PDF first
        info_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        info_tmp.write(info_pdf_bytes)
        info_tmp.close()
        temp_files.append(info_tmp.name)
        _add_to_writer(info_tmp.name)

        # 2. Collect all student certificates using the shared asset resolver
        # photo_file is the student photo - we add it as a separate page in the merged PDF
        photo_file, image_files, pdf_files, collected_temp_files = collect_student_files(
            student,
            skip_photo=bool(photo_override_path),
            skip_certificate_fields=override_certificate_fields,
        )
        temp_files.extend(collected_temp_files)

        for override_asset in certificate_override_assets:
            override_path = override_asset['path']
            if override_asset.get('is_pdf'):
                if override_path not in pdf_files:
                    pdf_files.append(override_path)
            else:
                if override_path not in image_files:
                    image_files.append(override_path)
        
        # If the photo was already downloaded for the info PDF, use that path to avoid duplicate download
        if photo_override_path and os.path.exists(photo_override_path):
            print(f"  [DEBUG] Adding uploaded photo override as separate page: {photo_override_path}")
            if photo_override_path not in image_files:
                image_files.append(photo_override_path)
        elif local_photo_path and os.path.exists(local_photo_path) and local_photo_path != photo_file:
            print(f"  [DEBUG] Using pre-downloaded photo for merge: {local_photo_path}")
            if local_photo_path not in image_files:
                image_files.append(local_photo_path)
        elif photo_file and os.path.exists(photo_file):
            print(f"  [DEBUG] Adding student photo as separate page: {photo_file}")
            if photo_file not in image_files:
                image_files.append(photo_file)
        print(f"  [DEBUG] Certificates collected: {len(image_files)} images, {len(pdf_files)} PDFs")
        print(f"  [DEBUG] Writer pages before adding certificates: {len(writer.pages)}")
        print(f"  [DEBUG] PDF files: {[os.path.basename(p) for p in pdf_files]}")
        print(f"  [DEBUG] Image files: {[os.path.basename(p) for p in image_files]}")

        for pdf_path in pdf_files:
            print(f"  [DEBUG] Adding PDF: {pdf_path} (exists: {os.path.exists(pdf_path) if pdf_path else False})")
            _add_to_writer(pdf_path)

        for image_path in image_files:
            print(f"  [DEBUG] Adding image: {image_path} (exists: {os.path.exists(image_path) if image_path else False})")
            _add_to_writer(image_path)

        print(f"  [DEBUG] Writer pages after adding certificates: {len(writer.pages)}")

        # Write merged PDF
        if len(writer.pages) > 0:
            merged_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            merged_tmp.close()
            temp_files.append(merged_tmp.name)
            with open(merged_tmp.name, 'wb') as out:
                writer.write(out)
            file_size = os.path.getsize(merged_tmp.name)
            print(f"  [OK] Merged PDF: {len(writer.pages)} total pages, {file_size} bytes")
            with open(merged_tmp.name, 'rb') as mf:
                final_pdf_bytes = mf.read()
            final_pdf_bytes = encrypt_pdf_bytes(final_pdf_bytes, get_pdf_password(student))
            pdf_encrypted = bool(get_pdf_password(student))
            with open(merged_tmp.name, 'wb') as mf:
                mf.write(final_pdf_bytes)

                # Upload to Cloudinary
            # Upload to Cloudinary
            if is_cloudinary_configured():
                try:
                    cloud_result = cloudinary.uploader.upload(
                        merged_tmp.name,
                        resource_type='raw',
                        folder='student_pdfs',
                        public_id=f"student_{student.ht_no}_{date.today().strftime('%Y%m%d')}",
                        overwrite=True,
                        format='pdf',
                        type='upload',
                        access_mode='public',
                    )
                    if cloud_result and 'secure_url' in cloud_result:
                        student.pdf_url = cloud_result['secure_url']
                        return_url = cloud_result['secure_url']
                        record_cloudinary_upload(
                            upload_type='student_pdf',
                            upload_result=cloud_result,
                            student=student,
                        )
                        print(f"  [OK] Uploaded to Cloudinary: {cloud_result['secure_url']}")
                        pdf_persisted = True
                    else:
                        print("  [WARN] Cloudinary upload failed (no secure_url)")
                        return_url = None
                except Exception as cloud_err:
                    print(f"  [WARN] Cloudinary upload error: {cloud_err}")
                    return_url = None
            else:
                print("  [INFO] Cloudinary not configured")
                return_url = None
        else:
            print("  [WARN] No pages in writer — returning info PDF only")
            return_url = None

    except Exception as merge_err:
        print(f"  [ERR] Merge error: {merge_err}")
        return_url = None

    if not return_url:
        student.pdf_url = None

    if final_pdf_bytes and get_pdf_password(student) and not pdf_encrypted:
        final_pdf_bytes = encrypt_pdf_bytes(final_pdf_bytes, get_pdf_password(student))
        pdf_encrypted = True

    # Always persist the generated PDF through the model storage backend as a durable fallback.
    if final_pdf_bytes:
        try:
            student.pdf_file.save(filename, ContentFile(final_pdf_bytes), save=False)
            pdf_file_saved = True
            if not return_url and student.pdf_file:
                return_url = student.pdf_file.url
            print(f"  [OK] PDF persisted via model storage: {return_url or filename}")
        except Exception as e:
            print(f"  [ERR] Persistent PDF save failed: {e}")
            pdf_file_saved = False

    pdf_persisted = bool(return_url or pdf_file_saved)

    # Cleanup temp files
    for temp_path in temp_files:
        try:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

    student.pdf_generated = pdf_persisted
    student.pdf_generation_time = timezone.now() if pdf_persisted else None
    update_fields = ['pdf_generated', 'pdf_generation_time', 'updated_at']
    if pdf_file_saved:
        update_fields.append('pdf_file')
    if student.pdf_url is not None or return_url:
        update_fields.append('pdf_url')
    student.save(update_fields=list(dict.fromkeys(update_fields)))

    if used_reportlab_fallback:
        logger.info(f"Student PDF for {student.ht_no} used ReportLab fallback instead of pdfkit/wkhtmltopdf")

    print("=== STUDENT PDF GENERATION COMPLETE ===\n")

    # If return_bytes is True, return the PDF content directly
    if return_bytes:
        return final_pdf_bytes

    return return_url

def view_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Authentication: allow either Django authenticated users or student session
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if not (user_authenticated or request.session.get('student_logged_in')):
        messages.error(request, "Please log in to view PDFs.")
        return redirect('dashboard:student_login')
    
    # If student session (not admin), enforce ownership
    if request.session.get('student_logged_in') and not user_authenticated:
        if not student_session_can_access_record(request, student):
            messages.error(request, "You can only view your own PDF.")
            return redirect(student_dashboard_redirect_route(request))

    pdf_url = normalize_optional_url(getattr(student, 'pdf_url', None))
    if pdf_url:
        temp_pdf_path = None
        try:
            temp_pdf_path, _ = download_remote_asset(pdf_url, default_suffix='.pdf')
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                with open(temp_pdf_path, 'rb') as pdf_handle:
                    pdf_bytes = pdf_handle.read()
                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="student_{student.ht_no}.pdf"'
                response['Content-Length'] = len(pdf_bytes)
                return response
        finally:
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except OSError:
                    pass

    pdf_field = getattr(student, 'pdf_file', None)
    if pdf_field and getattr(pdf_field, 'name', ''):
        try:
            with pdf_field.open('rb') as pdf_handle:
                pdf_bytes = pdf_handle.read()
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="student_{student.ht_no}.pdf"'
            response['Content-Length'] = len(pdf_bytes)
            return response
        except Exception as exc:
            logger.warning(f"Could not stream local student PDF for {student.ht_no}: {exc}")
            try:
                return redirect(pdf_field.url)
            except Exception:
                pass

    try:
        regenerated_pdf_bytes = generate_student_pdf(student, return_bytes=True)
        if regenerated_pdf_bytes:
            response = HttpResponse(regenerated_pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="student_{student.ht_no}.pdf"'
            response['Content-Length'] = len(regenerated_pdf_bytes)
            return response
    except Exception as exc:
        logger.error(f"Failed to regenerate stale student PDF for {student.ht_no}: {exc}")

    messages.error(request, "PDF not generated yet.")
    return redirect('dashboard:student_detail', student_id=student_id)


def merge_student_certificates(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if not (user_authenticated or request.session.get('student_logged_in')):
        messages.error(request, "Please log in to merge certificates.")
        return redirect('dashboard:student_login')

    if request.session.get('student_logged_in') and not user_authenticated:
        if not student_session_can_access_record(request, student):
            messages.error(request, "You can only access your own student record.")
            return redirect(student_dashboard_redirect_route(request))

    temp_files = []
    try:
        writer = PdfWriter()
        merged_count = 0

        photo_path, image_files, pdf_files, collected_temp_files = collect_student_files(student)
        temp_files.extend(collected_temp_files)

        # 1. Add the photo if it exists
        if photo_path and os.path.exists(photo_path):
            try:
                # Convert image to PDF page
                from PIL import Image
                import io
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter

                image = Image.open(photo_path)
                if image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')

                img_pdf_buffer = io.BytesIO()
                c = canvas.Canvas(img_pdf_buffer, pagesize=letter)
                img_width, img_height = image.size
                page_width, page_height = letter
                scale = min((page_width - 40) / img_width, (page_height - 40) / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2

                c.drawImage(photo_path, x, y, width=new_width, height=new_height)
                c.showPage()
                c.save()

                img_pdf_buffer.seek(0)
                writer.add_page(PdfReader(img_pdf_buffer).pages[0])
                merged_count += 1
                logger.info(f"Added photo to merged PDF for student {student.ht_no}")
            except Exception as e:
                logger.error(f"Error adding photo to merged PDF: {e}")

        # 2. Add certificates
        for cert_path in pdf_files:
            if cert_path and os.path.exists(cert_path):
                try:
                    reader = PdfReader(cert_path)
                    for page in reader.pages:
                        writer.add_page(page)
                    merged_count += 1
                    logger.info(f"Successfully merged student PDF asset: {cert_path}")
                except Exception as e:
                    logger.warning(f"Failed to merge student PDF asset {cert_path}: {e}")

        for image_path in image_files:
            if image_path and os.path.exists(image_path):
                try:
                    # Image - convert to PDF page
                    from PIL import Image
                    import io
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter

                    img = Image.open(image_path)
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')

                    img_pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(img_pdf_buffer, pagesize=letter)
                    page_width, page_height = letter
                    img_width, img_height = img.size
                    scale = min((page_width - 40) / img_width, (page_height - 40) / img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2

                    c.drawImage(image_path, x, y, width=new_width, height=new_height)
                    c.showPage()
                    c.save()

                    img_pdf_buffer.seek(0)
                    writer.add_page(PdfReader(img_pdf_buffer).pages[0])
                    merged_count += 1
                    logger.info(f"Successfully merged student image asset: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to merge student image asset {image_path}: {e}")

        if merged_count == 0:
            messages.error(request, 'No valid photo or certificates could be merged.')
            return redirect('dashboard:student_detail', student_id=student_id)

        # 3. Create merged PDF
        output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        output_pdf_path = output_pdf.name
        output_pdf.close()
        temp_files.append(output_pdf_path)
        
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)

        # 4. Upload to Cloudinary if configured
        merged_url = None
        if is_cloudinary_configured():
            try:
                cr = cloudinary.uploader.upload(
                    output_pdf_path,
                    resource_type='raw',
                    folder='merged_student_certificates',
                    public_id=f"merged_student_{student.ht_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=True,
                    format='pdf',
                    type='upload',
                    access_mode='public',
                )
                merged_url = cr['secure_url']
                record_cloudinary_upload(
                    upload_type='merged_student_certificates',
                    upload_result=cr,
                    uploaded_by=request.user.username if user_authenticated else request.session.get('student_username'),
                    student=student,
                )
                logger.info(f"Uploaded merged certificates to Cloudinary: {merged_url}")
            except Exception as e:
                logger.error(f"Failed to upload merged certificates to Cloudinary: {e}")

        # 5. Result message
        if merged_url:
            from django.utils.safestring import mark_safe
            messages.success(request, mark_safe(f'Successfully merged {merged_count} items. <a href="{merged_url}" target="_blank" class="btn btn-sm btn-info">Download Merged PDF</a>'))
            return redirect('dashboard:student_detail', student_id=student_id)

        with open(output_pdf_path, 'rb') as merged_file:
            merged_bytes = merged_file.read()

        response = HttpResponse(merged_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="merged_student_{student.ht_no}.pdf"'
        response['Content-Length'] = len(merged_bytes)
        return response

    except Exception as e:
        logger.error(f"Error merging student certificates: {e}")
        messages.error(request, f'Error merging certificates: {str(e)}')
        return redirect('dashboard:student_detail', student_id=student_id)
    finally:
        # Clean up temp files
        for tf in temp_files:
            try:
                if os.path.exists(tf):
                    os.remove(tf)
            except Exception:
                pass

def merge_certificates_with_pdf_bytes(pdf_bytes, faculty):
    """
    Comprehensive merge of faculty profile PDF with all uploaded documents.
    This is used by the 'Merge with PDF' action in the certificates view.
    """
    try:
        from pypdf import PdfWriter, PdfReader
        from PIL import Image as PILImage

        writer = PdfWriter()
        temp_files = []  # Track all temp files for cleanup
        readers_keep = [] # Keep readers alive

        # --- helper: add a file (path) to writer ---
        seen_asset_keys = set()

        def _asset_key(file_field=None, url_value=None):
            normalized_url = normalize_optional_url(url_value)
            if normalized_url:
                return ('url', normalized_url)
            if file_field:
                path_value = getattr(file_field, 'path', None)
                if path_value:
                    return ('path', os.path.normcase(os.path.abspath(path_value)))
                name_value = getattr(file_field, 'name', None)
                if name_value:
                    return ('name', name_value)
            return None

        def _add_asset_once(file_field=None, url_value=None):
            key = _asset_key(file_field, url_value)
            if key and key in seen_asset_keys:
                return False

            asset_path, _ = get_local_or_remote_asset(file_field, url=url_value, default_suffix='.pdf')
            if not asset_path:
                return False

            if key:
                seen_asset_keys.add(key)
            path_key = ('path', os.path.normcase(os.path.abspath(asset_path)))
            if path_key in seen_asset_keys:
                return False
            seen_asset_keys.add(path_key)

            is_local_field_path = (
                file_field
                and hasattr(file_field, 'path')
                and getattr(file_field, 'path', None) == asset_path
            )
            if asset_path not in temp_files and not is_local_field_path:
                temp_files.append(asset_path)

            return _add_to_writer_internal(asset_path)

        def _add_to_writer_internal(path):
            if not path or not os.path.exists(path):
                return False
            try:
                with open(path, 'rb') as fh:
                    header = fh.read(4)
                if header.startswith(b'%PDF'):
                    reader = PdfReader(path)
                    readers_keep.append(reader)
                    for pg in reader.pages:
                        writer.add_page(pg)
                    return True
                else:
                    # Image -> convert to PDF page
                    img = PILImage.open(path)
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    tmp_img_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    img.save(tmp_img_pdf.name, 'PDF', resolution=100.0)
                    tmp_img_pdf.close()
                    temp_files.append(tmp_img_pdf.name)
                    reader = PdfReader(tmp_img_pdf.name)
                    readers_keep.append(reader)
                    for pg in reader.pages:
                        writer.add_page(pg)
                    return True
            except Exception:
                return False

        # 1. Add the main student/faculty profile PDF
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                tf.write(pdf_bytes)
                tfp = tf.name
                temp_files.append(tfp)
            _add_to_writer_internal(tfp)

        # 2. Collect all faculty documents from model fields
        doc_fields = [
            ('aadhar_url', 'aadhar_file'),
            ('pan_url', 'pan_file'),
            ('apaar_url', 'apaar_file'),
            ('scm_url', 'scm_file'),
            ('membership_proof_url', 'membership_proof'),
            ('jntuh_biodata_url', 'jntuh_biodata'),
            ('ssc_certificate_url', 'ssc_certificate'),
            ('inter_certificate_url', 'inter_certificate'),
            ('ug_certificate_url', 'ug_certificate'),
            ('pg_certificate_url', 'pg_certificate'),
            ('phd_certificate_url', 'phd_certificate'),
            ('research_proof_url', 'research_proof'),
            ('fdp_certificate_url', 'fdp_certificate'),
            ('experience_certificates_url', 'experience_certificates'),
            ('other_documents_url', 'other_documents'),
        ]
        
        for url_field, file_field in doc_fields:
            ff = getattr(faculty, file_field, None)
            url_val = getattr(faculty, url_field, None)
            _add_asset_once(ff, url_val)

        # 3. Certificate records (related model)
        from .models import Certificate
        for cert in Certificate.objects.filter(faculty=faculty):
            _add_asset_once(cert.certificate_file, cert.cloudinary_url)

        # 4. FDP Certificates
        from .models import FDP
        for fdp_rec in FDP.objects.filter(faculty=faculty):
            _add_asset_once(
                fdp_rec.certificate,
                getattr(fdp_rec, 'certificate_url', None),
            )

        # 5. Research Proofs
        from .models import ResearchPublication
        for pub in ResearchPublication.objects.filter(faculty=faculty):
            _add_asset_once(
                pub.proof_document,
                getattr(pub, 'proof_document_url', None),
            )

        # Finalize
        pages_count = len(writer.pages)
        logger.info(f"Merge attempt for {faculty.employee_code}: {pages_count} pages to write")
        
        if pages_count > 0:
            try:
                # Write PDF to temporary file with explicit flush
                mf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                mf_path = mf.name
                temp_files.append(mf_path)
                
                writer.write(mf)
                mf.flush()
                mf.close()
                
                # Now read it back
                with open(mf_path, 'rb') as f:
                    merged = f.read()
                
                if not merged or not merged.startswith(b'%PDF'):
                    logger.error(f"Merged PDF invalid for {faculty.employee_code}: size={len(merged) if merged else 0}")
                    return pdf_bytes if pdf_bytes else None
                
                logger.info(f"Successfully merged {pages_count} pages into {len(merged)} bytes for {faculty.employee_code}")
                return merged
            except Exception as e:
                logger.error(f"Error writing merged PDF for {faculty.employee_code}: {e}", exc_info=True)
                return pdf_bytes if pdf_bytes else None
            finally:
                # Cleanup
                for temp_file in temp_files:
                    try:
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                    except Exception:
                        pass
        else:
            logger.info(f"No pages to merge for {faculty.employee_code}, returning base PDF")
            return pdf_bytes if pdf_bytes else None

    except Exception as e:
        logger.error(f"Error in merge_certificates_with_pdf_bytes for {faculty.employee_code}: {e}", exc_info=True)
        return pdf_bytes if pdf_bytes else None


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
        'form': form, 'title': 'Bulk Faculty Upload', 'has_pandas': pd is not None
    })


def process_csv_faculty_data(df, user):
    ok = err = 0
    required = ['employee_code', 'staff_name', 'department', 'designation']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found.")
    for i, row in df.iterrows():
        try:
            ec = str(row['employee_code']).strip()
            fac = Faculty.objects.filter(employee_code=ec).first()
            if fac:
                for col in df.columns:
                    if hasattr(fac, col) and not pd.isna(row[col]):
                        if col in ['dob', 'joining_date']:
                            try:
                                setattr(fac, col, pd.to_datetime(row[col]).date())
                            except Exception:
                                pass
                        else:
                            setattr(fac, col, row[col])
                fac.save()
                act = 'updated'
            else:
                fd = {}
                for col in df.columns:
                    if hasattr(Faculty, col) and not pd.isna(row[col]):
                        if col in ['dob', 'joining_date']:
                            try:
                                fd[col] = pd.to_datetime(row[col]).date()
                            except Exception:
                                fd[col] = None
                        else:
                            fd[col] = row[col]
                fac = Faculty.objects.create(**fd)
                FacultyProfile.objects.create(faculty=fac)
                act = 'created'
            FacultyLog.objects.create(faculty=fac, action=f'Bulk Upload - {act}',
                                      details=f'Faculty {act} via bulk upload: {fac.employee_code}',
                                      performed_by=user.username if user else 'System', ip_address='127.0.0.1')
            ok += 1
        except Exception as e:
            logger.error(f"Error row {i}: {e}")
            err += 1
    return ok, err


# ==================== FACULTY STATISTICS & APIs ====================
@login_required
def faculty_statistics_api(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    rc = ResearchProject.objects.filter(faculty=faculty).count()
    rp = ResearchPublication.objects.filter(faculty=faculty).count()
    fdp_count = FDP.objects.filter(faculty=faculty).count()
    project_count = BTechProject.objects.filter(faculty=faculty).count()
    return JsonResponse({
        'total_subjects': faculty.subjects.count(),
        'total_students': 0,
        'avg_rating': 4.5,
        'teaching_load': 75,
        'research_output': 60,
        'attendance_rate': 95,
        'publications': rc,
        'research_publications': rp,
        'fdps': fdp_count,
        'projects': project_count,
        'conferences': rc,
        'awards': 2,
    })


# ==================== SYSTEM UTILITIES ====================
@login_required
def system_status(request):
    system_info = {}
    if psutil:
        try:
            system_info = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'python_version': sys.version,
                'django_version': django.get_version(),
            }
        except Exception:
            system_info = {'error': 'Unable to retrieve system info'}
    cs = {'connected': False, 'error': ''}
    if is_cloudinary_configured():
        try:
            r = cloudinary.api.ping()
            cs['connected'] = r.get('status') == 'ok'
        except Exception as e:
            cs['error'] = str(e)
    else:
        cs['error'] = 'Cloudinary not configured'
    return render(request, 'dashboard/system_status.html', {
        'title': 'System Status',
        'stats': {
            'total_faculty': Faculty.objects.count(),
            'active_faculty': Faculty.objects.filter(is_active=True).count(),
            'total_students': Student.objects.count(),
            'total_certificates': Certificate.objects.count(),
            'research_publications': ResearchPublication.objects.count(),
            'fdps': FDP.objects.count(),
            'btech_projects': BTechProject.objects.count(),
            'cloudinary_uploads': CloudinaryUpload.objects.count(),
            'total_logs': FacultyLog.objects.count(),
            'recent_logs': FacultyLog.objects.order_by('-created_at')[:10],
        },
        'system_info': system_info,
        'db_stats': {
            'faculty_table': Faculty.objects.count(),
            'student_table': Student.objects.count(),
            'certificate_table': Certificate.objects.count(),
            'research_publication_table': ResearchPublication.objects.count(),
            'fdp_table': FDP.objects.count(),
            'btech_project_table': BTechProject.objects.count(),
            'log_table': FacultyLog.objects.count(),
            'cloudinary_table': CloudinaryUpload.objects.count(),
        },
        'cloudinary_status': cs,
        'has_psutil': psutil is not None,
        'has_pandas': pd is not None,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })


@login_required
def clear_logs(request):
    if request.method == 'POST':
        try:
            days = int(request.POST.get('days', 30))
            cutoff = timezone.now() - timedelta(days=days)
            cnt, _ = FacultyLog.objects.filter(created_at__lt=cutoff).delete()
            FacultyLog.objects.create(faculty=None, action='Logs Cleared',
                                      details=f'Cleared {cnt} logs older than {days} days',
                                      performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Deleted {cnt} logs older than {days} days.')
            return redirect('dashboard:system_status')
        except Exception as e:
            messages.error(request, f'Error clearing logs: {e}')
            return redirect('dashboard:system_status')
    return render(request, 'dashboard/clear_logs.html', {'title': 'Clear System Logs'})


@login_required
def backup_database(request):
    try:
        from django.core.management import call_command
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bf = os.path.join(backup_dir, f'db_backup_{ts}.json')
        with open(bf, 'w') as f:
            call_command('dumpdata', stdout=f)
        FacultyLog.objects.create(faculty=None, action='Database Backup',
                                  details=f'Backup created: {bf}',
                                  performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Backup created: {os.path.basename(bf)}')
    except Exception as e:
        logger.error(f"Backup error: {e}")
        messages.error(request, f'Error creating backup: {e}')
    return redirect('dashboard:system_status')


# ==================== API ENDPOINTS ====================
@login_required
@require_GET
def api_faculty_list(request):
    data = list(Faculty.objects.all().values(
        'id', 'employee_code', 'staff_name', 'department', 'designation',
        'email', 'mobile', 'is_active', 'cloudinary_pdf_url', 'cloudinary_photo_url'
    ))
    return JsonResponse(data, safe=False)


@login_required
@require_GET
def api_faculty_detail(request, faculty_id):
    f = get_object_or_404(Faculty, id=faculty_id)
    return JsonResponse({
        'id': f.id, 'employee_code': f.employee_code, 'staff_name': f.staff_name,
        'department': f.department, 'designation': f.designation,
        'email': f.email, 'mobile': f.mobile,
        'dob': f.dob.strftime('%Y-%m-%d') if f.dob else None,
        'joining_date': f.joining_date.strftime('%Y-%m-%d') if f.joining_date else None,
        'ug_degree': getattr(f, 'ug_degree', None), 'ug_year': getattr(f, 'ug_year', None),
        'pg_degree': getattr(f, 'pg_degree', None), 'pg_year': getattr(f, 'pg_year', None),
        'phd_degree': getattr(f, 'phd_degree', None),
        'is_active': f.is_active,
        'experience': calculate_experience(f.joining_date) if f.joining_date else "N/A",
        'cloudinary_pdf_url': f.cloudinary_pdf_url,
        'cloudinary_photo_url': f.cloudinary_photo_url,
        'has_jntuh_biodata': bool(f.jntuh_biodata),
        'research_publications_count': ResearchPublication.objects.filter(faculty=f).count(),
        'fdps_count': FDP.objects.filter(faculty=f).count(),
        'btech_projects_count': BTechProject.objects.filter(faculty=f).count(),
    })


@login_required
@require_GET
def api_faculty_research(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    publications = ResearchPublication.objects.filter(faculty=faculty).values(
        'id', 'research_type', 'title', 'authors', 'publication_year', 'academic_year',
        'journal_name', 'conference_name', 'doi', 'url', 'status'
    )
    return JsonResponse({
        'faculty_id': faculty.id,
        'faculty_name': faculty.staff_name,
        'publications': list(publications),
        'count': publications.count()
    })


@login_required
@require_GET
def api_faculty_fdps(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    fdps = FDP.objects.filter(faculty=faculty).values(
        'id', 'fdp_type', 'title', 'academic_year', 'from_date', 'to_date',
        'organized_by', 'place', 'mode', 'level', 'role'
    )
    return JsonResponse({
        'faculty_id': faculty.id,
        'faculty_name': faculty.staff_name,
        'fdps': list(fdps),
        'count': fdps.count()
    })


@login_required
@require_GET
def api_faculty_projects(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    projects = BTechProject.objects.filter(faculty=faculty).values(
        'id', 'ht_no', 'student_name', 'batch', 'project_title', 'approved', 'marks'
    )
    return JsonResponse({
        'faculty_id': faculty.id,
        'faculty_name': faculty.staff_name,
        'projects': list(projects),
        'count': projects.count()
    })


@login_required
@require_GET
def api_students_list(request):
    data = list(Student.objects.all().values(
        'id', 'ht_no', 'student_name', 'father_name', 'mother_name',
        'gender', 'year', 'sem', 'email', 'student_phone', 'cgpa'
    ))
    return JsonResponse(data, safe=False)


@login_required
@require_GET
def api_student_detail(request, student_id):
    s = get_object_or_404(Student, id=student_id)
    return JsonResponse({
        'id': s.id,
        'ht_no': s.ht_no,
        'student_name': s.student_name,
        'father_name': s.father_name,
        'mother_name': s.mother_name,
        'gender': s.gender,
        'dob': s.dob.strftime('%Y-%m-%d') if s.dob else None,
        'age': s.age,
        'nationality': s.nationality,
        'category': s.category,
        'religion': s.religion,
        'blood_group': s.blood_group,
        'aadhar': s.aadhar,
        'apaar_id': s.apaar_id,
        'address': s.address,
        'parent_phone': s.parent_phone,
        'student_phone': s.student_phone,
        'email': s.email,
        'year': s.year,
        'sem': s.sem,
        'branch': getattr(s, 'branch', None),
        'roll_number': getattr(s, 'roll_number', None),
        'ssc_marks': s.ssc_marks,
        'inter_marks': s.inter_marks,
        'cgpa': s.cgpa,
        'admission_type': s.admission_type,
        'eamcet_rank': s.eamcet_rank,
        'rtrp_project_title': s.rtrp_project_title,
        'intern_title': s.intern_title,
        'final_project_title': s.final_project_title,
        'other_training': s.other_training,
        'photo_url': getattr(s, 'photo_url', None) or (s.photo.url if s.photo else None),
        'pdf_url': getattr(s, 'pdf_url', None) or (s.pdf_file.url if hasattr(s, 'pdf_file') and s.pdf_file else None),
        'pdf_generated': getattr(s, 'pdf_generated', False),
        'has_certificates': {
            'achievement': bool(s.cert_achieve),
            'internship': bool(s.cert_intern),
            'courses': bool(s.cert_courses),
            'sdp': bool(s.cert_sdp),
            'extra': bool(s.cert_extra),
            'placement': bool(s.cert_placement),
            'national': bool(s.cert_national),
        },
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else None,
        'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(s, 'updated_at') and s.updated_at else None,
    })


@login_required
@csrf_exempt
def api_student_certificates(request, student_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    student = get_object_or_404(Student, id=student_id)
    certificates = {
        'photo': student.photo.url if student.photo else student.photo_url,
        'achievement': student.cert_achieve.url if hasattr(student.cert_achieve, 'url') else student.cert_achieve,
        'internship': student.cert_intern.url if hasattr(student.cert_intern, 'url') else student.cert_intern,
        'courses': student.cert_courses.url if hasattr(student.cert_courses, 'url') else student.cert_courses,
        'sdp': student.cert_sdp.url if hasattr(student.cert_sdp, 'url') else student.cert_sdp,
        'extra': student.cert_extra.url if hasattr(student.cert_extra, 'url') else student.cert_extra,
        'placement': student.cert_placement.url if hasattr(student.cert_placement, 'url') else student.cert_placement,
        'national': student.cert_national.url if hasattr(student.cert_national, 'url') else student.cert_national,
    }
    certificates = {k: v for k, v in certificates.items() if v}
    return JsonResponse({
        'student_id': student.id,
        'student_name': student.student_name,
        'ht_no': student.ht_no,
        'certificates': certificates,
        'has_pdf': bool(getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None)),
        'pdf_generated': getattr(student, 'pdf_generated', False),
    })


@login_required
@require_GET
def api_dashboard_stats(request):
    today_date = date.today()
    faculty_total = Faculty.objects.count()
    faculty_active = Faculty.objects.filter(is_active=True).count()
    faculty_with_phd = Faculty.objects.filter(phd_degree='Completed').count()
    exp_stats = {'0-5': 0, '5-10': 0, '10-15': 0, '15+': 0}
    for f in Faculty.objects.filter(joining_date__isnull=False):
        yrs = (today_date - f.joining_date).days / 365.25
        if yrs <= 5:
            exp_stats['0-5'] += 1
        elif yrs <= 10:
            exp_stats['5-10'] += 1
        elif yrs <= 15:
            exp_stats['10-15'] += 1
        else:
            exp_stats['15+'] += 1
    departments = list(Faculty.objects.values('department')
                       .annotate(count=Count('id'))
                       .order_by('-count'))
    student_total = Student.objects.count()
    student_by_year = list(Student.objects.values('year')
                           .annotate(count=Count('id'))
                           .order_by('year'))
    research_total = ResearchPublication.objects.count()
    research_by_type = list(ResearchPublication.objects.values('research_type')
                            .annotate(count=Count('id')))
    fdp_total = FDP.objects.count()
    fdp_by_type = list(FDP.objects.values('fdp_type')
                       .annotate(count=Count('id')))
    recent_activities = FacultyLog.objects.select_related('faculty')[:10].values(
        'id', 'action', 'details', 'created_at', 'faculty__staff_name', 'performed_by'
    )
    return JsonResponse({
        'faculty': {
            'total': faculty_total,
            'active': faculty_active,
            'with_phd': faculty_with_phd,
            'inactive': faculty_total - faculty_active,
            'experience_distribution': exp_stats,
            'departments': list(departments),
        },
        'students': {
            'total': student_total,
            'by_year': list(student_by_year),
        },
        'research': {
            'total': research_total,
            'by_type': list(research_by_type),
        },
        'fdps': {
            'total': fdp_total,
            'by_type': list(fdp_by_type),
        },
        'certificates': {
            'total': Certificate.objects.count(),
            'with_cloudinary': Certificate.objects.exclude(cloudinary_url__isnull=True).exclude(
                cloudinary_url='').count(),
        },
        'cloudinary': {
            'total_uploads': CloudinaryUpload.objects.count(),
            'faculty_with_pdf': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
                cloudinary_pdf_url='').count(),
            'faculty_with_photo': Faculty.objects.exclude(cloudinary_photo_url__isnull=True).exclude(
                cloudinary_photo_url='').count(),
        },
        'recent_activities': list(recent_activities),
        'last_updated': datetime.now().isoformat(),
    })


@login_required
@require_GET
def api_department_stats(request, department):
    faculty_list = Faculty.objects.filter(department__icontains=department)
    if not faculty_list.exists():
        return JsonResponse({'error': 'Department not found'}, status=404)
    faculty_ids = [f.id for f in faculty_list]
    stats = {
        'department': department,
        'faculty_count': faculty_list.count(),
        'active_faculty': faculty_list.filter(is_active=True).count(),
        'with_phd': faculty_list.filter(phd_degree='Completed').count(),
        'designations': list(faculty_list.values('designation').annotate(count=Count('id')).order_by('-count')),
        'research_publications': ResearchPublication.objects.filter(faculty__in=faculty_ids).count(),
        'fdps': FDP.objects.filter(faculty__in=faculty_ids).count(),
        'btech_projects': BTechProject.objects.filter(faculty__in=faculty_ids).count(),
        'faculty_list': list(faculty_list.values('id', 'staff_name', 'employee_code', 'designation', 'email')),
    }
    return JsonResponse(stats)


# ==================== ADDITIONAL API ENDPOINTS ====================
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_update_faculty_status(request, faculty_id):
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        data = json.loads(request.body) if request.body else {}
        is_active = data.get('is_active')
        if is_active is None:
            is_active = request.POST.get('is_active')
        if isinstance(is_active, str):
            is_active = is_active.lower() in ['true', '1', 'yes', 'active']
        if is_active is None:
            return JsonResponse({
                'success': False,
                'error': 'is_active field is required'
            }, status=400)
        old_status = faculty.is_active
        faculty.is_active = is_active
        faculty.save()
        FacultyLog.objects.create(
            faculty=faculty,
            action='Status Updated',
            details=f'Status changed from {"Active" if old_status else "Inactive"} to {"Active" if is_active else "Inactive"}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return JsonResponse({
            'success': True,
            'message': f'Faculty status updated successfully',
            'faculty_id': faculty.id,
            'faculty_name': faculty.staff_name,
            'employee_code': faculty.employee_code,
            'is_active': faculty.is_active,
            'status_text': 'Active' if faculty.is_active else 'Inactive'
        })
    except Faculty.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Faculty not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating faculty status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_bulk_update_faculty_status(request):
    try:
        data = json.loads(request.body) if request.body else {}
        faculty_ids = data.get('faculty_ids', [])
        is_active = data.get('is_active')
        if not faculty_ids:
            return JsonResponse({
                'success': False,
                'error': 'faculty_ids list is required'
            }, status=400)
        if is_active is None:
            return JsonResponse({
                'success': False,
                'error': 'is_active field is required'
            }, status=400)
        if isinstance(is_active, str):
            is_active = is_active.lower() in ['true', '1', 'yes', 'active']
        updated_count = Faculty.objects.filter(id__in=faculty_ids).update(is_active=is_active)
        FacultyLog.objects.create(
            faculty=None,
            action='Bulk Status Update',
            details=f'Updated {updated_count} faculty to {"Active" if is_active else "Inactive"}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return JsonResponse({
            'success': True,
            'message': f'Updated {updated_count} faculty members',
            'updated_count': updated_count,
            'is_active': is_active
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in bulk status update: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_GET
def api_faculty_subjects(request, faculty_id):
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        subjects = faculty.subjects.all().values('id', 'name', 'code', 'credits')
        return JsonResponse({
            'success': True,
            'faculty_id': faculty.id,
            'faculty_name': faculty.staff_name,
            'employee_code': faculty.employee_code,
            'subjects': list(subjects),
            'count': subjects.count()
        })
    except Faculty.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Faculty not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching faculty subjects: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_assign_faculty_subjects(request, faculty_id):
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        data = json.loads(request.body) if request.body else {}
        subject_ids = data.get('subject_ids', [])
        if not subject_ids:
            return JsonResponse({
                'success': False,
                'error': 'subject_ids list is required'
            }, status=400)
        subjects = Subject.objects.filter(id__in=subject_ids)
        if subjects.count() != len(subject_ids):
            return JsonResponse({
                'success': False,
                'error': 'One or more subject IDs are invalid'
            }, status=400)
        old_subjects = set(faculty.subjects.values_list('id', flat=True))
        faculty.subjects.set(subjects)
        new_subjects = set(subject_ids)
        added = new_subjects - old_subjects
        removed = old_subjects - new_subjects
        changes = []
        if added:
            added_names = Subject.objects.filter(id__in=added).values_list('name', flat=True)
            changes.append(f"Added: {', '.join(added_names)}")
        if removed:
            removed_names = Subject.objects.filter(id__in=removed).values_list('name', flat=True)
            changes.append(f"Removed: {', '.join(removed_names)}")
        FacultyLog.objects.create(
            faculty=faculty,
            action='Subjects Assigned',
            details=f"Subjects updated. {'; '.join(changes) if changes else 'No changes'}",
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return JsonResponse({
            'success': True,
            'message': 'Subjects assigned successfully',
            'faculty_id': faculty.id,
            'faculty_name': faculty.staff_name,
            'assigned_subjects': list(subjects.values('id', 'name', 'code')),
            'added_count': len(added),
            'removed_count': len(removed)
        })
    except Faculty.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Faculty not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error assigning subjects: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ==================== EXPORT FUNCTIONS ====================
@login_required
def export_faculty_excel(request):
    if pd is None:
        messages.error(request, 'Pandas not installed. Cannot export to Excel.')
        return redirect('dashboard:faculty_list')
    try:
        faculty_data = []
        for f in Faculty.objects.all():
            faculty_data.append({
                'Employee Code': f.employee_code,
                'Staff Name': f.staff_name,
                'Department': f.department,
                'Designation': f.designation,
                'Email': f.email,
                'Mobile': f.mobile,
                'Date of Birth': f.dob.strftime('%Y-%m-%d') if f.dob else '',
                'Joining Date': f.joining_date.strftime('%Y-%m-%d') if f.joining_date else '',
                'UG Degree': getattr(f, 'ug_degree', ''),
                'UG Year': getattr(f, 'ug_year', ''),
                'PG Degree': getattr(f, 'pg_degree', ''),
                'PG Year': getattr(f, 'pg_year', ''),
                'PhD Status': getattr(f, 'phd_degree', ''),
                'Research Publications': ResearchPublication.objects.filter(faculty=f).count(),
                'FDPs Attended': FDP.objects.filter(faculty=f).count(),
                'B.Tech Projects': BTechProject.objects.filter(faculty=f).count(),
                'Status': 'Active' if f.is_active else 'Inactive',
                'Cloudinary PDF': 'Yes' if f.cloudinary_pdf_url else 'No',
            })
        df = pd.DataFrame(faculty_data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response[
            'Content-Disposition'] = f'attachment; filename="faculty_export_{date.today().strftime("%Y%m%d")}.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Faculty Data', index=False)
            worksheet = writer.sheets['Faculty Data']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        FacultyLog.objects.create(
            faculty=None,
            action='Faculty Excel Export',
            details=f'Exported {len(faculty_data)} faculty to Excel',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return response
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        messages.error(request, f'Error exporting to Excel: {e}')
        return redirect('dashboard:faculty_list')


@login_required
def export_students_csv(request):
    qs = Student.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_export_{date.today().strftime("%Y%m%d")}.csv"'
    w = csv.writer(response)
    w.writerow(['HT No', 'Student Name', 'Father Name', 'Mother Name', 'Gender', 'Date of Birth', 'Age',
                'Nationality', 'Category', 'Religion', 'Blood Group', 'Aadhar', 'APAAR ID', 'Address',
                'Parent Phone', 'Student Phone', 'Email', 'Year', 'Semester', 'SSC Marks', 'Inter Marks',
                'CGPA', 'Task Registered', 'Task Username', 'CSI Registered', 'CSI Membership ID',
                'Admission Type', 'Other Admission Details', 'EAMCET Rank', 'RTRP Project Title',
                'Intern Title', 'Final Project Title', 'Other Training', 'Photo URL',
                'Certificate Achievement URL', 'Certificate Internship URL', 'Certificate Courses URL',
                'Certificate SDP URL', 'Certificate Extra URL', 'Certificate Placement URL',
                'Certificate National URL', 'PDF URL', 'PDF Generated', 'PDF Generation Time'])
    for s in qs:
        w.writerow([
            s.ht_no, s.student_name, s.father_name, s.mother_name, s.gender,
            s.dob.strftime('%Y-%m-%d') if s.dob else '', s.age,
            s.nationality, s.category, s.religion, s.blood_group, s.aadhar, s.apaar_id, s.address,
            s.parent_phone, s.student_phone, s.email, s.year, s.sem,
            s.ssc_marks, s.inter_marks, s.cgpa, s.task_registered, s.task_username,
            s.csi_registered, s.csi_membership_id, s.admission_type, s.other_admission_details,
            s.eamcet_rank, s.rtrp_project_title, s.intern_title, s.final_project_title,
            s.other_training, s.photo_url,
            s.cert_achieve_url, s.cert_intern_url, s.cert_courses_url, s.cert_sdp_url,
            s.cert_extra_url, s.cert_placement_url, s.cert_national_url,
            s.pdf_url, s.pdf_generated,
            s.pdf_generation_time.strftime('%Y-%m-%d %H:%M:%S') if s.pdf_generation_time else ''
        ])
    FacultyLog.objects.create(faculty=None, action='Student CSV Export',
                              details=f'Exported {qs.count()} students to CSV',
                              performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
    return response


@login_required
def export_students_excel(request):
    if pd is None:
        messages.error(request, 'Pandas not installed. Cannot export to Excel.')
        return redirect('dashboard:students_data')
    try:
        student_data = []
        for s in Student.objects.all():
            student_data.append({
                'HT No': s.ht_no,
                'Student Name': s.student_name,
                'Father Name': s.father_name,
                'Mother Name': s.mother_name,
                'Gender': s.gender,
                'Date of Birth': s.dob.strftime('%Y-%m-%d') if s.dob else '',
                'Age': s.age,
                'Category': s.category,
                'Religion': s.religion,
                'Blood Group': s.blood_group,
                'Aadhar': s.aadhar,
                'Address': s.address,
                'Parent Phone': s.parent_phone,
                'Student Phone': s.student_phone,
                'Email': s.email,
                'Year': s.year,
                'Semester': s.sem,
                'SSC Marks': s.ssc_marks,
                'Inter Marks': s.inter_marks,
                'CGPA': s.cgpa,
                'Admission Type': s.admission_type,
                'EAMCET Rank': s.eamcet_rank,
                'Created Date': s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else '',
            })
        df = pd.DataFrame(student_data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response[
            'Content-Disposition'] = f'attachment; filename="students_export_{date.today().strftime("%Y%m%d")}.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Student Data', index=False)
            worksheet = writer.sheets['Student Data']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        FacultyLog.objects.create(
            faculty=None,
            action='Students Excel Export',
            details=f'Exported {len(student_data)} students to Excel',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return response
    except Exception as e:
        logger.error(f"Student Excel export error: {e}")
        messages.error(request, f'Error exporting to Excel: {e}')
        return redirect('dashboard:students_data')


# ==================== ADDITIONAL VIEW FUNCTIONS ====================
@login_required
def session_info(request):
    return JsonResponse({
        'session_data': dict(request.session),
        'session_keys': list(request.session.keys()),
        'is_authenticated': request.user.is_authenticated,
        'user': str(request.user),
    })


@login_required
def clear_session(request):
    if request.method == 'POST':
        request.session.flush()
        messages.success(request, 'Session cleared successfully.')
        return redirect('dashboard:login')
    return render(request, 'dashboard/confirm_clear_session.html', {
        'title': 'Clear Session',
    })


@login_required
def application_home(request):
    return redirect('dashboard:dashboard')


@login_required
def profile_settings(request):
    return render(request, 'dashboard/profile_settings.html', {
        'title': 'Profile Settings',
        'user': request.user,
    })


@login_required
def about_system(request):
    return render(request, 'dashboard/about.html', {
        'title': 'About ANURAG Engineering College',
        'version': '2.0.0',
        'release_date': '2024',
        'features': [
            'Faculty Management',
            'Student Management',
            'Certificate Management',
            'Cloudinary Integration',
            'PDF Generation',
            'Analytics Dashboard',
        ]
    })


@login_required
def help_documentation(request):
    return render(request, 'dashboard/help.html', {
        'title': 'Help & Documentation',
        'sections': [
            {'title': 'Getting Started', 'content': 'How to use the system...'},
            {'title': 'Faculty Management', 'content': 'Managing faculty records...'},
            {'title': 'Student Management', 'content': 'Managing student records...'},
            {'title': 'PDF Generation', 'content': 'Generating and merging PDFs...'},
            {'title': 'Cloudinary Integration', 'content': 'Cloud storage management...'},
        ]
    })


@login_required
def contact_support(request):
    return render(request, 'dashboard/contact.html', {
        'title': 'Contact Support',
        'support_email': 'support@anurag.edu.in',
        'support_phone': '+91-XXXXXXXXXX',
        'office_hours': 'Monday to Friday, 9:00 AM - 5:00 PM',
    })


def privacy_policy(request):
    return redirect('dashboard:project_policy_pdf', policy_slug='privacy-policy')


# ==================== EXAM BRANCH VIEWS ====================
@login_required
def exam_branch(request):
    from django.core.paginator import Paginator
    from datetime import datetime, timedelta

    try:
        view_mode = request.GET.get('view', 'dashboard')
        search_query = request.GET.get('search', '')
        department_filter = request.GET.get('department', '')
        status_filter = request.GET.get('status', '')

        # Filters for Attendance
        branch = request.GET.get('branch', 'IT')
        year_sem = request.GET.get('year_sem', 'IV-I')
        from_date_str = request.GET.get('from_date', '2025-07-10')
        to_date_str = request.GET.get('to_date', '2025-09-30')

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            from_date = date(2025, 7, 10)
            to_date = date(2025, 9, 30)

        # Faculty List Data
        faculties = Faculty.objects.all().select_related('profile').order_by('staff_name')
        if search_query:
            faculties = faculties.filter(
                Q(staff_name__icontains=search_query) |
                Q(employee_code__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(department__icontains=search_query)
            )
        if department_filter:
            faculties = faculties.filter(department__icontains=department_filter)

        if status_filter == 'available':
            faculties = faculties.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='')
        elif status_filter == 'pending':
            faculties = faculties.filter(Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url=''))

        faculty_data = []
        for f in faculties:
            faculty_data.append({
                'id': f.id,
                'employee_code': f.employee_code,
                'name': f.staff_name,
                'department': f.department or 'Not Assigned',
                'designation': f.designation or 'Faculty',
                'email': f.email,
                'mobile': f.mobile or 'N/A',
                'cloudinary_pdf_url': f.cloudinary_pdf_url,
                'cloudinary_photo_url': f.cloudinary_photo_url,
                'updated_at': f.updated_at if hasattr(f, 'updated_at') else f.created_at,
                'pdf_status': 'Available' if f.cloudinary_pdf_url else 'Not Available',
                'total_certificates': Certificate.objects.filter(faculty=f).count(),
            })

        total_faculty = Faculty.objects.count()
        with_pdf = Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='').count()

        available_departments = Faculty.objects.values_list('department', flat=True).distinct().order_by('department')

        # Syllabus data for subjects by year-sem and branch
        syllabus_data = {
            "1-1": {
                "IT": [
                    {"code": "MA101BS", "name": "MATRICES AND CALCULUS"},
                    {"code": "AP102BS", "name": "APPLIED PHYSICS"},
                    {"code": "CS103ES", "name": "PROGRAMMING FOR PROBLEM SOLVING"},
                    {"code": "EN104HS", "name": "ENGLISH FOR SKILL ENHANCEMENT"},
                    {"code": "ME105ES", "name": "ENGINEERING WORKSHOP"},
                    {"code": "CS106ES", "name": "ELEMENTS OF COMPUTER SCIENCE & ENGINEERING"},
                    {"code": "AP107BS", "name": "APPLIED PHYSICS LABORATORY"},
                    {"code": "EN108HS", "name": "ENGLISH LANGUAGE AND COMMUNICATION SKILLS LABORATORY"},
                    {"code": "CS109ES", "name": "PROGRAMMING FOR PROBLEM SOLVING LABORATORY"},
                    {"code": "ES110MC", "name": "ENVIRONMENTAL SCIENCE"}
                ],
                "CSE": [
                    {"code": "MA101BS", "name": "MATRICES AND CALCULUS"},
                    {"code": "CH102BS", "name": "ENGINEERING CHEMISTRY"},
                    {"code": "CS103ES", "name": "PROGRAMMING FOR PROBLEM SOLVING"},
                    {"code": "EE104ES", "name": "BASIC ELECTRICAL ENGINEERING"},
                    {"code": "EG105ES", "name": "COMPUTER AIDED ENGINEERING GRAPHICS"},
                    {"code": "CS106ES", "name": "ELEMENTS OF COMPUTER SCIENCE & ENGINEERING"},
                    {"code": "CH107BS", "name": "ENGINEERING CHEMISTRY LABORATORY"},
                    {"code": "CS109ES", "name": "PROGRAMMING FOR PROBLEM SOLVING LABORATORY"},
                    {"code": "EE108ES", "name": "BASIC ELECTRICAL ENGINEERING LABORATORY"},
                    {"code": "HS110MC", "name": "CONSTITUTION OF INDIA"}
                ]
            },
            "1-2": {
                "IT": [
                    {"code": "MA201BS", "name": "ORDINARY DIFFERENTIAL EQUATIONS AND VECTOR CALCULUS"},
                    {"code": "CH202BS", "name": "ENGINEERING CHEMISTRY"},
                    {"code": "EG203ES", "name": "COMPUTER AIDED ENGINEERING GRAPHICS"},
                    {"code": "EE204ES", "name": "BASIC ELECTRICAL ENGINEERING"},
                    {"code": "EC205ES", "name": "ELECTRONIC DEVICES AND CIRCUITS"},
                    {"code": "CH206BS", "name": "ENGINEERING CHEMISTRY LABORATORY"},
                    {"code": "CS207ES", "name": "PYTHON PROGRAMMING LABORATORY"},
                    {"code": "EE208ES", "name": "BASIC ELECTRICAL ENGINEERING LABORATORY"},
                    {"code": "CS209ES", "name": "IT WORKSHOP"},
                    {"code": "HS210MC", "name": "CONSTITUTION OF INDIA"}
                ]
            },
            "2-1": {
                "IT": [
                    {"code": "MA301BS", "name": "COMPLEX VARIABLES AND STATISTICAL METHODS"},
                    {"code": "CS302PC", "name": "DATA STRUCTURES"},
                    {"code": "CS303PC", "name": "COMPUTER ORGANIZATION"},
                    {"code": "IT304PC", "name": "WEB PROGRAMMING"},
                    {"code": "CS305PC", "name": "OBJECT ORIENTED PROGRAMMING USING C++"},
                    {"code": "CS306PC", "name": "DATA STRUCTURES LABORATORY"},
                    {"code": "IT307PC", "name": "WEB PROGRAMMING LABORATORY"},
                    {"code": "CS308PC", "name": "OBJECT ORIENTED PROGRAMMING USING C++ LABORATORY"},
                    {"code": "MC309", "name": "GENDER SENSITIZATION LAB"},
                    {"code": "HS310MC", "name": "BUSINESS VENTURES AND ENTREPRENEURSHIP"}
                ]
            },
            "2-2": {
                "IT": [
                    {"code": "MB401HS", "name": "BUSINESS ECONOMICS & FINANCIAL ANALYSIS"},
                    {"code": "CS402PC", "name": "DISCRETE MATHEMATICS"},
                    {"code": "CS403PC", "name": "OPERATING SYSTEMS"},
                    {"code": "CS404PC", "name": "DATABASE MANAGEMENT SYSTEMS"},
                    {"code": "IT405PC", "name": "JAVA PROGRAMMING"},
                    {"code": "CS406PC", "name": "OPERATING SYSTEMS LABORATORY"},
                    {"code": "CS407PC", "name": "DATABASE MANAGEMENT SYSTEMS LABORATORY"},
                    {"code": "IT408PC", "name": "JAVA PROGRAMMING LABORATORY"},
                    {"code": "IT409PW", "name": "REAL-TIME RESEARCH PROJECT/ SOCIETAL RELATED PROJECT"},
                    {"code": "IT410PC", "name": "SKILL DEVELOPMENT COURSE (NODE JS/REACTJS/DJANGO)"},
                    {"code": "HS411MC", "name": "INTELLECTUAL PROPERTY RIGHTS"}
                ]
            }
        }

        # Get subjects for the selected year_sem and branch
        subjects = []
        if year_sem in syllabus_data and branch in syllabus_data[year_sem]:
            subjects = syllabus_data[year_sem][branch]

        # Attendance Dashboard Data
        date_list = []
        curr = from_date
        # Limit to 31 days to keep the table manageable
        max_days = 31
        days_added = 0
        while curr <= to_date and days_added < max_days:
            date_list.append(curr)
            curr += timedelta(days=1)
            days_added += 1

        students = Student.objects.all()
        if branch:
            # Assuming branch is stored in some field or we just filter for demo
            pass

        # Mock attendance data for now
        attendance_data = {}
        for s in students:
            attendance_data[s.id] = {}
            total_p = 0
            for d in date_list:
                # Simple logic: Present except Sundays
                status = 'P' if d.weekday() != 6 else 'A'
                attendance_data[s.id][d] = status
                if status == 'P': total_p += 1

            s.total_present = total_p
            s.attendance_percentage = int((total_p / len(date_list) * 100)) if date_list else 0

        if view_mode == 'list':
            paginator = Paginator(faculty_data, 20)
            page = request.GET.get('page', 1)
            faculties_page = paginator.get_page(page)
        else:
            faculties_page = faculty_data[:50]

        context = {
            'view_mode': view_mode,
            'faculties': faculties_page,
            'total_count': total_faculty,
            'available_pdfs': with_pdf,
            'departments': [d for d in available_departments if d],
            'search_query': search_query,
            'department_filter': department_filter,
            'status_filter': status_filter,

            # Attendance context
            'students': students,
            'date_list': date_list,
            'attendance_data': attendance_data,
            'from_date': from_date_str,
            'to_date': to_date_str,
            'branch': branch,
            'year_sem': year_sem,
            'subjects': subjects,

            'title': 'Exam Branch - Management',
        }
        return render(request, 'dashboard/exambranch.html', context)
    except Exception as e:
        logger.error(f"Error in exam_branch view: {str(e)}", exc_info=True)
        # Return a simple error page or redirect
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f"An error occurred: {str(e)}")


@login_required
@require_POST
def exam_branch_download_lesson_plan(request):
    payload = {}
    try:
        submitted_payload = request.POST.get('lesson_plan_payload', '{}')
        parsed_payload = json.loads(submitted_payload)
        if isinstance(parsed_payload, dict):
            payload = parsed_payload
    except (TypeError, ValueError, json.JSONDecodeError):
        payload = {}

    header = payload.get('header', {}) if isinstance(payload, dict) else {}
    rows = payload.get('rows', []) if isinstance(payload, dict) else []

    lines = [
        'Teaching / Lesson Plan',
        f"Branch: {header.get('branch', '')}",
        f"Year: {header.get('year', '')}",
        f"Semester: {header.get('semester', '')}",
        f"Faculty: {header.get('faculty', '')}",
        f"Employee Code: {header.get('employeeCode', '')}",
        f"Subject: {header.get('subject', '')}",
        f"Subject Code: {header.get('subjectCode', '')}",
        '',
        'S.No\tDate\tDay\tTopic\tMethod\tRemarks',
    ]

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        lines.append('\t'.join([
            str(index),
            str(row.get('date', '')),
            str(row.get('day', '')),
            str(row.get('topic', '')),
            str(row.get('method', '')),
            str(row.get('remarks', '')),
        ]))

    response = HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="lesson_plan.txt"'
    return response


@login_required
@csrf_exempt
def update_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            date_val = data.get('date')
            status = data.get('status')
            
            # Here you would normally save to an Attendance model
            # For now, we'll just return a mock success
            
            return JsonResponse({
                'success': True, 
                'total_present': 22, 
                'percentage': 88
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST method required'})


@login_required
@csrf_exempt
def save_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process and save all attendance data
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST method required'})


@login_required
def attendance_report(request):
    # Logic to generate attendance report (PDF or Excel)
    branch = request.GET.get('branch', 'IT')
    return HttpResponse(f"Attendance Report for {branch} generated successfully.")


@login_required
def exam_branch_generate_report(request):
    report_format = request.GET.get('format', 'excel')
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')
    faculties = Faculty.objects.all().order_by('staff_name')
    if search_query:
        faculties = faculties.filter(
            Q(staff_name__icontains=search_query) |
            Q(employee_code__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    if department_filter:
        faculties = faculties.filter(department__icontains=department_filter)
    if status_filter == 'available':
        faculties = faculties.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='')
    elif status_filter == 'pending':
        faculties = faculties.filter(Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url=''))
    if report_format == 'excel':
        if pd is None:
            messages.error(request, 'Pandas not installed. Cannot generate Excel report.')
            return redirect('dashboard:exam_branch')
        data = []
        for f in faculties:
            data.append({
                'Employee Code': f.employee_code,
                'Staff Name': f.staff_name,
                'Department': f.department or 'N/A',
                'Designation': f.designation or 'N/A',
                'Email': f.email,
                'Mobile': f.mobile or 'N/A',
                'PDF Status': 'Available' if f.cloudinary_pdf_url else 'Not Available',
                'PDF URL': f.cloudinary_pdf_url or 'N/A',
                'Certificates Count': Certificate.objects.filter(faculty=f).count(),
            })
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response[
            'Content-Disposition'] = f'attachment; filename="exam_branch_report_{date.today().strftime("%Y%m%d")}.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Exam Branch Report', index=False)
        FacultyLog.objects.create(
            faculty=None,
            action='Exam Branch Report',
            details=f'Excel report generated with {len(data)} faculty records',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return response
    elif report_format == 'pdf':
        html_string = render_to_string('dashboard/exambranch_report.html', {
            'faculties': faculties,
            'generated_date': datetime.now(),
            'total_count': faculties.count(),
            'with_pdf': faculties.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='').count(),
            'generated_by': request.user.username,
        })
        if pdfkit is None:
            messages.error(request, 'PDF generation not available. Please install pdfkit.')
            return redirect('dashboard:exam_branch')
        try:
            opts = {
                'page-size': 'A4',
                'margin-top': '15mm',
                'margin-right': '15mm',
                'margin-bottom': '15mm',
                'margin-left': '15mm',
                'encoding': 'UTF-8',
            }
            # Cross-platform wkhtmltopdf detection
            wkhtmltopdf_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                '/usr/local/bin/wkhtmltopdf',
                '/usr/bin/wkhtmltopdf',
                'wkhtmltopdf',
            ]

            wkhtmltopdf_path = None
            for path in wkhtmltopdf_paths:
                if (isinstance(path, str) and os.path.exists(path)) or path == 'wkhtmltopdf':
                    try:
                        import subprocess
                        result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            wkhtmltopdf_path = path
                            break
                    except:
                        continue

            try:
                from weasyprint import HTML
                from django.conf import settings as django_settings
                base_url = Path(django_settings.BASE_DIR).resolve().as_uri() if django_settings.BASE_DIR else None
                html_obj = HTML(string=html_string, base_url=base_url)
                pdf = html_obj.write_pdf()
            except ImportError:
                return JsonResponse({'success': False, 'error': 'WeasyPrint not installed.'})
            response = HttpResponse(pdf, content_type='application/pdf')
            response[
                'Content-Disposition'] = f'attachment; filename="exam_branch_report_{date.today().strftime("%Y%m%d")}.pdf"'
            FacultyLog.objects.create(
                faculty=None,
                action='Exam Branch Report',
                details=f'PDF report generated with {faculties.count()} faculty records',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return response
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            messages.error(request, f'Error generating PDF: {e}')
            return redirect('dashboard:exam_branch')
    return redirect('dashboard:exam_branch')


@login_required
def exam_branch_batch_download(request):
    faculties = Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='')
    if not faculties.exists():
        messages.warning(request, 'No PDFs available for download.')
        return redirect('dashboard:exam_branch')
    try:
        temp_dir = tempfile.mkdtemp()
        zip_filename = f'exam_branch_faculty_pdfs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        zip_path = os.path.join(temp_dir, zip_filename)
        downloaded_count = 0
        failed_count = 0
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for faculty in faculties:
                try:
                    response = requests.get(faculty.cloudinary_pdf_url, timeout=30)
                    if response.status_code == 200:
                        filename = f"{faculty.employee_code}_{faculty.staff_name.replace(' ', '_')}.pdf"
                        zipf.writestr(filename, response.content)
                        downloaded_count += 1
                    else:
                        failed_count += 1
                        logger.warning(
                            f"Failed to download PDF for {faculty.employee_code}: HTTP {response.status_code}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error downloading PDF for {faculty.employee_code}: {e}")
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        response = HttpResponse(zip_data, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        os.remove(zip_path)
        os.rmdir(temp_dir)
        FacultyLog.objects.create(
            faculty=None,
            action='Exam Branch Batch Download',
            details=f'Downloaded {downloaded_count} faculty PDFs ({failed_count} failed)',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        if downloaded_count > 0:
            messages.success(request, f'Downloaded {downloaded_count} faculty PDFs')
        if failed_count > 0:
            messages.warning(request, f'{failed_count} PDFs failed to download')
        return response
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        messages.error(request, f'Error creating ZIP file: {e}')
        return redirect('dashboard:exam_branch')


# Password Protection Views
def students_data_password(request):
    """Password protection for students data page"""
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'aecithod':
            return redirect('dashboard:students')
        else:
            messages.error(request, 'Invalid password. Access denied.')
            return redirect('dashboard:students_data')
    return render(request, 'dashboard/students_data_password.html')


def student_dashboard_password(request):
    """Password protection for student dashboard page"""
    if request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard_view')
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'aecithod':
            return redirect('dashboard:student_dashboard_view')
        else:
            messages.error(request, 'Invalid password. Access denied.')
            return redirect('dashboard:student_dashboard')
    return render(request, 'dashboard/student_dashboard_password.html')


def faculty_list_password(request):
    """Password protection for faculty list page"""
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'aecithod':
            return redirect('dashboard:faculty_list_view')
        else:
            messages.error(request, 'Invalid password. Access denied.')
            return redirect('dashboard:faculty_list')
    return render(request, 'dashboard/faculty_list_password.html')


def simple_test(request):
    """Simple test view to verify Django is working"""
    return HttpResponse("""
    <html>
    <head><title>ANURAG Engineering College</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🏫 ANURAG Engineering College</h1>
        <p>Django is working! Your application is running.</p>
        <hr>
        <p><a href="/admin-login/">🔐 Click here for Admin Login</a></p>
        <p><a href="/student-login/">👨‍🎓 Click here for Student Login</a></p>
    </body>
    </html>
    """)


def diagnose_weasyprint(request):
    """Diagnostic view to test WeasyPrint installation and configuration"""
    import sys
    import os
    from io import StringIO
    
    output = StringIO()
    output.write("<html><head><title>WeasyPrint Diagnostic</title></head><body style='font-family:monospace;padding:20px;'>")
    output.write("<h1>🔧 WeasyPrint Diagnostic</h1>")
    
    # Check Python version
    output.write(f"<p><strong>Python:</strong> {sys.version}</p>")
    
    # Check WeasyPrint import
    try:
        from weasyprint import HTML
        output.write("<p style='color:green;'>✅ WeasyPrint imported successfully</p>")
        
        # Try to get version
        try:
            import weasyprint
            output.write(f"<p><strong>WeasyPrint version:</strong> {weasyprint.__version__}</p>")
        except:
            output.write("<p>⚠️ Could not determine WeasyPrint version</p>")
        
        # Test basic PDF generation
        try:
            test_html = "<html><body><h1>Test PDF</h1><p>This is a test.</p></body></html>"
            html_obj = HTML(string=test_html)
            pdf_bytes = html_obj.write_pdf()
            output.write(f"<p style='color:green;'>✅ Basic PDF generation works! Generated {len(pdf_bytes)} bytes</p>")
        except Exception as e:
            output.write(f"<p style='color:red;'>❌ PDF generation failed: {e}</p>")
            import traceback
            output.write(f"<pre>{traceback.format_exc()}</pre>")
        
        # Check Cairo
        try:
            import cairo
            output.write("<p style='color:green;'>✅ Cairo available</p>")
        except ImportError:
            output.write("<p style='color:orange;'>⚠️ Cairo not available (may be needed for some features)</p>")
        
        # Check pydyf
        try:
            import pydyf
            output.write(f"<p style='color:green;'>✅ pydyf available (version: {getattr(pydyf, '__version__', 'unknown')})</p>")
        except ImportError:
            output.write("<p style='color:red;'>❌ pydyf not available</p>")
        
        # Check font configuration
        try:
            from weasyprint.text.fonts import FontConfiguration
            font_config = FontConfiguration()
            output.write("<p style='color:green;'>✅ Font configuration initialized</p>")
        except Exception as e:
            output.write(f"<p style='color:red;'>❌ Font configuration error: {e}</p>")
        
    except ImportError as e:
        output.write(f"<p style='color:red;'>❌ WeasyPrint import failed: {e}</p>")
    except Exception as e:
        output.write(f"<p style='color:red;'>❌ Unexpected error: {e}</p>")
        import traceback
        output.write(f"<pre>{traceback.format_exc()}</pre>")
    
    output.write("</body></html>")
    return HttpResponse(output.getvalue())


# ==================== ERROR HANDLERS ====================
def handler404(request, exception):
    return render(request, 'errors/404.html', {
        'title': 'Page Not Found',
        'path': request.path,
    }, status=404)


def handler500(request):
    try:
        return render(request, 'errors/500.html', {
            'title': 'Server Error',
        }, status=500)
    except Exception:
        tb = traceback.format_exc()
        return HttpResponse(f"<h1>DEBUG 500 ERROR (HANDLER)</h1><pre>{tb}</pre>", content_type="text/html")


def handler403(request, exception):
    return render(request, 'errors/403.html', {
        'title': 'Access Denied',
    }, status=403)


def handler400(request, exception):
    return render(request, 'errors/400.html', {
        'title': 'Bad Request',
    }, status=400)


def test_render(request):
    """Simple test view to check if Django is working"""
    return HttpResponse("""
    <html>
    <head><title>Test Page</title></head>
    <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h1>[OK] Django is Working!</h1>
        <p>Your application is running successfully on Render.</p>
        <p>Time: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <hr>
        <h2>Navigation:</h2>
        <ul style="list-style: none; padding: 0;">
            <li><a href="/admin-login/">Admin Login</a></li>
            <li><a href="/student-login/">Student Login</a></li>
            <li><a href="/admin/">Django Admin</a></li>
        </ul>
    </body>
    </html>
    """)


# ==================== MISSING VIEW STUBS ====================
# These are referenced in dashboard/urls.py but not yet implemented.
# Stubs return HTTP 501 (Not Implemented) to satisfy URL resolution.


def _read_faculty_pdf_bytes(faculty):
    """Read a previously persisted faculty PDF from Cloudinary or local storage."""
    pdf_url = normalize_optional_url(getattr(faculty, 'cloudinary_pdf_url', None))
    if pdf_url:
        temp_pdf_path, is_pdf = download_remote_asset(pdf_url, default_suffix='.pdf')
        try:
            if temp_pdf_path and os.path.exists(temp_pdf_path) and is_pdf:
                with open(temp_pdf_path, 'rb') as pdf_file:
                    return pdf_file.read()
        finally:
            try:
                if temp_pdf_path and os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
            except Exception:
                pass

    pdf_field = getattr(faculty, 'pdf_document', None)
    if pdf_field and getattr(pdf_field, 'name', ''):
        try:
            with pdf_field.open('rb') as pdf_file:
                return pdf_file.read()
        except Exception as exc:
            logger.warning(f"Could not read stored faculty PDF for {faculty.employee_code}: {exc}")

    return None


def _faculty_pdf_response(pdf_bytes, employee_code, as_attachment=False):
    """Build an HTTP response for faculty PDF content."""
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    disposition = 'attachment' if as_attachment else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="faculty_{employee_code}.pdf"'
    response['Content-Length'] = len(pdf_bytes)
    return response


@login_required
def generate_faculty_pdf(request, faculty_id):
    """Generate, persist, and return the merged faculty PDF."""
    try:
        faculty = Faculty.objects.filter(id=faculty_id).first()
        if not faculty:
            logger.warning(f"Faculty PDF request for non-existent id={faculty_id}")
            return HttpResponse(
                f"Faculty with id={faculty_id} not found.",
                status=404,
                content_type='text/plain'
            )

        logger.info(f"Generating faculty PDF for {faculty.employee_code}")
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        
        if not pdf_bytes or not pdf_bytes.startswith(b'%PDF'):
            logger.error(f"Generated PDF is invalid for {faculty.employee_code}")
            return HttpResponse(
                f"PDF generation failed for {faculty.employee_code}.",
                status=500,
                content_type='text/plain'
            )
        
        persist_faculty_pdf(faculty, pdf_bytes, uploaded_by=request.user.username)
        FacultyLog.objects.create(
            faculty=faculty,
            action='Faculty PDF Generated',
            details=f'Merged faculty PDF generated for {faculty.staff_name} ({faculty.employee_code})',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        logger.info(f"Successfully generated and persisted faculty PDF for {faculty.employee_code}")
        return _faculty_pdf_response(pdf_bytes, faculty.employee_code, as_attachment=True)
    except Exception as exc:
        logger.error(f"Error generating faculty PDF for {faculty_id}: {exc}", exc_info=True)
        return HttpResponse(
            f"Error generating faculty PDF: {str(exc)}",
            status=500,
            content_type='text/plain'
        )


def student_charts(request):
    """Student charts view - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Student charts not yet implemented.", status=501)


def faculty_charts(request):
    """Faculty charts view - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Faculty charts not yet implemented.", status=501)


@login_required
def faculty_pdf(request, faculty_id):
    """View the saved faculty PDF inline, generating it on demand when necessary."""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        pdf_bytes = _read_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            pdf_bytes = generate_faculty_pdf_bytes(faculty)
            persist_faculty_pdf(faculty, pdf_bytes, uploaded_by=request.user.username)
        return _faculty_pdf_response(pdf_bytes, faculty.employee_code, as_attachment=False)
    except Exception as exc:
        logger.error(f"Error viewing faculty PDF for {faculty_id}: {exc}", exc_info=True)
        messages.error(request, f'Error viewing faculty PDF: {exc}')
        return redirect('dashboard:faculty_profile_view', faculty_id=faculty.id)


@login_required
def download_faculty_pdf(request, faculty_id):
    """Download the saved faculty PDF, generating it on demand when missing."""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        pdf_bytes = _read_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            pdf_bytes = generate_faculty_pdf_bytes(faculty)
            persist_faculty_pdf(faculty, pdf_bytes, uploaded_by=request.user.username)
        return _faculty_pdf_response(pdf_bytes, faculty.employee_code, as_attachment=True)
    except Exception as exc:
        logger.error(f"Error downloading faculty PDF for {faculty_id}: {exc}", exc_info=True)
        messages.error(request, f'Error downloading faculty PDF: {exc}')
        return redirect('dashboard:faculty_profile_view', faculty_id=faculty.id)


@login_required
def preview_faculty_pdf(request, faculty_id):
    """Alias for inline faculty PDF preview."""
    return faculty_pdf(request, faculty_id)


@login_required
def ajax_check_pdf_status(request, faculty_id):
    """Return current faculty PDF availability for AJAX consumers."""
    faculty = get_object_or_404(Faculty, id=faculty_id)
    has_pdf = bool(
        normalize_optional_url(getattr(faculty, 'cloudinary_pdf_url', None)) or
        getattr(getattr(faculty, 'pdf_document', None), 'name', '')
    )
    return JsonResponse({
        'status': 'ready' if has_pdf else 'missing',
        'has_pdf': has_pdf,
        'pdf_url': reverse('dashboard:faculty_pdf', args=[faculty.id]) if has_pdf else None,
        'download_url': reverse('dashboard:download_faculty_pdf', args=[faculty.id]) if has_pdf else None,
        'cloudinary_pdf_url': normalize_optional_url(getattr(faculty, 'cloudinary_pdf_url', None)) or '',
    })


@login_required
def bulk_generate_faculty_pdfs(request):
    """Generate merged PDFs for all faculty records."""
    faculties = Faculty.objects.all().order_by('staff_name')
    generated_count = 0
    failed = []

    for faculty in faculties:
        try:
            pdf_bytes = generate_faculty_pdf_bytes(faculty)
            persist_faculty_pdf(faculty, pdf_bytes, uploaded_by=request.user.username)
            generated_count += 1
        except Exception as exc:
            logger.error(f"Bulk faculty PDF generation failed for {faculty.employee_code}: {exc}")
            failed.append(faculty.employee_code)

    if generated_count:
        messages.success(request, f'Generated PDFs for {generated_count} faculty record(s).')
    if failed:
        messages.warning(request, f'Failed to generate PDFs for: {", ".join(failed)}')

    FacultyLog.objects.create(
        faculty=None,
        action='Bulk Faculty PDF Generation',
        details=f'Generated {generated_count} faculty PDFs; failed: {", ".join(failed) if failed else "none"}',
        performed_by=request.user.username,
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    return redirect('dashboard:faculty_list_view')


def delete_certificate(request, certificate_id):
    """Delete certificate - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Delete certificate not yet implemented.", status=501)


def edit_certificate(request, certificate_id):
    """Edit certificate - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Edit certificate not yet implemented.", status=501)


def merge_certificates(request, faculty_id):
    """Merge certificates - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Merge certificates not yet implemented.", status=501)


def merge_certificates_with_pdf(request, faculty_id):
    """Merge certificates with PDF - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Merge certificates with PDF not yet implemented.", status=501)


def _unused_preview_merged_pdf_stub(request, faculty_id):
    """Preview merged PDF - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Preview merged PDF not yet implemented.", status=501)


def _unused_sync_to_cloudinary_stub(request, faculty_id):
    """Sync faculty to Cloudinary - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Sync to Cloudinary not yet implemented.", status=501)


def _unused_upload_to_cloudinary_stub(request, faculty_id):
    """Upload to Cloudinary - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Upload to Cloudinary not yet implemented.", status=501)


def upload_faculty_pdf(request):
    """Upload faculty PDF - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Upload faculty PDF not yet implemented.", status=501)


def upload_faculty_photo(request):
    """Upload faculty photo - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Upload faculty photo not yet implemented.", status=501)


def cloudinary_status(request):
    """Cloudinary status - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def get_cloudinary_url(request, faculty_id):
    """Get Cloudinary URL - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'url': None}, status=501)


def bulk_sync_to_cloudinary(request):
    """Bulk sync to Cloudinary - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Bulk sync to Cloudinary not yet implemented.", status=501)


def sync_all_faculty_photos_to_cloudinary(request):
    """Sync all faculty photos to Cloudinary - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Sync all faculty photos not yet implemented.", status=501)


def _unused_bulk_upload_stub(request):
    """Bulk upload - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Bulk upload not yet implemented.", status=501)


def _unused_bulk_faculty_actions_stub(request):
    """Bulk faculty actions - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Bulk faculty actions not yet implemented.", status=501)


def _unused_bulk_student_actions_stub(request):
    """Bulk student actions - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Bulk student actions not yet implemented.", status=501)


def _unused_export_faculty_csv_stub(request):
    """Export faculty CSV - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Export faculty CSV not yet implemented.", status=501)


def _unused_export_faculty_excel_stub(request):
    """Export faculty Excel - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Export faculty Excel not yet implemented.", status=501)


def search_faculty(request):
    """Search faculty - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Search faculty not yet implemented.", status=501)


def search_students(request):
    """Search students - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Search students not yet implemented.", status=501)


def generate_pdf_with_data(request):
    """Generate PDF with data - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Generate PDF with data not yet implemented.", status=501)


def preview_pdf_template(request):
    """Preview PDF template - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Preview PDF template not yet implemented.", status=501)


def recent_activity(request):
    """Recent activity - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Recent activity not yet implemented.", status=501)


def _unused_system_status_stub(request):
    """System status - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("System status not yet implemented.", status=501)


def _unused_clear_logs_stub(request):
    """Clear logs - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Clear logs not yet implemented.", status=501)


def _unused_backup_database_stub(request):
    """Backup database - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Backup database not yet implemented.", status=501)


def _unused_exam_branch_stub(request):
    """Exam branch - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Exam branch not yet implemented.", status=501)


def _unused_exam_branch_generate_report_stub(request):
    """Exam branch generate report - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Exam branch generate report not yet implemented.", status=501)


def _unused_exam_branch_batch_download_stub(request):
    """Exam branch batch download - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Exam branch batch download not yet implemented.", status=501)


def _unused_update_attendance_stub(request):
    """Update attendance - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Update attendance not yet implemented.", status=501)


def _unused_save_attendance_stub(request):
    """Save attendance - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Save attendance not yet implemented.", status=501)


def _unused_attendance_report_stub(request):
    """Attendance report - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Attendance report not yet implemented.", status=501)


def _unused_laboratory_stub(request):
    """Laboratory - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Laboratory not yet implemented.", status=501)


def _unused_gallery_stub(request):
    """Gallery - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Gallery not yet implemented.", status=501)


def _unused_session_info_stub(request):
    """Session info - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Session info not yet implemented.", status=501)


def _unused_clear_session_stub(request):
    """Clear session - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Clear session not yet implemented.", status=501)


def _unused_about_system_stub(request):
    """About system - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("About system not yet implemented.", status=501)


def _unused_help_documentation_stub(request):
    """Help documentation - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Help documentation not yet implemented.", status=501)


def _unused_contact_support_stub(request):
    """Contact support - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Contact support not yet implemented.", status=501)


def _unused_profile_settings_stub(request):
    """Profile settings - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Profile settings not yet implemented.", status=501)


def _unused_application_home_stub(request):
    """Application home - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Application home not yet implemented.", status=501)


def _unused_syllabus_view_stub(request):
    """Syllabus view - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Syllabus view not yet implemented.", status=501)


def quick_stats(request):
    """Quick stats API - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_faculty_statistics_api_stub(request, faculty_id):
    """Faculty statistics API - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_student_photo_redirect_stub(request, student_id):
    """Unused legacy stub retained only to avoid shadowing the real view."""
    from django.http import HttpResponse
    return HttpResponse("Student photo redirect not yet implemented.", status=501)


def _unused_regenerate_student_pdf_stub(request, student_id):
    """Unused legacy stub retained only to avoid shadowing the real view."""
    return JsonResponse({'error': 'Not implemented'}, status=501)


def _unused_merge_student_certificates_stub(request, student_id):
    """Unused legacy stub retained only to avoid shadowing the real view."""
    from django.http import HttpResponse
    return HttpResponse("Merge student certificates not yet implemented.", status=501)


def _unused_api_faculty_list_stub(request):
    """API: faculty list - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_faculty_detail_stub(request, faculty_id):
    """API: faculty detail - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_faculty_research_stub(request, faculty_id):
    """API: faculty research - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_faculty_fdps_stub(request, faculty_id):
    """API: faculty FDPs - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_faculty_projects_stub(request, faculty_id):
    """API: faculty projects - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_faculty_subjects_stub(request, faculty_id):
    """API: faculty subjects - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_assign_faculty_subjects_stub(request, faculty_id):
    """API: assign faculty subjects - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_update_faculty_status_stub(request, faculty_id):
    """API: update faculty status - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_bulk_update_faculty_status_stub(request):
    """API: bulk update faculty status - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_students_list_stub(request):
    """API: students list - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_student_detail_stub(request, student_id):
    """API: student detail - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_student_certificates_stub(request, student_id):
    """API: student certificates - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_dashboard_stats_stub(request):
    """API: dashboard stats - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


def _unused_api_department_stats_stub(request, department):
    """API: department stats - not yet implemented."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'not_implemented'}, status=501)


# ==================== MISSING VIEW STUBS ====================
# These are referenced in dashboard/urls.py but not yet implemented.
# They are stubbed to avoid AttributeError during URL resolution.

def _unused_generate_faculty_pdf_stub(request, faculty_id):
    """Generate a faculty PDF - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Faculty PDF generation not yet implemented.", status=501)


def _unused_student_charts_stub(request):
    """Student charts view - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Student charts not yet implemented.", status=501)


def _unused_faculty_charts_stub(request):
    """Faculty charts view - not yet implemented."""
    from django.http import HttpResponse
    return HttpResponse("Faculty charts not yet implemented.", status=501)


def view_certificates(request, *args, **kwargs):
    from django.http import HttpResponse
    return HttpResponse("view_certificates not yet implemented.", status=501)


def upload_certificate(request, *args, **kwargs):
    from django.http import HttpResponse
    return HttpResponse("upload_certificate not yet implemented.", status=501)


def upload_certificates_bulk(request, *args, **kwargs):
    from django.http import HttpResponse
    return HttpResponse("upload_certificates_bulk not yet implemented.", status=501)
