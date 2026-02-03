# dashboard/utils.py
import os
import logging
from datetime import datetime, date
import pdfkit
from PyPDF2 import PdfMerger
import cloudinary.uploader
from django.conf import settings

logger = logging.getLogger(__name__)


def calculate_experience(joining_date):
    """Calculates experience string from joining date to today."""
    if not joining_date:
        return "0Y 0M 0D"
    if isinstance(joining_date, str):
        try:
            joining_date = datetime.strptime(joining_date, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid Date"
    today = date.today()
    diff = today - joining_date
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30
    return f"{years}Y {months}M {days}D"


def generate_pdf_from_html(html_content, output_path=None):
    """Generates PDF binary data or file from HTML string."""
    try:
        config = pdfkit.configuration(wkhtmltopdf=getattr(settings, 'WKHTMLTOPDF_PATH', None))
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
            'enable-local-file-access': '',
        }
        if output_path:
            pdfkit.from_string(html_content, output_path, options=options, configuration=config)
            return True
        return pdfkit.from_string(html_content, False, options=options, configuration=config)
    except Exception as e:
        logger.error(f"PDF Generation Error: {str(e)}")
        return None


def merge_pdfs(pdf_paths, output_path=None):
    """Merges multiple PDFs into one."""
    try:
        merger = PdfMerger()
        for path in pdf_paths:
            if os.path.exists(path):
                merger.append(path)

        if output_path:
            merger.write(output_path)
            merger.close()
            return True
        return None
    except Exception as e:
        logger.error(f"PDF Merge Error: {str(e)}")
        return False


def calculate_age(dob):
    if not dob: return 0
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def format_date(date_obj, format_str='%d-%m-%Y'):
    return date_obj.strftime(format_str) if date_obj else ""


def get_academic_year():
    today = date.today()
    year = today.year
    return f"{year}-{year + 1}" if today.month >= 6 else f"{year - 1}-{year}"


def extract_text_from_pdf(pdf_path):
    return ""  # Placeholder to satisfy import


def validate_faculty_data(data):
    return []  # Placeholder to satisfy import (returns list of errors)


def upload_to_cloudinary(file, folder="faculty_portal", resource_type="auto"):
    try:
        return cloudinary.uploader.upload(file, folder=folder, resource_type=resource_type)
    except Exception as e:
        logger.error(f"Cloudinary Error: {str(e)}")
        return None