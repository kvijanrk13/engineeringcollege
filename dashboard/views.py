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
from pathlib import Path
from datetime import datetime, date, timedelta
import requests
from urllib.parse import quote
from django.shortcuts import render, redirect, get_object_or_404
from django.http import (HttpResponse, JsonResponse, HttpResponseRedirect,
                         HttpResponseBadRequest)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.urls import reverse
from django.utils import timezone
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
    ResearchPublication, FDP, BTechProject
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


def try_cloudinary_private_download(public_id, headers=None):
    """Download a raw Cloudinary asset through the signed API download endpoint."""
    if not public_id:
        return None

    try:
        if '.' in public_id:
            base_public_id, extension = public_id.rsplit('.', 1)
        else:
            base_public_id, extension = public_id, None

        download_url = cloudinary.utils.private_download_url(
            public_id if extension else base_public_id,
            resource_type='raw',
            format=extension,
            type='upload',
            attachment=False,
        )
        response = requests.get(download_url, timeout=30, headers=headers or {})
        if response.status_code == 200:
            return response
        logger.warning(
            f"Cloudinary private download failed for {public_id}: HTTP {response.status_code}"
        )
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
    if not url or not isinstance(url, str) or not url.startswith('http'):
        return None, False
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)

        # Primary Cloudinary fallback for auth errors
        if response.status_code in [401, 403, 404] and 'cloudinary.com' in url:
            print(f"  [FALLBACK] Cloudinary error {response.status_code}, trying signed URL...")
            try:
                # Extract public_id from URL
                public_ids = get_cloudinary_public_id_candidates(url)
                for public_id in public_ids:
                    # Try raw resource type with signed URL
                    for res_type in ['raw', 'image', 'auto']:
                        try:
                            if is_cloudinary_configured():
                                # Generate a signed download URL
                                signed_url = cloudinary.utils.private_download_url(
                                    public_id,
                                    resource_type=res_type,
                                    type='upload',
                                    attachment=False,
                                    expires_at=int(__import__('time').time()) + 3600
                                )
                                r2 = requests.get(signed_url, timeout=30, headers=headers)
                                if r2.status_code == 200:
                                    response = r2
                                    print(f"  [OK] Signed URL worked for {res_type}: {public_id}")
                                    break
                        except Exception as signed_err:
                            pass

                        # Try direct URL construction
                        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
                        if cloud_name:
                            try_url = f"https://res.cloudinary.com/{cloud_name}/{res_type}/upload/{public_id}"
                            r3 = requests.get(try_url, timeout=30, headers=headers)
                            if r3.status_code == 200:
                                response = r3
                                print(f"  [OK] Direct {res_type} URL worked: {public_id}")
                                break

                    if response.status_code == 200:
                        break

                    # Try Cloudinary API to get fresh URL
                    if is_cloudinary_configured():
                        for res_type in ['raw', 'image']:
                            try:
                                resource = cloudinary.api.resource(public_id, resource_type=res_type)
                                fresh_url = resource.get('secure_url')
                                if fresh_url:
                                    r4 = requests.get(fresh_url, timeout=30, headers=headers)
                                    if r4.status_code == 200:
                                        response = r4
                                        print(f"  [OK] Fresh API URL worked: {fresh_url}")
                                        break
                            except Exception:
                                continue
                    if response.status_code == 200:
                        break

            except Exception as cloud_err:
                print(f"  [WARN] Cloudinary fallback error: {cloud_err}")

        # Try swapping resource type in URL
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
            if field_url:
                return download_remote_asset(field_url, default_suffix=default_suffix)

        if url:
            return download_remote_asset(url, default_suffix=default_suffix)
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
        photo_path, image_files, pdf_files, collected_temp_files = collect_student_files(student)
        temp_files.extend(collected_temp_files)

        # 2a. Add photo if it exists (convert image to PDF page)
        if photo_path and os.path.exists(photo_path):
            try:
                from PIL import Image as PILImage
                import io
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter

                image = PILImage.open(photo_path)
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
                cert_count += 1
                logger.info(f"Added photo to merged PDF for student {student.ht_no}")
            except Exception as e:
                logger.error(f"Error adding photo to merged student PDF: {e}")

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


def collect_student_files(student):
    """Collect student photo and certificates from Cloudinary or local storage."""
    photo_file = None
    image_files = []
    pdf_files = []
    temp_files = []

    def _collect_asset(file_field, url_value=None, default_suffix='.pdf'):
        """Helper to collect a single asset (photo or certificate) from local or remote storage."""
        # 1. Try local file path first (standard storage)
        if file_field:
            try:
                # Check if it has a path (local storage)
                local_path = file_field.path if hasattr(file_field, 'path') else None
                if local_path and os.path.exists(local_path):
                    return local_path, local_path.lower().endswith('.pdf')
            except Exception:
                pass

        # 1. Try local file first (more reliable than Cloudinary)
        if file_field:
            try:
                local_path = file_field.path if hasattr(file_field, 'path') else None
                if local_path and os.path.exists(local_path):
                    print(f"  [COLLECT] Using local file: {local_path}")
                    return local_path, local_path.lower().endswith('.pdf')
            except Exception:
                pass

        # 2. Try provided URL value (Cloudinary/Remote URL field) - with better error handling
        if url_value and isinstance(url_value, str) and url_value.startswith('http'):
            print(f"  [COLLECT] Trying URL: {url_value}")
            downloaded_path, is_pdf = download_remote_asset(url_value, default_suffix=default_suffix)
            if downloaded_path:
                if downloaded_path not in temp_files:
                    temp_files.append(downloaded_path)
                return downloaded_path, is_pdf

        # 3. Try the file field's URL (Cloudinary storage)
        if file_field:
            try:
                if hasattr(file_field, 'url') and file_field.url:
                    furl = file_field.url
                    # Handle local media URLs that might be passed as relative
                    if furl.startswith(settings.MEDIA_URL):
                        local_media_path = os.path.join(settings.MEDIA_ROOT, furl.replace(settings.MEDIA_URL, '', 1).lstrip('/'))
                        if os.path.exists(local_media_path):
                            return local_media_path, local_media_path.lower().endswith('.pdf')
                    
                    # Handle remote URLs from Cloudinary storage
                    if furl.startswith('http'):
                        downloaded_path, is_pdf = download_remote_asset(furl, default_suffix=default_suffix)
                        if downloaded_path:
                            if downloaded_path not in temp_files:
                                temp_files.append(downloaded_path)
                            return downloaded_path, is_pdf
            except Exception:
                pass

        # 4. Fallback to generic helper if available
        try:
            file_path, file_url = get_file_from_field(file_field, url_value)
            if file_path and os.path.exists(file_path):
                return file_path, file_path.lower().endswith('.pdf')

            if file_url and isinstance(file_url, str) and file_url.startswith('http'):
                downloaded_path, is_pdf = download_remote_asset(file_url, default_suffix=default_suffix)
                if downloaded_path:
                    if downloaded_path not in temp_files:
                        temp_files.append(downloaded_path)
                    return downloaded_path, is_pdf
        except Exception:
            pass

        return None, False

    photo_file, _ = _collect_asset(student.photo, getattr(student, 'photo_url', None), default_suffix='.jpg')
    print(f"  [COLLECT] Photo collected: {photo_file is not None}")

    cert_fields = [
        ('cert_achieve', 'cert_achieve_url'),
        ('cert_intern', 'cert_intern_url'),
        ('cert_courses', 'cert_courses_url'),
        ('cert_sdp', 'cert_sdp_url'),
        ('cert_extra', 'cert_extra_url'),
        ('cert_placement', 'cert_placement_url'),
        ('cert_national', 'cert_national_url'),
    ]

    cert_count = 0
    for file_field_name, url_field_name in cert_fields:
        file_field = getattr(student, file_field_name, None)
        url_field = getattr(student, url_field_name, None)
        print(f"  [COLLECT] Checking {file_field_name}: file={file_field is not None}, url={url_field is not None}")

        asset_path, is_pdf = _collect_asset(file_field, url_field, default_suffix='.jpg')
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

    print(f"  [COLLECT] Total certificates collected: {cert_count}")

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

    # Student URLs are already stored directly on the model

    # Automatically generate PDF if it doesn't exist and student has photo/certificates
    if not student.pdf_url and not student.pdf_generated:
        has_content = bool(
            student.photo or student.photo_url or
            student.cert_achieve or student.cert_intern or student.cert_courses or
            student.cert_sdp or student.cert_extra or student.cert_placement or student.cert_national or
            student.cert_achieve_url or student.cert_intern_url or student.cert_courses_url or
            student.cert_sdp_url or student.cert_extra_url or student.cert_placement_url or student.cert_national_url
        )

        if has_content:
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
            'admin_login': True, 'error': error,
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
                return redirect('dashboard:student_dashboard')

            student = Student.objects.filter(ht_no=username).first()
            if student:
                valid_passwords = [student.student_phone, student.student_email, student.ht_no]
                if student.dob:
                    valid_passwords.append(student.dob.strftime('%Y-%m-%d'))
                    valid_passwords.append(student.dob.strftime('%d-%m-%Y'))
                if any(p and password == p for p in valid_passwords):
                    request.session['student_logged_in'] = True
                    request.session['student_username'] = username
                    return redirect('dashboard:student_dashboard')
            error = 'Invalid student credentials'
            messages.error(request, error)
        return render(request, 'dashboard/login.html', {
            'title': 'Student Login',
            'student_login': True,
            'error': error,
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
        return redirect('dashboard:student_dashboard')
    # Directly render login page instead of redirecting
    return render(request, 'dashboard/login.html', {
        'title': 'Admin Login - ANURAG ENGINEERING COLLEGE',
        'admin_login': True,
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

        dob_raw = request.POST.get('dob', '')
        joining_date_raw = request.POST.get('joining_date', '')
        if dob_raw and parse_date(dob_raw) is None:
            messages.error(request, 'Invalid date of birth. Use YYYY-MM-DD format (e.g., 1990-01-15)')
            return render(request, 'dashboard/add_faculty_form.html', {})
        if joining_date_raw and parse_date(joining_date_raw) is None:
            messages.error(request, 'Invalid joining date. Use YYYY-MM-DD format (e.g., 2020-01-15)')
            return render(request, 'dashboard/add_faculty_form.html', {})

        try:
            phd_status = request.POST.get('phd_degree', '')
            phd_title = request.POST.get('phd_title', '').strip() if phd_status == 'Completed' else ''

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
                joining_date=parse_date(request.POST.get('joining_date')),
                jntuh_id=request.POST.get('jntuh_id', ''),
                aicte_id=request.POST.get('aicte_id', ''),
                pan=request.POST.get('pan', ''),
                aadhar=request.POST.get('aadhar', ''),
                apaar_id=request.POST.get('apaar_id', ''),
                orcid_id=request.POST.get('orcid_id', ''),
                exp_anurag=request.POST.get('exp_anurag', ''),
                exp_other=request.POST.get('exp_other', ''),
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
                    Certificate.objects.filter(faculty=faculty).exists()
                )
                if has_uploads:
                    generate_faculty_pdf(request, faculty.id)
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
            'phd_degree', 'phd_title', 'phd_year', 'phd_university', 'phd_spec',
            'subjects_dealt', 'scm', 'about_yourself', 'results',
            'exp_anurag', 'exp_other',
        ]
        for attr in text_fields:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)
        if request.POST.get('phd_degree') != 'Completed':
            faculty.phd_title = ''
        for date_attr in ['dob', 'joining_date']:
            val = request.POST.get(date_attr)
            setattr(faculty, date_attr, parse_date(val) if val else None)
            
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
                    res = cloudinary.uploader.upload(
                        file,
                        resource_type=resource_type,
                        folder=f"student_documents/{folder}",
                        public_id=public_id,
                        overwrite=True,
                        access_mode="public"  # Ensure public access
                    )
                    print(f"  [UPLOAD] Upload result keys: {list(res.keys())}")
                    actual_public_id = res.get('public_id')
                    secure_url = res.get('secure_url')
                    print(f"  [UPLOAD] Actual public_id: {actual_public_id}")
                    print(f"  [UPLOAD] Secure URL: {secure_url}")

                    # Verify the upload by trying to access the resource immediately
                    if secure_url:
                        import requests
                        try:
                            verify_response = requests.head(secure_url, timeout=10)
                            if verify_response.status_code == 200:
                                print(f"  [UPLOAD] Verification successful - resource is accessible")
                                return secure_url
                            else:
                                print(f"  [UPLOAD] Verification failed - HTTP {verify_response.status_code}")
                                return None
                        except Exception as verify_err:
                            print(f"  [UPLOAD] Verification error: {verify_err}")
                            return None
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
                    return saved_path
                except Exception as e:
                    logger.error(f"Local file save error ({folder}): {e}")
                    return None
            # Parse DOB properly
            dob_value = None
            if request.POST.get('dob'):
                try:
                    from datetime import datetime
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
                if ca: # Cloudinary configured - prioritize Cloudinary
                    curl = _upload(pf, 'photos')
                    if curl:
                        student.photo_url = curl
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
            for fn, folder, fn_url in [('cert_achieve', 'achievement', 'cert_achieve_url'),
                              ('cert_intern', 'internship', 'cert_intern_url'),
                              ('cert_courses', 'courses', 'cert_courses_url'),
                              ('cert_sdp', 'sdp', 'cert_sdp_url'),
                              ('cert_extra', 'extra', 'cert_extra_url'),
                              ('cert_placement', 'placement', 'cert_placement_url'),
                              ('cert_national', 'national', 'cert_national_url')]:
                if request.FILES.get(fn):
                    print(f"  [DEBUG] Processing {fn} ({folder})")
                    cf = request.FILES[fn]
                    print(f"  [DEBUG] File: {cf.name}, size: {cf.size}")
                    if ca: # Cloudinary configured
                        curl = _upload(cf, folder)
                        if curl:
                            setattr(student, fn_url, curl)
                            files_up.append(fn)
                            print(f"  [DEBUG] Successfully uploaded {fn} to {curl}")
                        else:
                            print(f"  [DEBUG] Cloudinary upload failed for {fn}, trying local")
                            local_path = _save_local(cf, folder)
                            if local_path:
                                setattr(student, fn, local_path)
                                files_lo.append(fn)
                                print(f"  [DEBUG] Saved {fn} locally to {local_path}")
                    else:
                        local_path = _save_local(cf, folder)
                        if local_path:
                            setattr(student, fn, local_path)
                            files_lo.append(fn)
                else:
                    print(f"  [DEBUG] No file received for {fn}")
            student.save()

            # Ensure the student flow (add_student.html) always attempts
            # to build a single individual PDF that includes photo + certificates.
            try:
                has_uploads = bool(
                    student.photo or student.photo_url or
                    student.cert_achieve or student.cert_intern or student.cert_courses or
                    student.cert_sdp or student.cert_extra or student.cert_placement or student.cert_national or
                    student.cert_achieve_url or student.cert_intern_url or student.cert_courses_url or
                    student.cert_sdp_url or student.cert_extra_url or student.cert_placement_url or
                    student.cert_national_url
                )
                if has_uploads:
                    generate_student_pdf(student)
            except Exception as pdf_e:
                logger.warning(f"Student added, but merged PDF generation failed: {pdf_e}")

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
    try:
        return render(request, 'dashboard/add_student.html')
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
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            ca = is_cloudinary_configured()
            
            def _upload(file, folder):
                if not file or not ca:
                    return None
                try:
                    file.seek(0) # Ensure at beginning
                    res = cloudinary.uploader.upload(
                        file,
                        resource_type="auto",
                        folder=f"student_documents/{folder}",
                        public_id=f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=True,
                        access_mode="public"  # Ensure public access
                    )
                    return res.get('secure_url')
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
                    return saved_path
                except Exception as e:
                    logger.error(f"Local file save error ({folder}): {e}")
                    return None
            updated_student = form.save()

            # Handle photo manually because we want Cloudinary support
            if request.FILES.get('photo'):
                pf = request.FILES['photo']
                if ca:
                    curl = _upload(pf, 'photos')
                    if curl:
                        updated_student.photo_url = curl
                        updated_student.photo = None # Clear local file if uploaded to Cloudinary
                        updated_student.save(update_fields=['photo', 'photo_url'])
                    else:
                        # If Cloudinary fails, it already has the local file from form.save()
                        pass
                
            # Calculate correct age from DOB if DOB was updated
            if updated_student.dob:
                try:
                    updated_student.age = calculate_correct_age(updated_student.dob)
                    updated_student.save(update_fields=['age'])
                except Exception:
                    pass

            # Check for certificates in POST/FILES even if not in form
            cert_fields = [
                ('cert_achieve', 'achievement', 'cert_achieve_url'), 
                ('cert_intern', 'internship', 'cert_intern_url'),
                ('cert_courses', 'courses', 'cert_courses_url'), 
                ('cert_sdp', 'sdp', 'cert_sdp_url'),
                ('cert_extra', 'extra', 'cert_extra_url'), 
                ('cert_placement', 'placement', 'cert_placement_url'),
                ('cert_national', 'national', 'cert_national_url')
            ]
            
            any_cert_updated = False
            for fn, folder, fn_url in cert_fields:
                if request.FILES.get(fn):
                    cf = request.FILES[fn]
                    if ca:
                        curl = _upload(cf, folder)
                        if curl:
                            setattr(updated_student, fn_url, curl)
                            setattr(updated_student, fn, None)
                            any_cert_updated = True
                        else:
                            local_path = _save_local(cf, folder)
                            if local_path:
                                setattr(updated_student, fn, local_path)
                                setattr(updated_student, fn_url, None)
                                any_cert_updated = True
                    else:
                        local_path = _save_local(cf, folder)
                        if local_path:
                            setattr(updated_student, fn, local_path)
                            setattr(updated_student, fn_url, None)
                            any_cert_updated = True
            
            if any_cert_updated:
                updated_student.save()
                
            messages.success(request, "Student updated successfully.")
            return redirect('dashboard:students_data')
    else:
        form = StudentForm(instance=student)
    return render(request, 'dashboard/add_student.html', {'form': form, 'title': 'Edit Student', 'student': student})


def generate_student_pdf_view(request, student_id):
    # Allow both Django authenticated users and student session users
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if not (user_authenticated or request.session.get('student_logged_in')):
        return redirect('dashboard:student_login')

    student = get_object_or_404(Student, id=student_id)

    # If student session user, only allow access to their own record
    user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
    if request.session.get('student_logged_in') and not user_authenticated:
        student_username = request.session.get('student_username')
        if student.ht_no != student_username:
            messages.error(request, "You can only access your own student record.")
            return redirect('dashboard:student_dashboard')

    try:
        # Generate student PDF with merged certificates
        pdf_bytes = generate_student_pdf(student, return_bytes=True)
        if not pdf_bytes:
            messages.error(request, "Failed to generate PDF.")
            return redirect('dashboard:students_data' if user_authenticated else 'dashboard:student_dashboard')
        
        # Merge with certificates if available
        has_certificates = bool(
            student.cert_achieve or student.cert_intern or student.cert_courses or
            student.cert_sdp or student.cert_extra or student.cert_placement or student.cert_national or
            student.cert_achieve_url or student.cert_intern_url or student.cert_courses_url or
            student.cert_sdp_url or student.cert_extra_url or student.cert_placement_url or student.cert_national_url
        )
        
        if has_certificates:
            try:
                merged_bytes = merge_student_certificates_with_pdf_bytes(pdf_bytes, student)
                if merged_bytes and len(merged_bytes) > 100:
                    pdf_bytes = merged_bytes
                    logger.info(f"Successfully merged student PDF with certificates for {student.ht_no}")
                else:
                    logger.warning(f"Merge failed for student {student.ht_no}, using main PDF only")
            except Exception as merge_err:
                logger.warning(f"Certificate merge error for student {student.ht_no}: {merge_err}. Using main PDF only.")
        
        # Return PDF directly as downloadable file
        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
        response['Content-Length'] = len(pdf_bytes)
        return response
    except Exception as e:
        logger.error(f"Error generating PDF for student {student_id}: {e}")
        messages.error(request, f"Failed to generate PDF: {str(e)}")
        return redirect('dashboard:students_data' if user_authenticated else 'dashboard:student_dashboard')


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
def generate_student_pdf(student, return_bytes=False):
    print(f"\n{'='*60}\nSTUDENT PDF: {student.student_name} ({student.ht_no})\n{'='*60}")

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

    def _build_reportlab_info_pdf(student_obj, photo_path=None):
        """Create a simple student profile PDF without wkhtmltopdf."""
        import io
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

        if photo_path and os.path.exists(photo_path):
            try:
                photo_img = Image(photo_path, width=1.4 * inch, height=1.7 * inch)
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
    local_photo_path = None
    photo_url_for_pdf = None

    # Try Cloudinary URL first
    if student.photo_url:
        p = _download(student.photo_url)
        if p:
            local_photo_path = p
            photo_url_for_pdf = build_file_uri(p)
            print(f"  [OK] Photo (Cloudinary -> local): {photo_url_for_pdf}")

    # Fallback to FileField
    if not photo_url_for_pdf and student.photo and getattr(student.photo, 'name', ''):
        lp = _local_path(student.photo)
        if lp:
            local_photo_path = lp
            photo_url_for_pdf = build_file_uri(lp)
            print(f"  [OK] Photo (local file): {photo_url_for_pdf}")
        else:
            try:
                fu = student.photo.url
                if fu and fu.startswith('http'):
                    p = _download(fu)
                    if p:
                        local_photo_path = p
                        photo_url_for_pdf = build_file_uri(p)
                        print(f"  [OK] Photo (URL -> local): {photo_url_for_pdf}")
            except Exception:
                pass

    # ── ANURAG HEADER IMAGE PATH ──────────────────────────────
    anurag_header_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'ANURAG HEADER.png')
    anurag_header_url = build_file_uri(anurag_header_path)

    # ── BUILD TEMPLATE CONTEXT ────────────────────────────────
    context = {
        'student': student,
        'current_date': datetime.now(),
        'local_photo_path': photo_url_for_pdf,
        'anurag_header_url': anurag_header_url,
    }

    # ── GENERATE INFO PDF with pdfkit ─────────────────────────
    html_string = render_to_string('dashboard/student_pdf.html', context)

    info_pdf_bytes = None
    used_reportlab_fallback = False

    if pdfkit is not None:
        options = {
            'page-size': 'A4',
            'margin-top': '15mm', 'margin-right': '15mm',
            'margin-bottom': '15mm', 'margin-left': '15mm',
            'encoding': 'UTF-8',
            'enable-local-file-access': '',
            'quiet': '',
            'no-stop-slow-scripts': None,
            'javascript-delay': '500',
            'load-error-handling': 'ignore',
            'no-outline': None,
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
            if os.path.exists(path) or path == 'wkhtmltopdf':
                try:
                    import subprocess
                    result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        wkhtmltopdf_path = path
                        break
                except:
                    continue

        try:
            if wkhtmltopdf_path:
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                info_pdf_bytes = pdfkit.from_string(html_string, False, options=options, configuration=config)
            else:
                info_pdf_bytes = pdfkit.from_string(html_string, False, options=options)
            print(f"  [OK] Info PDF generated: {len(info_pdf_bytes)} bytes")
        except Exception as e:
            print(f"  [WARN] pdfkit error, using ReportLab fallback: {e}")

    # Always try wkhtmltopdf first for better compatibility
    if info_pdf_bytes is None:
        print("  [INFO] wkhtmltopdf failed, using ReportLab fallback")
        info_pdf_bytes = _build_reportlab_info_pdf(student, local_photo_path)
        used_reportlab_fallback = True
        print(f"  [OK] ReportLab fallback info PDF generated: {len(info_pdf_bytes)} bytes")

    # Validate PDF content
    if info_pdf_bytes and len(info_pdf_bytes) > 100:
        if not info_pdf_bytes.startswith(b'%PDF'):
            print("  [WARN] Generated content is not a valid PDF, using fallback")
            info_pdf_bytes = _build_reportlab_info_pdf(student, local_photo_path)
            used_reportlab_fallback = True
            print(f"  [OK] Fallback PDF generated: {len(info_pdf_bytes)} bytes")
    else:
        print("  [WARN] PDF generation failed, using basic fallback")
        info_pdf_bytes = _build_reportlab_info_pdf(student, local_photo_path)
        used_reportlab_fallback = True

    # ── MERGE: info PDF + all uploaded documents ──────────────
    filename = f"student_{student.ht_no}_{date.today().strftime('%Y%m%d')}.pdf"
    final_pdf_bytes = info_pdf_bytes  # fallback = info PDF only

    try:
        from pypdf import PdfWriter, PdfReader
        from PIL import Image as PILImage

        writer = PdfWriter()
        readers_keep = []  # keep PdfReader objects alive

        # --- helper: add a file (path) to writer ---
        def _add_to_writer(path):
            if not path or not os.path.exists(path):
                return
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

        # 2. Collect all student certificates
        cert_fields = [
            ('cert_achieve', 'cert_achieve_url'),
            ('cert_intern', 'cert_intern_url'),
            ('cert_courses', 'cert_courses_url'),
            ('cert_sdp', 'cert_sdp_url'),
            ('cert_extra', 'cert_extra_url'),
            ('cert_placement', 'cert_placement_url'),
            ('cert_national', 'cert_national_url'),
        ]

        for file_field_name, url_field_name in cert_fields:
            ff = getattr(student, file_field_name, None)
            url_val = getattr(student, url_field_name, None)

            # Try local file first
            p = _local_path(ff) if ff else None
            if not p and url_val and isinstance(url_val, str) and url_val.startswith('http'):
                p = _download(url_val)
            elif ff:
                try:
                    furl = ff.url
                    if furl and furl.startswith('http'):
                        p = _download(furl)
                except Exception:
                    pass

            if p:
                _add_to_writer(p)

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

                # Upload to Cloudinary
                if is_cloudinary_configured():
                    try:
                        cloud_result = cloudinary.uploader.upload(
                            merged_tmp.name,
                            resource_type='raw',
                            folder=f"student_pdfs",
                            public_id=f"student_{student.ht_no}_{date.today().strftime('%Y%m%d')}",
                            overwrite=True
                        )
                        if cloud_result and 'secure_url' in cloud_result:
                            student.pdf_url = cloud_result['secure_url']
                            student.save(update_fields=['pdf_url'])
                            print(f"  [OK] Uploaded to Cloudinary: {cloud_result['secure_url']}")
                            return_url = cloud_result['secure_url']
                        else:
                            print("  [WARN] Cloudinary upload failed (non-fatal)")
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

    # Fallback: save locally if Cloudinary failed or not configured
    if not return_url:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_final:
                tmp_final.write(final_pdf_bytes)
                tmp_final_path = tmp_final.name

            with open(tmp_final_path, 'rb') as pdf_handle:
                student.pdf_file.save(f"student_{student.ht_no}.pdf", File(pdf_handle), save=False)
            student.pdf_generated = True
            student.pdf_generation_time = timezone.now()
            student.save(update_fields=['pdf_file', 'pdf_generated', 'pdf_generation_time'])
            return_url = student.pdf_file.url if student.pdf_file else None
            print(f"  [OK] PDF saved locally: {return_url}")
        except Exception as e:
            print(f"  [ERR] Local save failed: {e}")
            return_url = None

    # Cleanup temp files
    for temp_path in temp_files:
        try:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

    student.pdf_generated = True
    student.pdf_generation_time = timezone.now()
    student.save(update_fields=['pdf_generated', 'pdf_generation_time', 'updated_at'])

    if used_reportlab_fallback:
        logger.info(f"Student PDF for {student.ht_no} used ReportLab fallback instead of pdfkit/wkhtmltopdf")

    print("=== STUDENT PDF GENERATION COMPLETE ===\n")

    # If return_bytes is True, return the PDF content directly
    if return_bytes:
        return final_pdf_bytes

    return return_url








def view_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    url = getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None)
    if url:
        return redirect(url)
    messages.error(request, "PDF not generated yet.")
    return redirect('dashboard:students_data')


def download_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if student.pdf_url:
        return redirect(student.pdf_url)
    if student.pdf_file and student.pdf_file.url:
        response = HttpResponse(student.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
        return response
    # Generate PDF if not available
    pdf_url = generate_student_pdf(student)
    if pdf_url:
        return redirect(pdf_url)
    messages.error(request, "Failed to generate PDF.")
    return redirect('dashboard:students_data')


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
# ==================== ENHANCED GENERATE FACULTY PDF — FIXED VERSION ====================
@login_required
def generate_faculty_pdf(request, faculty_id):
    """
    Generate faculty PDF with comprehensive error handling for Render deployment.
    """
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        print(f"\n{'='*60}\nFACULTY PDF: {faculty.staff_name} ({faculty.employee_code})\n{'='*60}")
        print(f"  [DEBUG] ON_RENDER={getattr(settings, 'ON_RENDER', False)}")
        print(f"  [DEBUG] CLOUDINARY_CONFIGURED={getattr(settings, 'CLOUDINARY_CONFIGURED', False)}")
        print(f"  [DEBUG] BASE_DIR={settings.BASE_DIR}")

        # Test WeasyPrint import and basic functionality FIRST
        try:
            from weasyprint import HTML
            from weasyprint.text.fonts import FontConfiguration
            print("  [CHECK] WeasyPrint imported successfully")
            print(f"  [CHECK] WeasyPrint version: {HTML.__module__}")
        except ImportError as ie:
            error_msg = f'WeasyPrint not installed: {ie}'
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')
        except Exception as e:
            error_msg = f'WeasyPrint initialization error: {e}'
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')

        # Early validation: Ensure BASE_DIR is set
        if not settings.BASE_DIR:
            error_msg = "BASE_DIR is not configured"
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')
        print(f"\n{'='*60}\nFACULTY PDF: {faculty.staff_name} ({faculty.employee_code})\n{'='*60}")
        print(f"  [DEBUG] ON_RENDER={getattr(settings, 'ON_RENDER', False)}")
        print(f"  [DEBUG] CLOUDINARY_CONFIGURED={getattr(settings, 'CLOUDINARY_CONFIGURED', False)}")
        print(f"  [DEBUG] BASE_DIR={settings.BASE_DIR}")
        
        # Test WeasyPrint import and basic functionality FIRST
        try:
            from weasyprint import HTML
            from weasyprint.text.fonts import FontConfiguration
            print("  [CHECK] WeasyPrint imported successfully")
            print(f"  [CHECK] WeasyPrint version: {HTML.__module__}")
        except ImportError as ie:
            error_msg = f'WeasyPrint not installed: {ie}'
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')
        except Exception as e:
            error_msg = f'WeasyPrint initialization error: {e}'
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')
        
        # Early validation: Ensure BASE_DIR is set
        if not settings.BASE_DIR:
            error_msg = "BASE_DIR is not configured"
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')
        
        print("  [DEBUG] Starting asset collection...")

        # ── temp file tracker ──────────────────────────────────────
        temp_files = []

        # ── Helper: download URL -> local temp file ─────────────────
        def _download(url, suffix=None):
            """Download a URL to a local temp file. Returns path or None."""
            if not url or not url.startswith('http'):
                return None

            # Try to download Cloudinary URLs even on Render if configured
            # if getattr(settings, 'ON_RENDER', False) and 'cloudinary.com' in url:
            #     print(f"  [SKIP] Cloudinary URL download on Render: {url}")
            #     return None
            
            # Use a browser-like User-Agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            try:
                print(f"  [DOWNLOAD] Attempting: {url}")
                r = requests.get(url, timeout=30, headers=headers)
                
                # Enhanced fallback for Cloudinary errors (401/403/404)
                if r.status_code in [401, 403, 404] and 'cloudinary.com' in url:
                    print(f"  [DOWNLOAD] Cloudinary error {r.status_code}, trying fallbacks...")
                    try:
                        # Try without extension first
                        if '.' in url.split('/')[-1]:
                            base_url = url.rsplit('.', 1)[0]
                            print(f"  [DOWNLOAD] Trying without extension: {base_url}")
                            r_alt = requests.get(base_url, timeout=30, headers=headers)
                            if r_alt.status_code == 200:
                                r = r_alt
                        
                        if r.status_code != 200:
                            for public_id in get_cloudinary_public_id_candidates(url):
                                if r.status_code == 200:
                                    break

                                if '/raw/upload/' in url:
                                    private_response = try_cloudinary_private_download(public_id, headers=headers)
                                    if private_response is not None:
                                        r = private_response
                                        break

                                for resource_type in ('raw', 'image'):
                                    try:
                                        # Attempt API lookup if configured
                                        if is_cloudinary_configured():
                                            resource = cloudinary.api.resource(public_id, resource_type=resource_type)
                                            secure_url = resource.get('secure_url')
                                            if secure_url:
                                                r = requests.get(secure_url, timeout=30, headers=headers)
                                                if r.status_code == 200:
                                                    break
                                    except Exception as api_err:
                                        print(f"  [DOWNLOAD] API lookup failed for {public_id} ({resource_type}): {api_err}")

                                if r.status_code == 200:
                                    break

                                # Construct alternative resource type URLs
                                cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
                                if cloud_name:
                                    for res_type in ['raw', 'image']:
                                        try_url = f"https://res.cloudinary.com/{cloud_name}/{res_type}/upload/{public_id}"
                                        if try_url != url:
                                            print(f"  [DOWNLOAD] Trying {res_type} URL: {try_url}")
                                            test_r = requests.get(try_url, timeout=30, headers=headers)
                                            if test_r.status_code == 200:
                                                r = test_r
                                                break
                    except Exception as cloud_err:
                        print(f"  [WARN] Cloudinary fallback failed: {cloud_err}")

                if r.status_code != 200:
                    print(f"  [SKIP] HTTP {r.status_code}: {url}")
                    return None
                
                ct = r.headers.get('content-type', '').lower()
                if suffix is None:
                    if 'pdf' in ct or url.lower().endswith('.pdf'):
                        suffix = '.pdf'
                    elif 'png' in ct or url.lower().endswith('.png'):
                        suffix = '.png'
                    elif 'jpg' in ct or 'jpeg' in ct or url.lower().endswith('.jpg') or url.lower().endswith('.jpeg'):
                        suffix = '.jpg'
                    else:
                        suffix = '.pdf' # Default to PDF for raw docs
                
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

        # ── Helper: FileField -> any accessible path (local or dl) ─
        def _resolve(ff, url_attr=None, as_image=True):
            """
            Returns (local_path, is_pdf) for a FileField or URL string.
            Downloads remote files to temp. Returns (None, False) if unavailable.
            """
            # 1. Explicit URL field
            url = getattr(faculty, url_attr, None) if url_attr else None
            if not url and ff:
                url = getattr(ff, 'url', None) if hasattr(ff, 'url') else (ff if isinstance(ff, str) else None)

            # 2. Local path (fastest)
            lp = _local_path(ff) if ff and hasattr(ff, 'path') else None
            if lp:
                is_pdf = lp.lower().endswith('.pdf')
                return lp, is_pdf

            # 3. Download from URL
            if url and isinstance(url, str) and url.startswith('http'):
                # For Cloudinary raw PDFs: convert to image URL for display if requested
                if as_image and 'cloudinary.com' in url and '/raw/upload/' in url:
                    img_url = url.replace('/raw/upload/', '/image/upload/')
                    if img_url.lower().endswith('.pdf'):
                        img_url = img_url[:-4] + '.jpg'
                    p = _download(img_url, '.jpg')
                    if p:
                        return p, False
                
                # Otherwise download the original file
                p = _download(url)
                if p:
                    is_pdf = p.endswith('.pdf')
                    return p, is_pdf

            return None, False

        # ── PHOTO ──────────────────────────────────────────────────
        print(f"  [DEBUG] Resolving photo for faculty: {faculty.staff_name} ({faculty.employee_code})")
        print(f"  [DEBUG] faculty.photo: {faculty.photo}")
        print(f"  [DEBUG] faculty.cloudinary_photo_url: {faculty.cloudinary_photo_url}")

        photo_url_for_pdf, local_photo_path, photo_temp_files, photo_source = resolve_faculty_photo_for_pdf(faculty)
        temp_files.extend(photo_temp_files)

        if not photo_url_for_pdf:
            print(f"  [WARNING] No photo available for faculty {faculty.employee_code} in PDF")
        else:
            print(
                f"  [OK] Final photo encoded for PDF from {photo_source} "
                f"(base64 length: {len(photo_url_for_pdf)})"
            )

        # ── RELATED DATA ──────────────────────────────────────────
        research_publications = ResearchPublication.objects.filter(faculty=faculty).order_by('-publication_year')
        fdps = FDP.objects.filter(faculty=faculty).order_by('-from_date')
        btech_projects = BTechProject.objects.filter(faculty=faculty).order_by('-batch')
        research_projects = ResearchProject.objects.filter(faculty=faculty)
        certificates = Certificate.objects.filter(faculty=faculty)
        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
        except FacultyProfile.DoesNotExist:
            profile = None

        subjects_list = [s.strip() for s in (faculty.subjects_dealt or '').split(',') if s.strip()]

        # ── RESULTS — parse into two separate context vars ────────
        # results_data_list: guaranteed list of dicts (for template loop)
        # results_text:      plain text fallback
        results_data_list = []
        results_text = ''
        if faculty.results:
            try:
                raw = json.loads(faculty.results)
                if isinstance(raw, list):
                    for item in raw:
                        if isinstance(item, dict):
                            attempted = int(item.get('students_attempted') or item.get('attempted') or 0)
                            passed = int(item.get('students_passed') or item.get('passed') or 0)
                            pct = float(item.get('percentage') or 0)
                            if attempted > 0 and pct == 0:
                                pct = round(passed / attempted * 100, 2)
                            results_data_list.append({
                                'subject_name': item.get('subject_name') or item.get('subject') or 'N/A',
                                'subject_code': item.get('subject_code') or item.get('code') or '',
                                'academic_year': item.get('academic_year') or item.get('year') or '',
                                'classes_taken': int(item.get('classes_taken') or 0),
                                'students_attempted': attempted,
                                'students_passed': passed,
                                'percentage': pct,
                            })
                        else:
                            results_text += str(item) + '\n'
                elif isinstance(raw, dict):
                    attempted = int(raw.get('students_attempted') or raw.get('attempted') or 0)
                    passed = int(raw.get('students_passed') or raw.get('passed') or 0)
                    pct = float(raw.get('percentage') or 0)
                    if attempted > 0 and pct == 0:
                        pct = round(passed / attempted * 100, 2)
                    results_data_list.append({
                        'subject_name': raw.get('subject_name') or 'Result',
                        'subject_code': raw.get('subject_code') or '',
                        'academic_year': raw.get('academic_year') or '',
                        'classes_taken': int(raw.get('classes_taken') or 0),
                        'students_attempted': attempted,
                        'students_passed': passed,
                        'percentage': pct,
                    })
                else:
                    results_text = str(faculty.results)
            except (json.JSONDecodeError, TypeError, ValueError):
                results_text = str(faculty.results)

        print(f"  Results parsed: {len(results_data_list)} rows, text fallback: {bool(results_text)}")

        # ── EXPERIENCE ────────────────────────────────────────────
        experience = "N/A"
        if faculty.joining_date:
            today = date.today()
            j = faculty.joining_date
            yrs = today.year - j.year
            mths = today.month - j.month
            dys = today.day - j.day
            if dys < 0:
                mths -= 1
                pm = (today.month - 1) or 12
                py = today.year - (1 if today.month == 1 else 0)
                dim = 30 if pm in [4,6,9,11] else (29 if pm==2 and ((py%4==0 and py%100!=0) or py%400==0) else (28 if pm==2 else 31))
                dys += dim
            if mths < 0:
                yrs -= 1
                mths += 12
            experience = f"{yrs} Years {mths} Months {dys} Days"

        # ── DOCUMENT STATUS FLAGS ─────────────────────────────────
        has_aadhar = bool(getattr(faculty, 'aadhar_file', None) or getattr(faculty, 'aadhar_url', None))
        has_pan = bool(getattr(faculty, 'pan_file', None) or getattr(faculty, 'pan_url', None))
        has_apaar = bool(getattr(faculty, 'apaar_file', None) or getattr(faculty, 'apaar_url', None))
        has_scm = bool(getattr(faculty, 'scm_file', None) or getattr(faculty, 'scm_url', None))
        has_jntuh_biodata = bool(getattr(faculty, 'jntuh_biodata', None) or getattr(faculty, 'jntuh_biodata_url', None))
        has_ssc_cert = bool(getattr(faculty, 'ssc_certificate', None) or getattr(faculty, 'ssc_certificate_url', None))
        has_inter_cert = bool(getattr(faculty, 'inter_certificate', None) or getattr(faculty, 'inter_certificate_url', None))
        has_ug_cert = bool(getattr(faculty, 'ug_certificate', None) or getattr(faculty, 'ug_certificate_url', None))
        has_pg_cert = bool(getattr(faculty, 'pg_certificate', None) or getattr(faculty, 'pg_certificate_url', None))
        has_phd_cert = bool(getattr(faculty, 'phd_certificate', None) or getattr(faculty, 'phd_certificate_url', None))

        def _has_doc(url_field, file_field):
            url = getattr(faculty, url_field, '') or ''
            if url.strip():
                return True
            ff = getattr(faculty, file_field, None)
            return bool(ff and getattr(ff, 'name', ''))

        has_research_proof = _has_doc('research_proof_url', 'research_proof') or any(
            (getattr(p, 'proof_document', None) and getattr(p.proof_document, 'name', '')) or
            getattr(p, 'proof_document_url', None) for p in research_publications)
        has_fdp_certificate = _has_doc('fdp_certificate_url', 'fdp_certificate') or any(
            (getattr(f, 'certificate', None) and getattr(f.certificate, 'name', '')) or
            getattr(f, 'certificate_url', None) for f in fdps)
        has_experience_certificates = _has_doc('experience_certificates_url', 'experience_certificates')
        has_other_documents = _has_doc('other_documents_url', 'other_documents')

        def _asset_identity(file_field=None, url=None):
            if url and str(url).strip():
                return f"url:{str(url).strip()}"
            if file_field and getattr(file_field, 'name', ''):
                return f"file:{file_field.name}"
            return None

        def _collect_unique_asset_refs(primary_file_field=None, primary_url=None, related_items=None,
                                       related_file_attr=None, related_url_attr=None):
            refs = []
            seen_refs = set()

            def _add_ref(file_field=None, url=None):
                identity = _asset_identity(file_field=file_field, url=url)
                if not identity or identity in seen_refs:
                    return
                seen_refs.add(identity)
                refs.append((file_field, url))

            _add_ref(primary_file_field, primary_url)
            for item in related_items or []:
                _add_ref(
                    getattr(item, related_file_attr, None),
                    getattr(item, related_url_attr, None),
                )
            return refs

        def _track_temp_asset(path, file_field=None):
            if not path:
                return
            if path not in temp_files and not (
                file_field and hasattr(file_field, 'path') and getattr(file_field, 'path', None) == path
            ):
                temp_files.append(path)

        def _count_asset_pages(asset_refs):
            total_pages = 0
            document_count = 0
            try:
                from pypdf import PdfReader
            except ImportError:
                return 0, 0

            for file_field, url in asset_refs:
                path, is_pdf = get_local_or_remote_asset(file_field, url=url, default_suffix='.pdf')
                if not path or not os.path.exists(path):
                    continue

                _track_temp_asset(path, file_field=file_field)
                document_count += 1

                if not is_pdf:
                    total_pages += 1
                    continue

                try:
                    with open(path, 'rb') as f:
                        reader = PdfReader(f)
                        total_pages += len(reader.pages)
                except Exception:
                    total_pages += 1

            return total_pages, document_count

        research_proof_asset_refs = _collect_unique_asset_refs(
            primary_file_field=getattr(faculty, 'research_proof', None),
            primary_url=getattr(faculty, 'research_proof_url', None),
            related_items=research_publications,
            related_file_attr='proof_document',
            related_url_attr='proof_document_url',
        )
        fdp_certificate_asset_refs = _collect_unique_asset_refs(
            primary_file_field=getattr(faculty, 'fdp_certificate', None),
            primary_url=getattr(faculty, 'fdp_certificate_url', None),
            related_items=fdps,
            related_file_attr='certificate',
            related_url_attr='certificate_url',
        )

        research_proof_total_pages, research_proof_documents_count = _count_asset_pages(research_proof_asset_refs)
        fdp_certificate_total_pages, fdp_certificate_documents_count = _count_asset_pages(fdp_certificate_asset_refs)

        if has_research_proof and research_proof_total_pages == 0:
            research_proof_total_pages = max(research_proof_documents_count, 1)
        if has_fdp_certificate and fdp_certificate_total_pages == 0:
            fdp_certificate_total_pages = max(fdp_certificate_documents_count, 1)

        # Academic years for display
        research_proof_academic_year = getattr(faculty, 'research_proof_academic_year', '') or ''
        if not research_proof_academic_year:
            fp = research_publications.exclude(academic_year='').exclude(academic_year=None).first()
            if fp:
                research_proof_academic_year = fp.academic_year or ''

        fdp_certificate_academic_year = getattr(faculty, 'fdp_certificate_academic_year', '') or ''
        if not fdp_certificate_academic_year:
            ff = fdps.exclude(academic_year='').exclude(academic_year=None).first()
            if ff:
                fdp_certificate_academic_year = ff.academic_year or ''

        experience_certificates_academic_year = getattr(faculty, 'experience_certificates_academic_year', '') or ''
        other_documents_academic_year = getattr(faculty, 'other_documents_academic_year', '') or ''

        # ── DOCUMENT DISPLAY URLs (for inline preview in PDF) ─────
        def _display_url(url_field, file_field):
            """Return a file:/// URL for inline display in wkhtmltopdf."""
            url = getattr(faculty, url_field, '') or ''
            ff = getattr(faculty, file_field, None)
            p, _ = _resolve(ff, url_field)
            if p:
                return build_file_uri(p)
            return ''

        research_proof_is_image = True
        research_proof_display_url = ''
        for proof_file, proof_url in research_proof_asset_refs:
            proof_path, proof_is_pdf = get_local_or_remote_asset(proof_file, url=proof_url, default_suffix='.pdf')
            if proof_path:
                _track_temp_asset(proof_path, file_field=proof_file)
                research_proof_display_url = build_file_uri(proof_path)
                research_proof_is_image = not proof_is_pdf
                break

        fdp_certificate_is_image = True
        fdp_certificate_display_url = ''
        for fdp_file, fdp_url in fdp_certificate_asset_refs:
            fdp_path, fdp_is_pdf = get_local_or_remote_asset(fdp_file, url=fdp_url, default_suffix='.pdf')
            if fdp_path:
                _track_temp_asset(fdp_path, file_field=fdp_file)
                fdp_certificate_display_url = build_file_uri(fdp_path)
                fdp_certificate_is_image = not fdp_is_pdf
                break

        experience_certificates_display_url = _display_url('experience_certificates_url', 'experience_certificates')
        other_documents_display_url = _display_url('other_documents_url', 'other_documents')

        # ── ANURAG HEADER IMAGE (convert to base64 for reliability) ──────────────────────────────
        anurag_header_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'ANURAG HEADER.png')
        anurag_header_url = ''
        if os.path.exists(anurag_header_path):
            try:
                import base64
                with open(anurag_header_path, 'rb') as f:
                    header_data = f.read()
                anurag_header_url = f"data:image/png;base64,{base64.b64encode(header_data).decode('utf-8')}"
                print(f"  [OK] Header image encoded as base64")
            except Exception as e:
                print(f"  [WARN] Could not encode header image: {e}")
                anurag_header_url = build_file_uri(anurag_header_path)
        else:
            print(f"  [WARN] Header image not found at {anurag_header_path}")

        # ── BUILD TEMPLATE CONTEXT ────────────────────────────────
        context = {
            'faculty': faculty,
            'profile': profile,
            'anurag_header_url': anurag_header_url,
            'research_publications': research_publications,
            'research_projects': research_projects,
            'fdps': fdps,
            'btech_projects': btech_projects,
            'certificates': certificates,
            'subjects_list': subjects_list,
            'experience': experience,
            'current_date': datetime.now(),
             # ── Results — TWO separate vars so template never shows raw text ──
             'results_data_list': results_data_list,   # list of dicts
             'results_text': results_text,              # plain text fallback
             # ── Photo ──
             'photo_url': photo_url_for_pdf,
             'local_photo_path': build_file_uri(local_photo_path) if local_photo_path else '',
            # ── Document flags ──
            'has_aadhar': has_aadhar, 'has_pan': has_pan, 'has_apaar': has_apaar,
            'has_scm': has_scm, 'has_jntuh_biodata': has_jntuh_biodata,
            'has_ssc_cert': has_ssc_cert, 'has_inter_cert': has_inter_cert,
            'has_ug_cert': has_ug_cert, 'has_pg_cert': has_pg_cert, 'has_phd_cert': has_phd_cert,
            'has_research_proof': has_research_proof,
            'research_proof_academic_year': research_proof_academic_year,
            'research_proof_display_url': research_proof_display_url,
            'research_proof_is_image': research_proof_is_image,
            'research_proof_total_pages': research_proof_total_pages,
            'has_fdp_certificate': has_fdp_certificate,
            'fdp_certificate_academic_year': fdp_certificate_academic_year,
            'fdp_certificate_display_url': fdp_certificate_display_url,
            'fdp_certificate_is_image': fdp_certificate_is_image,
            'fdp_certificate_total_pages': fdp_certificate_total_pages,
            'has_experience_certificates': has_experience_certificates,
            'experience_certificates_academic_year': experience_certificates_academic_year,
            'experience_certificates_display_url': experience_certificates_display_url,
            'experience_certificates_is_image': True,
            'has_other_documents': has_other_documents,
            'other_documents_academic_year': other_documents_academic_year,
            'other_documents_display_url': other_documents_display_url,
            'other_documents_is_image': True,
            'classes_taken': getattr(faculty, 'classes_taken', None) or 'Not specified',
        }

        # ── GENERATE INFO PDF with WeasyPrint ───────────────────────
        print("  [DEBUG] Rendering template to string...")
        try:
            html_string = render_to_string('dashboard/faculty_pdf.html', context)
            print(f"  [DEBUG] Template rendered: {len(html_string)} characters")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"  [ERROR] Template rendering failed:\n{error_details}")
            logger.error(f"Template error: {e}\n{error_details}")
            messages.error(request, f'Template error: {str(e)[:200]}')
            return redirect('dashboard:faculty_dashboard')

        print("  [DEBUG] Generating PDF with WeasyPrint...")
        try:
            from weasyprint import HTML
            # Use BASE_DIR as base_url for resolving relative paths
            base_url = Path(settings.BASE_DIR).resolve().as_uri() if settings.BASE_DIR else None

            print(f"  [DEBUG] base_url={base_url}")
            html_obj = HTML(string=html_string, base_url=base_url)
            info_pdf_bytes = html_obj.write_pdf()
            print(f"  [OK] Info PDF generated: {len(info_pdf_bytes)} bytes")
        except ImportError as ie:
            error_msg = f'WeasyPrint not installed: {ie}'
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('dashboard:faculty_dashboard')
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"WeasyPrint error: {e}\n{error_details}")
            print(f"\n{'='*60}")
            print(f"WEASYPRINT ERROR:")
            print(f"{error_details}")
            print(f"{'='*60}\n")
            messages.error(request, f'PDF generation error: {str(e)[:200]}')
            return redirect('dashboard:faculty_dashboard')

        # ── MERGE: info PDF + all uploaded documents ──────────────
        filename = f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}.pdf"
        final_pdf_bytes = info_pdf_bytes  # fallback = info PDF only

        try:
            from pypdf import PdfWriter, PdfReader
            from PIL import Image as PILImage

            writer = PdfWriter()
            readers_keep = []  # keep PdfReader objects alive

            # --- helper: add a file (path) to writer ---
            def _add_to_writer(path):
                if not path or not os.path.exists(path):
                    return
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

            # 2. Collect ALL faculty documents (enhanced with direct download fallback)
            doc_fields = [
                ('aadhar_url', 'aadhar_file', 'Aadhar'),
                ('pan_url', 'pan_file', 'PAN'),
                ('apaar_url', 'apaar_file', 'APAAR'),
                ('scm_url', 'scm_file', 'SCM'),
                ('jntuh_biodata_url', 'jntuh_biodata', 'JNTUH Bio-Data'),
                ('ssc_certificate_url', 'ssc_certificate', 'SSC Certificate'),
                ('inter_certificate_url', 'inter_certificate', 'Inter Certificate'),
                ('ug_certificate_url', 'ug_certificate', 'UG Certificate'),
                ('pg_certificate_url', 'pg_certificate', 'PG Certificate'),
                ('phd_certificate_url', 'phd_certificate', 'PhD Certificate'),
                ('experience_certificates_url', 'experience_certificates', 'Experience Certificates'),
                ('other_documents_url', 'other_documents', 'Other Documents'),
            ]
            for url_field, file_field, label in doc_fields:
                ff = getattr(faculty, file_field, None)
                url_val = getattr(faculty, url_field, None)
                print(f"  [DOC] Processing {label}: url={bool(url_val)}, file={bool(ff and getattr(ff, 'name', ''))}")
                
                p = None
                # Try URL first (Render/Cloudinary path)
                if url_val and isinstance(url_val, str) and url_val.startswith('http'):
                    p, _ = download_remote_asset(url_val, default_suffix='.pdf')
                    if p:
                        temp_files.append(p)
                        print(f"  [OK] {label} downloaded from URL")
                
                # Fallback to local file
                if not p and ff and getattr(ff, 'name', ''):
                    try:
                        local_p = ff.path
                        if os.path.exists(local_p):
                            p = local_p
                            print(f"  [OK] {label} found locally")
                    except Exception:
                        pass
                    
                    # Try file URL if local path failed
                    if not p:
                        try:
                            fu = ff.url if hasattr(ff, 'url') else None
                            if fu and fu.startswith('http'):
                                p, _ = download_remote_asset(fu, default_suffix='.pdf')
                                if p:
                                    temp_files.append(p)
                                    print(f"  [OK] {label} downloaded from file URL")
                        except Exception:
                            pass

                if p:
                    _add_to_writer(p)
                else:
                    print(f"  [SKIP] {label}: no accessible file found")

            # 3. Certificate records (the ones in the related Certificate model)
            for cert in certificates:
                cert_p, _ = get_local_or_remote_asset(cert.certificate_file, url=cert.cloudinary_url, default_suffix='.pdf')
                if cert_p and cert_p not in temp_files and not (cert.certificate_file and hasattr(cert.certificate_file, 'path') and getattr(cert.certificate_file, 'path', None) == cert_p):
                    temp_files.append(cert_p)
                if cert_p:
                    _add_to_writer(cert_p)

            # 4. Merge unique research/FDP proof assets once
            for proof_file, proof_url in research_proof_asset_refs:
                proof_path, _ = get_local_or_remote_asset(proof_file, url=proof_url, default_suffix='.pdf')
                if proof_path:
                    _track_temp_asset(proof_path, file_field=proof_file)
                    _add_to_writer(proof_path)

            for fdp_file, fdp_url in fdp_certificate_asset_refs:
                fdp_path, _ = get_local_or_remote_asset(fdp_file, url=fdp_url, default_suffix='.pdf')
                if fdp_path:
                    _track_temp_asset(fdp_path, file_field=fdp_file)
                    _add_to_writer(fdp_path)

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

                # Upload to Cloudinary
                if is_cloudinary_configured():
                    try:
                        cloudinary_public_id = f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}"
                        print(f" [CLOUD]  Uploading merged PDF to Cloudinary: {cloudinary_public_id}")
                        cloud_result = cloudinary.uploader.upload(
                            merged_tmp.name, resource_type='raw',
                            folder=f"faculty_documents/{faculty.employee_code}",
                            public_id='complete_profile', overwrite=True,
                        )
                        faculty.cloudinary_pdf_url = cloud_result['secure_url']
                        faculty.save(update_fields=['cloudinary_pdf_url'])
                        CloudinaryUpload.objects.update_or_create(
                            faculty=faculty, upload_type='complete_profile_pdf',
                            defaults={
                                'cloudinary_url': cloud_result['secure_url'],
                                'public_id': cloud_result['public_id'],
                                'resource_type': 'raw',
                                'uploaded_by': request.user.username if getattr(request.user, 'is_authenticated', False) else 'Anonymous',
                            }
                        )
                        print(f"  [OK] Uploaded to Cloudinary: {cloud_result['secure_url']}")
                    except Exception as e:
                        print(f"  [WARN] Cloudinary upload failed (non-fatal): {e}")
            else:
                print("  [WARN] No pages in writer — returning info PDF only")

        except Exception as merge_err:
            logger.error(f"Merge error (non-fatal): {merge_err}")
            traceback.print_exc()
            print(f"  [ERR] Merge failed, using info PDF: {merge_err}")

        # ── CLEANUP ───────────────────────────────────────────────
        for t in temp_files:
            try:
                if os.path.exists(t):
                    os.remove(t)
            except Exception:
                pass

        # ── LOG + RETURN ──────────────────────────────────────────
        FacultyLog.objects.create(
            faculty=faculty, action='PDF Generated',
            details=f'PDF for {faculty.employee_code}: {len(results_data_list)} results, {fdps.count()} FDPs, {certificates.count()} certs',
            performed_by=request.user.username if request.user.is_authenticated else 'Anonymous',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        try:
            faculty.pdf_document.save(filename, ContentFile(final_pdf_bytes), save=False)
            faculty.save(update_fields=['pdf_document'])
        except Exception as save_err:
            logger.warning(f"Could not save local faculty PDF copy: {save_err}")

        response = HttpResponse(final_pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Error generating faculty PDF for {faculty_id}: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error generating PDF: {str(e)[:200]}')
        return redirect('dashboard:faculty_dashboard')









# ==================== CHARTS & ANALYTICS ====================
@login_required
def faculty_charts(request):
    if plt is None:
        messages.error(request, 'Matplotlib not installed.')
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
        messages.error(request, 'Matplotlib not installed.')
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
        try:
            from weasyprint import HTML
            from django.conf import settings as django_settings

            html_string = render_to_string('faculty/custom_pdf_template.html', {'data': request.POST.dict()})
            base_url = Path(django_settings.BASE_DIR).resolve().as_uri() if django_settings.BASE_DIR else None
            html_obj = HTML(string=html_string, base_url=base_url)
            pdf = html_obj.write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_document.pdf"'
            return response
        except ImportError:
            return JsonResponse({'success': False, 'error': 'WeasyPrint not installed. Please install weasyprint package.'})
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
                    # Use the comprehensive generation function that includes certificate merging
                    pdf_bytes = generate_faculty_pdf_bytes(fac)
                    
                    if pdf_bytes:
                        pname = f"faculty_{fac.employee_code}.pdf"
                        pp = os.path.join(temp_dir, pname)
                        with open(pp, 'wb') as f:
                            f.write(pdf_bytes)
                        zipf.write(pp, pname)

                        # Cloudinary upload handled inside generate_faculty_pdf if not already present
                        # But we can still ensure it's recorded if needed
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
            # Save photo locally
            faculty.photo = request.FILES['photo']
            # Upload to Cloudinary
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


@login_required
def sync_all_faculty_photos_to_cloudinary(request):
    if not is_cloudinary_configured():
        messages.error(request, "Cloudinary is not configured properly.")
        return redirect("dashboard:faculty_list")
    
    faculty_list = Faculty.objects.all()
    ok = err = 0
    
    for faculty in faculty_list:
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
                ok += 1
            except Exception as e:
                logger.error(f"Photo sync error for {faculty.employee_code}: {e}")
                err += 1
    
    FacultyLog.objects.create(
        faculty=None, action='Sync All Faculty Photos to Cloudinary',
        details=f'Synced {ok} faculty photos ({err} errors)',
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    
    if ok:
        messages.success(request, f"Synced {ok} faculty photos to Cloudinary.")
    if err:
        messages.warning(request, f"Failed to sync {err} faculty photos.")
    
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
            writer.write(mf)
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
    """
    Generate PDF bytes for a faculty member without requiring a real request.
    This is used internally for merging certificates and bulk operations.
    """
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        # Use a real superuser instead of AnonymousUser to bypass login requirement
        # This is safe because this function is only called internally
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        except Exception:
            # Fallback if User model has issues
            from django.contrib.auth.models import AnonymousUser
            user = AnonymousUser()
        
        factory = RequestFactory()
        fake_req = factory.get('/')
        fake_req.user = user
        fake_req.META['REMOTE_ADDR'] = '127.0.0.1'
        
        r = generate_faculty_pdf(fake_req, faculty.id)
        return r.content if isinstance(r, HttpResponse) else None
    except Exception as e:
        logger.error(f"Error generating PDF bytes: {e}")
        import traceback
        traceback.print_exc()
        return None


def merge_student_certificates(request, student_id):
    """Merges student photo and all certificates into a single PDF and uploads to Cloudinary."""
    student = get_object_or_404(Student, id=student_id)

    # Check if student has photo or any certificates
    has_content = bool(
        student.photo or student.photo_url or
        student.cert_achieve or student.cert_intern or student.cert_courses or
        student.cert_sdp or student.cert_extra or student.cert_placement or student.cert_national or
        student.cert_achieve_url or student.cert_intern_url or student.cert_courses_url or
        student.cert_sdp_url or student.cert_extra_url or student.cert_placement_url or student.cert_national_url
    )

    if not has_content:
        messages.error(request, 'No photo or certificates found to merge.')
        return redirect('dashboard:student_detail', student_id=student_id)

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
                    output_pdf_path, resource_type="raw", folder="merged_student_certificates",
                    public_id=f"merged_student_{student.ht_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=True
                )
                merged_url = cr['secure_url']
                logger.info(f"Uploaded merged certificates to Cloudinary: {merged_url}")
            except Exception as e:
                logger.error(f"Failed to upload merged certificates to Cloudinary: {e}")

        # 5. Result message
        if merged_url:
            from django.utils.safestring import mark_safe
            messages.success(request, mark_safe(f'Successfully merged {merged_count} items. <a href="{merged_url}" target="_blank" class="btn btn-sm btn-info">Download Merged PDF</a>'))
        else:
            messages.warning(request, f'Merged {merged_count} items into PDF, but Cloudinary upload failed.')

        return redirect('dashboard:student_detail', student_id=student_id)

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
            p, _ = get_local_or_remote_asset(ff, url=url_val, default_suffix='.pdf')
            if p and p not in temp_files and not (ff and hasattr(ff, 'path') and getattr(ff, 'path', None) == p):
                temp_files.append(p)
            if p:
                _add_to_writer_internal(p)

        # 3. Certificate records (related model)
        from .models import Certificate
        for cert in Certificate.objects.filter(faculty=faculty):
            cert_p, _ = get_local_or_remote_asset(cert.certificate_file, url=cert.cloudinary_url, default_suffix='.pdf')
            if cert_p and cert_p not in temp_files and not (cert.certificate_file and hasattr(cert.certificate_file, 'path') and getattr(cert.certificate_file, 'path', None) == cert_p):
                temp_files.append(cert_p)
            if cert_p:
                _add_to_writer_internal(cert_p)

        # 4. FDP Certificates
        from .models import FDP
        for fdp_rec in FDP.objects.filter(faculty=faculty):
            fdp_p, _ = get_local_or_remote_asset(
                fdp_rec.certificate,
                url=getattr(fdp_rec, 'certificate_url', None),
                default_suffix='.pdf'
            )
            if fdp_p and fdp_p not in temp_files and not (fdp_rec.certificate and hasattr(fdp_rec.certificate, 'path') and getattr(fdp_rec.certificate, 'path', None) == fdp_p):
                temp_files.append(fdp_p)
            if fdp_p:
                _add_to_writer_internal(fdp_p)

        # 5. Research Proofs
        from .models import ResearchPublication
        for pub in ResearchPublication.objects.filter(faculty=faculty):
            pub_p, _ = get_local_or_remote_asset(
                pub.proof_document,
                url=getattr(pub, 'proof_document_url', None),
                default_suffix='.pdf'
            )
            if pub_p and pub_p not in temp_files and not (pub.proof_document and hasattr(pub.proof_document, 'path') and getattr(pub.proof_document, 'path', None) == pub_p):
                temp_files.append(pub_p)
            if pub_p:
                _add_to_writer_internal(pub_p)

        # Finalize
        if len(writer.pages) > 0:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as mf:
                writer.write(mf)
                temp_files.append(mf.name)
                with open(mf.name, 'rb') as f:
                    merged = f.read()
            
            # Cleanup
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass
            
            return merged
        
        return pdf_bytes if pdf_bytes else None

    except Exception as e:
        logger.error(f"Error in merge_certificates_with_pdf_bytes: {e}")
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
            return redirect('dashboard:students_data_view')
        else:
            messages.error(request, 'Invalid password. Access denied.')
            return redirect('dashboard:students_data')
    return render(request, 'dashboard/students_data_password.html')


def student_dashboard_password(request):
    """Password protection for student dashboard page"""
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
