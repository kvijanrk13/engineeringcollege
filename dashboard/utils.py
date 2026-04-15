# dashboard/utils.py

import os
import logging
from datetime import datetime, date
from django.conf import settings
from django.core.mail import send_mail
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from PIL import Image as PILImage
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


def parse_date(date_str):
    """
    Parse and validate date string in YYYY-MM-DD format.
    Returns None if invalid or empty.
    Validates reasonable year range (1900-current year).
    """
    if not date_str or date_str.strip() == '':
        return None
    date_str = date_str.strip()
    try:
        parsed = datetime.strptime(date_str, '%Y-%m-%d').date()
        if parsed.year < 1900 or parsed.year > date.today().year:
            return None
        return parsed
    except ValueError:
        return None


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
# ENHANCED PDF VALIDATION
# =================================================

def validate_pdf_file(file_path):
    """
    Validates if a PDF file is properly formatted and readable.
    Returns (True, None) if valid, (False, error_message) if invalid.
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    if os.path.getsize(file_path) == 0:
        return False, "Empty file"

    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if not header.startswith(b'%PDF'):
                return False, "Not a valid PDF file"

        # Try to read the PDF
        reader = PdfReader(file_path)
        if len(reader.pages) == 0:
            return False, "PDF has no pages"

        return True, None
    except Exception as e:
        return False, f"Error reading PDF: {str(e)}"


def validate_image_file(file_path):
    """
    Validates if an image file is properly formatted and readable.
    Returns (True, None) if valid, (False, error_message) if invalid.
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    if os.path.getsize(file_path) == 0:
        return False, "Empty file"

    try:
        with PILImage.open(file_path) as img:
            img.verify()  # Verify it's a valid image
        return True, None
    except Exception as e:
        return False, f"Invalid image: {str(e)}"


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
# ENHANCED PDF MERGE FUNCTIONS
# =================================================

def merge_documents(output_path, image_files=None, pdf_files=None):
    """
    Enhanced merge function with comprehensive validation
    """
    if image_files is None:
        image_files = []
    if pdf_files is None:
        pdf_files = []

    writer = PdfWriter()
    temp_files = []
    merged_count = 0
    skipped_count = 0

    print(f"\n{'=' * 60}")
    print(f"ENHANCED PDF MERGE")
    print(f"  Images: {len(image_files)}")
    print(f"  PDFs: {len(pdf_files)}")
    print(f"{'=' * 60}")

    # Validate and process PDF files
    for pdf_path in pdf_files:
        is_valid, error = validate_pdf_file(pdf_path)
        if not is_valid:
            print(f"  [SKIP] PDF validation failed: {pdf_path} - {error}")
            skipped_count += 1
            continue

        try:
            reader = PdfReader(pdf_path)
            if len(reader.pages) == 0:
                print(f"  [SKIP] PDF has no pages: {os.path.basename(pdf_path)}")
                skipped_count += 1
                continue

            for page in reader.pages:
                writer.add_page(page)
            merged_count += 1
            print(f"  [OK] Added PDF: {os.path.basename(pdf_path)} ({len(reader.pages)} pages)")
        except Exception as e:
            print(f"  [ERROR] Failed to add PDF {pdf_path}: {e}")
            skipped_count += 1

    # Validate and process image files
    for img_path in image_files:
        is_valid, error = validate_image_file(img_path)
        if not is_valid:
            print(f"  [SKIP] Image validation failed: {img_path} - {error}")
            skipped_count += 1
            continue

        try:
            # Create a temporary PDF for this image
            img_buffer = BytesIO()
            c = canvas.Canvas(img_buffer, pagesize=letter)

            # Open and process image
            img = PILImage.open(img_path)

            # Handle transparency
            if img.mode in ('RGBA', 'P', 'LA'):
                bg = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img.convert('RGBA'), mask=img.convert('RGBA').split()[3])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Save as temporary file for ImageReader
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_img.name, 'JPEG', quality=95)
            temp_files.append(temp_img.name)
            temp_img.close()

            # Calculate image dimensions
            img_width, img_height = img.size
            page_width, page_height = letter
            available_width = page_width - 100
            available_height = page_height - 100

            scale = min(available_width / img_width, available_height / img_height)
            draw_width = img_width * scale
            draw_height = img_height * scale
            x = (page_width - draw_width) / 2
            y = (page_height - draw_height) / 2

            # Draw image on canvas
            image = ImageReader(temp_img.name)
            c.drawImage(image, x, y, width=draw_width, height=draw_height)
            c.showPage()
            c.save()

            img_buffer.seek(0)
            img_pdf = PdfReader(img_buffer)
            for page in img_pdf.pages:
                writer.add_page(page)

            merged_count += 1
            print(f"  [OK] Added image: {os.path.basename(img_path)}")

        except Exception as e:
            print(f"  [ERROR] Failed to add image {img_path}: {e}")
            skipped_count += 1

    # Save final PDF
    try:
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"  [OK] Final PDF saved: {output_path}")
        print(f"  Summary: {merged_count} files merged, {skipped_count} files skipped")
        print(f"{'=' * 60}\n")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to save final PDF: {e}")
        return False
    finally:
        # Cleanup temporary files
        for tmp in temp_files:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass


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
