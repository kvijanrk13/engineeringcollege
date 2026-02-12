# dashboard/utils.py

import os
import logging
from datetime import datetime, date
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

# -------------------------------------------------
# OPTIONAL DEPENDENCIES (SAFE IMPORTS)
# -------------------------------------------------

try:
    import pdfkit
except Exception:
    pdfkit = None

try:
    from PyPDF2 import PdfMerger
except Exception:
    PdfMerger = None

try:
    import cloudinary.uploader
except Exception:
    cloudinary = None

try:
    import qrcode
except Exception:
    qrcode = None

try:
    import pandas as pd
except Exception:
    pd = None


# =================================================
# EMAIL
# =================================================

def send_email_notification(subject, message, recipient_list, from_email=None, fail_silently=True):
    try:
        if not recipient_list:
            return False

        if not from_email:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=fail_silently,
        )
        return True

    except Exception as e:
        logger.error(f"Email error: {str(e)}")
        return False


# =================================================
# QR CODE
# =================================================

def generate_qr_code(data, output_path=None):
    if not qrcode:
        logger.warning("qrcode library not installed")
        return None

    try:
        qr = qrcode.make(data)
        if output_path:
            qr.save(output_path)
            return output_path
        return qr
    except Exception as e:
        logger.error(f"QR Code error: {str(e)}")
        return None


# =================================================
# EXPERIENCE / DATE UTILITIES
# =================================================

def calculate_experience(joining_date):
    if not joining_date:
        return "0Y 0M 0D"

    if isinstance(joining_date, str):
        try:
            joining_date = datetime.strptime(joining_date, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid Date"

    today = date.today()
    diff = today - joining_date

    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30

    return f"{years}Y {months}M {days}D"


def calculate_age(dob):
    if not dob:
        return 0
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def format_date(date_obj, format_str="%d-%m-%Y"):
    return date_obj.strftime(format_str) if date_obj else ""


def get_academic_year():
    today = date.today()
    year = today.year
    return f"{year}-{year + 1}" if today.month >= 6 else f"{year - 1}-{year}"


# =================================================
# PDF UTILITIES
# =================================================

def generate_pdf_from_html(html_content, output_path=None):
    if not pdfkit:
        return None

    try:
        config = None
        if hasattr(settings, "WKHTMLTOPDF_PATH"):
            config = pdfkit.configuration(
                wkhtmltopdf=settings.WKHTMLTOPDF_PATH
            )

        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "quiet": "",
            "enable-local-file-access": "",
        }

        if output_path:
            pdfkit.from_string(html_content, output_path, options=options, configuration=config)
            return True

        return pdfkit.from_string(html_content, False, options=options, configuration=config)

    except Exception as e:
        logger.error(f"PDF Generation Error: {str(e)}")
        return None


def merge_pdfs(pdf_paths, output_path=None):
    if not PdfMerger:
        return False

    try:
        merger = PdfMerger()
        for path in pdf_paths:
            if os.path.exists(path):
                merger.append(path)

        if output_path:
            merger.write(output_path)
            merger.close()
            return True

        merger.close()
        return False

    except Exception as e:
        logger.error(f"PDF Merge Error: {str(e)}")
        return False


# =================================================
# CLOUDINARY
# =================================================

def upload_to_cloudinary(file, folder="faculty_portal", resource_type="auto"):
    if not cloudinary:
        return None

    try:
        return cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type
        )
    except Exception as e:
        logger.error(f"Cloudinary Error: {str(e)}")
        return None


# =================================================
# EXCEL EXPORT
# =================================================

def export_to_excel(queryset, fields, file_path):
    """
    Export queryset to Excel file.
    Safe stub if pandas is not installed.
    """
    if not pd:
        logger.warning("pandas not installed, cannot export to Excel")
        return None

    try:
        data = list(queryset.values(*fields))
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return file_path
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}")
        return None


# =================================================
# PLACEHOLDERS REQUIRED BY VIEWS IMPORTS
# =================================================

def extract_text_from_pdf(pdf_path):
    return ""


def validate_faculty_data(data):
    return []


def validate_student_data(data):
    """
    Placeholder validation for student bulk upload / form data.
    """
    return []
