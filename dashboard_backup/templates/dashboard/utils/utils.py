# faculty/dashboard/utils.py
import os
import tempfile
import logging
from datetime import datetime, date
from io import BytesIO
from typing import List, Optional, Tuple, Dict, Any
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import requests
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import cloudinary
import cloudinary.uploader
import cloudinary.api
from .models import Faculty, Certificate, CloudinaryUpload

logger = logging.getLogger(__name__)


# ==================== CERTIFICATE MERGING FUNCTIONS ====================

def merge_certificates_with_faculty_pdf(faculty_pdf_path: str, certificate_files: List) -> Optional[bytes]:
    """
    Merge faculty PDF with certificate PDFs

    Args:
        faculty_pdf_path: Path to faculty PDF file
        certificate_files: List of certificate file objects

    Returns:
        Merged PDF bytes or None if error
    """
    try:
        merger = PdfMerger()

        # Add faculty PDF
        if os.path.exists(faculty_pdf_path):
            with open(faculty_pdf_path, 'rb') as faculty_pdf:
                merger.append(faculty_pdf)
        elif default_storage.exists(faculty_pdf_path):
            with default_storage.open(faculty_pdf_path, 'rb') as faculty_pdf:
                merger.append(faculty_pdf)
        else:
            logger.error(f"Faculty PDF not found: {faculty_pdf_path}")
            return None

        # Add all certificates
        certificate_count = 0
        for cert_file in certificate_files:
            try:
                if hasattr(cert_file, 'path') and os.path.exists(cert_file.path):
                    # Local file system
                    merger.append(cert_file.path)
                    certificate_count += 1
                elif hasattr(cert_file, 'file') and cert_file.file:
                    # In-memory file
                    cert_file.file.seek(0)
                    merger.append(cert_file.file)
                    certificate_count += 1
                elif hasattr(cert_file, 'read'):
                    # File-like object
                    cert_file.seek(0)
                    merger.append(cert_file)
                    certificate_count += 1
                else:
                    logger.warning(f"Could not process certificate file: {cert_file}")
            except Exception as e:
                logger.error(f"Error adding certificate: {str(e)}")
                continue

        # Create merged PDF in memory
        merged_pdf = BytesIO()
        merger.write(merged_pdf)
        merger.close()

        logger.info(f"Merged {certificate_count} certificates with faculty PDF")
        return merged_pdf.getvalue()

    except Exception as e:
        logger.error(f"Error merging certificates: {str(e)}")
        return None


def merge_certificates_with_faculty_pdf_bytes(faculty_pdf_bytes: bytes, faculty: Faculty) -> Optional[bytes]:
    """
    Merge faculty PDF bytes with certificates

    Args:
        faculty_pdf_bytes: Faculty PDF as bytes
        faculty: Faculty object

    Returns:
        Merged PDF bytes or None if error
    """
    try:
        merger = PdfMerger()

        # Add faculty PDF from bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_faculty:
            tmp_faculty.write(faculty_pdf_bytes)
            tmp_faculty_path = tmp_faculty.name

        merger.append(tmp_faculty_path)

        # Get certificates for this faculty
        certificates = Certificate.objects.filter(faculty=faculty)
        certificate_count = 0

        for certificate in certificates:
            try:
                if certificate.certificate_file and certificate.certificate_file.path:
                    # Local file
                    if os.path.exists(certificate.certificate_file.path):
                        merger.append(certificate.certificate_file.path)
                        certificate_count += 1
                    else:
                        logger.warning(f"Certificate file not found: {certificate.certificate_file.path}")

                elif certificate.cloudinary_url:
                    # Download from Cloudinary
                    cert_bytes = download_from_cloudinary(certificate.cloudinary_url)
                    if cert_bytes:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cert:
                            tmp_cert.write(cert_bytes)
                            tmp_cert_path = tmp_cert.name
                        merger.append(tmp_cert_path)
                        os.unlink(tmp_cert_path)
                        certificate_count += 1

            except Exception as e:
                logger.error(f"Error adding certificate {certificate.id}: {str(e)}")
                continue

        # Create merged PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as merged_tmp:
            merger.write(merged_tmp.name)
            merger.close()

            # Read merged PDF
            with open(merged_tmp.name, 'rb') as f:
                merged_pdf = f.read()

            # Clean up temp files
            os.unlink(merged_tmp.name)

        os.unlink(tmp_faculty_path)

        logger.info(f"Merged {certificate_count} certificates for faculty {faculty.employee_code}")
        return merged_pdf

    except Exception as e:
        logger.error(f"Error merging certificates with PDF bytes: {str(e)}")
        return None


def download_from_cloudinary(cloudinary_url: str) -> Optional[bytes]:
    """
    Download file from Cloudinary URL

    Args:
        cloudinary_url: Cloudinary URL of the file

    Returns:
        File bytes or None if error
    """
    try:
        response = requests.get(cloudinary_url, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to download from Cloudinary: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading from Cloudinary: {str(e)}")
        return None


def upload_merged_pdf_to_cloudinary(merged_pdf_bytes: bytes, faculty: Faculty) -> Optional[str]:
    """
    Upload merged PDF to Cloudinary

    Args:
        merged_pdf_bytes: Merged PDF bytes
        faculty: Faculty object

    Returns:
        Cloudinary URL or None if error
    """
    try:
        # Save merged PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(merged_pdf_bytes)
            tmp_file_path = tmp_file.name

        # Upload to Cloudinary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        cloudinary_response = cloudinary.uploader.upload(
            tmp_file_path,
            resource_type="raw",
            folder="merged_documents",
            public_id=f"merged_{faculty.employee_code}_{timestamp}",
            overwrite=False,
            tags=[f"merged_{faculty.employee_code}", faculty.department, "merged_pdf"]
        )

        # Record the upload
        CloudinaryUpload.objects.create(
            faculty=faculty,
            upload_type='merged_pdf',
            cloudinary_url=cloudinary_response['secure_url'],
            public_id=cloudinary_response['public_id'],
            resource_type=cloudinary_response['resource_type'],
            format=cloudinary_response.get('format', 'pdf'),
            bytes=cloudinary_response['bytes'],
            raw_response=cloudinary_response,
            uploaded_by='System'
        )

        # Clean up temp file
        os.unlink(tmp_file_path)

        logger.info(f"Merged PDF uploaded to Cloudinary for faculty {faculty.employee_code}")
        return cloudinary_response['secure_url']

    except Exception as e:
        logger.error(f"Error uploading merged PDF to Cloudinary: {str(e)}")
        return None


def batch_merge_certificates_for_faculty(faculty_id: int) -> Dict[str, Any]:
    """
    Batch merge certificates for a faculty member

    Args:
        faculty_id: Faculty ID

    Returns:
        Dictionary with results
    """
    try:
        faculty = Faculty.objects.get(id=faculty_id)
        certificates = Certificate.objects.filter(faculty=faculty)

        if not certificates.exists():
            return {
                'success': False,
                'error': 'No certificates found to merge'
            }

        # Check if faculty has PDF on Cloudinary
        if not faculty.cloudinary_pdf_url:
            return {
                'success': False,
                'error': 'Faculty PDF not available on Cloudinary'
            }

        # Download faculty PDF from Cloudinary
        faculty_pdf_bytes = download_from_cloudinary(faculty.cloudinary_pdf_url)
        if not faculty_pdf_bytes:
            return {
                'success': False,
                'error': 'Failed to download faculty PDF from Cloudinary'
            }

        # Merge certificates
        merged_pdf_bytes = merge_certificates_with_faculty_pdf_bytes(faculty_pdf_bytes, faculty)
        if not merged_pdf_bytes:
            return {
                'success': False,
                'error': 'Failed to merge certificates'
            }

        # Upload merged PDF to Cloudinary
        merged_url = upload_merged_pdf_to_cloudinary(merged_pdf_bytes, faculty)
        if not merged_url:
            return {
                'success': False,
                'error': 'Failed to upload merged PDF to Cloudinary'
            }

        return {
            'success': True,
            'merged_url': merged_url,
            'certificate_count': certificates.count(),
            'message': f'Successfully merged {certificates.count()} certificates'
        }

    except Faculty.DoesNotExist:
        return {
            'success': False,
            'error': 'Faculty not found'
        }
    except Exception as e:
        logger.error(f"Error in batch_merge_certificates_for_faculty: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def split_pdf_by_pages(pdf_bytes: bytes) -> List[bytes]:
    """
    Split PDF into individual pages

    Args:
        pdf_bytes: PDF bytes

    Returns:
        List of page bytes
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        reader = PdfReader(tmp_file_path)
        pages = []

        for page_num in range(len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as page_file:
                writer.write(page_file.name)
                with open(page_file.name, 'rb') as f:
                    pages.append(f.read())
                os.unlink(page_file.name)

        os.unlink(tmp_file_path)
        return pages

    except Exception as e:
        logger.error(f"Error splitting PDF: {str(e)}")
        return []


def extract_certificate_metadata(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extract metadata from certificate PDF

    Args:
        pdf_bytes: Certificate PDF bytes

    Returns:
        Dictionary with metadata
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        reader = PdfReader(tmp_file_path)
        metadata = {
            'page_count': len(reader.pages),
            'pdf_version': reader.metadata.get('/Producer', 'Unknown'),
            'creation_date': reader.metadata.get('/CreationDate', 'Unknown'),
            'modification_date': reader.metadata.get('/ModDate', 'Unknown'),
            'author': reader.metadata.get('/Author', 'Unknown'),
            'title': reader.metadata.get('/Title', 'Unknown'),
            'subject': reader.metadata.get('/Subject', 'Unknown'),
        }

        # Try to extract text from first page
        try:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            if text:
                metadata['preview_text'] = text[:200] + '...' if len(text) > 200 else text
        except:
            metadata['preview_text'] = 'Unable to extract text'

        os.unlink(tmp_file_path)
        return metadata

    except Exception as e:
        logger.error(f"Error extracting certificate metadata: {str(e)}")
        return {}


def validate_certificate_pdf(pdf_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate certificate PDF

    Args:
        pdf_bytes: PDF bytes to validate

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        # Check if bytes are valid PDF
        if not pdf_bytes.startswith(b'%PDF'):
            return False, "Invalid PDF format"

        # Check file size (max 10MB)
        if len(pdf_bytes) > 10 * 1024 * 1024:
            return False, "File size exceeds 10MB limit"

        # Try to read PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        reader = PdfReader(tmp_file_path)

        # Check number of pages (reasonable limit)
        if len(reader.pages) > 50:
            return False, "Certificate has too many pages (max 50)"

        # Check for encryption
        if reader.is_encrypted:
            return False, "PDF is encrypted/password protected"

        os.unlink(tmp_file_path)
        return True, "Valid PDF"

    except Exception as e:
        return False, f"Invalid PDF: {str(e)}"


def compress_pdf(pdf_bytes: bytes, quality: str = 'medium') -> Optional[bytes]:
    """
    Compress PDF to reduce file size

    Args:
        pdf_bytes: Original PDF bytes
        quality: Compression quality (low, medium, high)

    Returns:
        Compressed PDF bytes or None if error
    """
    try:
        # This is a placeholder - actual implementation would use a PDF compression library
        # For now, return original bytes
        return pdf_bytes

    except Exception as e:
        logger.error(f"Error compressing PDF: {str(e)}")
        return None


def generate_merged_pdf_with_cover(faculty: Faculty, certificates: List[Certificate]) -> Optional[bytes]:
    """
    Generate merged PDF with a cover page

    Args:
        faculty: Faculty object
        certificates: List of certificate objects

    Returns:
        Merged PDF bytes with cover or None if error
    """
    try:
        merger = PdfMerger()

        # Generate cover page
        cover_pdf_bytes = generate_cover_page(faculty, len(certificates))
        if cover_pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cover:
                tmp_cover.write(cover_pdf_bytes)
                tmp_cover_path = tmp_cover.name
            merger.append(tmp_cover_path)

        # Add faculty PDF
        if faculty.cloudinary_pdf_url:
            faculty_pdf_bytes = download_from_cloudinary(faculty.cloudinary_pdf_url)
            if faculty_pdf_bytes:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_faculty:
                    tmp_faculty.write(faculty_pdf_bytes)
                    tmp_faculty_path = tmp_faculty.name
                merger.append(tmp_faculty_path)

        # Add certificates with separator pages
        for i, certificate in enumerate(certificates, 1):
            # Add separator page for each certificate
            separator_pdf_bytes = generate_certificate_separator(certificate, i, len(certificates))
            if separator_pdf_bytes:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_separator:
                    tmp_separator.write(separator_pdf_bytes)
                    tmp_separator_path = tmp_separator.name
                merger.append(tmp_separator_path)

            # Add certificate
            if certificate.certificate_file and certificate.certificate_file.path:
                if os.path.exists(certificate.certificate_file.path):
                    merger.append(certificate.certificate_file.path)
            elif certificate.cloudinary_url:
                cert_bytes = download_from_cloudinary(certificate.cloudinary_url)
                if cert_bytes:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cert:
                        tmp_cert.write(cert_bytes)
                        tmp_cert_path = tmp_cert.name
                    merger.append(tmp_cert_path)
                    os.unlink(tmp_cert_path)

        # Create merged PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as merged_tmp:
            merger.write(merged_tmp.name)

            # Read merged PDF
            with open(merged_tmp.name, 'rb') as f:
                merged_pdf = f.read()

            # Clean up
            merger.close()
            os.unlink(merged_tmp.name)

            if cover_pdf_bytes:
                os.unlink(tmp_cover_path)
            if faculty.cloudinary_pdf_url and faculty_pdf_bytes:
                os.unlink(tmp_faculty_path)

        return merged_pdf

    except Exception as e:
        logger.error(f"Error generating merged PDF with cover: {str(e)}")
        return None


def generate_cover_page(faculty: Faculty, certificate_count: int) -> Optional[bytes]:
    """
    Generate cover page for merged PDF

    Args:
        faculty: Faculty object
        certificate_count: Number of certificates

    Returns:
        Cover page PDF bytes or None if error
    """
    try:
        # This would generate a cover page using a template
        # For now, return None (no cover page)
        return None

    except Exception as e:
        logger.error(f"Error generating cover page: {str(e)}")
        return None


def generate_certificate_separator(certificate: Certificate, index: int, total: int) -> Optional[bytes]:
    """
    Generate separator page for certificate

    Args:
        certificate: Certificate object
        index: Certificate index
        total: Total number of certificates

    Returns:
        Separator page PDF bytes or None if error
    """
    try:
        # This would generate a separator page using a template
        # For now, return None (no separator page)
        return None

    except Exception as e:
        logger.error(f"Error generating certificate separator: {str(e)}")
        return None


def get_merged_pdf_info(faculty_id: int) -> Dict[str, Any]:
    """
    Get information about merged PDFs for a faculty

    Args:
        faculty_id: Faculty ID

    Returns:
        Dictionary with merged PDF information
    """
    try:
        faculty = Faculty.objects.get(id=faculty_id)

        # Get recent merged uploads
        merged_uploads = CloudinaryUpload.objects.filter(
            faculty=faculty,
            upload_type='merged_pdf'
        ).order_by('-upload_date')[:5]

        # Get certificate count
        certificate_count = Certificate.objects.filter(faculty=faculty).count()

        # Check if faculty PDF exists
        has_faculty_pdf = bool(faculty.cloudinary_pdf_url)

        return {
            'success': True,
            'faculty_id': faculty_id,
            'employee_code': faculty.employee_code,
            'has_faculty_pdf': has_faculty_pdf,
            'certificate_count': certificate_count,
            'merged_uploads': [
                {
                    'id': upload.id,
                    'url': upload.cloudinary_url,
                    'date': upload.upload_date.isoformat(),
                    'size': upload.bytes
                }
                for upload in merged_uploads
            ],
            'can_merge': has_faculty_pdf and certificate_count > 0
        }

    except Faculty.DoesNotExist:
        return {
            'success': False,
            'error': 'Faculty not found'
        }
    except Exception as e:
        logger.error(f"Error getting merged PDF info: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def cleanup_old_merged_pdfs(days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old merged PDFs from Cloudinary

    Args:
        days_old: Delete files older than this many days

    Returns:
        Dictionary with cleanup results
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Get old merged uploads
        old_uploads = CloudinaryUpload.objects.filter(
            upload_type='merged_pdf',
            upload_date__lt=cutoff_date
        )

        deleted_count = 0
        failed_deletions = []

        for upload in old_uploads:
            try:
                # Delete from Cloudinary
                result = cloudinary.uploader.destroy(
                    upload.public_id,
                    resource_type="raw"
                )

                if result.get('result') == 'ok':
                    # Delete database record
                    upload.delete()
                    deleted_count += 1
                else:
                    failed_deletions.append(upload.public_id)

            except Exception as e:
                failed_deletions.append(upload.public_id)
                logger.error(f"Error deleting upload {upload.public_id}: {str(e)}")

        return {
            'success': True,
            'deleted_count': deleted_count,
            'failed_deletions': failed_deletions,
            'message': f'Deleted {deleted_count} old merged PDFs'
        }

    except Exception as e:
        logger.error(f"Error in cleanup_old_merged_pdfs: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# ==================== OTHER UTILITY FUNCTIONS (for reference) ====================

def calculate_experience(joining_date: date) -> str:
    """Calculate experience from joining date"""
    if not joining_date:
        return "Not specified"

    today = date.today()

    years = today.year - joining_date.year
    months = today.month - joining_date.month
    days = today.day - joining_date.day

    if days < 0:
        months -= 1
        days += 30  # Approximation

    if months < 0:
        years -= 1
        months += 12

    if years > 0:
        if months > 0:
            return f"{years} years, {months} months"
        else:
            return f"{years} years"
    elif months > 0:
        return f"{months} months"
    else:
        return f"{days} days"


def generate_pdf_from_html(html_content: str, options: Dict = None) -> Optional[bytes]:
    """Generate PDF from HTML content"""
    try:
        import pdfkit

        default_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
        }

        if options:
            default_options.update(options)

        # Configure wkhtmltopdf path
        config = pdfkit.configuration()
        if hasattr(settings, 'WKHTMLTOPDF_PATH'):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

        pdf = pdfkit.from_string(html_content, False, options=default_options, configuration=config)
        return pdf

    except Exception as e:
        logger.error(f"Error generating PDF from HTML: {str(e)}")
        return None


def merge_pdfs(pdf_files: List[str]) -> Optional[bytes]:
    """Merge multiple PDF files"""
    try:
        merger = PdfMerger()

        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                merger.append(pdf_file)

        merged_pdf = BytesIO()
        merger.write(merged_pdf)
        merger.close()

        return merged_pdf.getvalue()

    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}")
        return None


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""


def validate_faculty_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate faculty data"""
    errors = []

    # Check required fields
    required_fields = ['employee_code', 'name', 'department', 'email']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} is required")

    # Validate email format
    email = data.get('email', '')
    if email and '@' not in email:
        errors.append("Invalid email format")

    # Validate percentages
    percentage_fields = ['ssc_percent', 'inter_percent', 'ug_percentage', 'pg_percentage']
    for field in percentage_fields:
        value = data.get(field)
        if value is not None:
            try:
                percentage = float(value)
                if percentage < 0 or percentage > 100:
                    errors.append(f"{field} must be between 0 and 100")
            except ValueError:
                errors.append(f"{field} must be a number")

    return len(errors) == 0, errors


def calculate_age(dob: date) -> int:
    """Calculate age from date of birth"""
    if not dob:
        return 0

    today = date.today()
    age = today.year - dob.year

    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age


def format_date(date_obj: date, format_str: str = "%d-%m-%Y") -> str:
    """Format date object to string"""
    if not date_obj:
        return ""
    return date_obj.strftime(format_str)


def get_academic_year() -> str:
    """Get current academic year"""
    today = date.today()
    year = today.year

    # Academic year runs from June to May
    if today.month >= 6:
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"


def get_disk_usage() -> Dict[str, Any]:
    """Get disk usage statistics"""
    try:
        import shutil

        total, used, free = shutil.disk_usage("/")

        return {
            'total_gb': total // (2 ** 30),
            'used_gb': used // (2 ** 30),
            'free_gb': free // (2 ** 30),
            'percent_used': (used / total) * 100
        }
    except:
        return {'error': 'Unable to get disk usage'}


def get_memory_usage() -> Dict[str, Any]:
    """Get memory usage statistics"""
    try:
        import psutil

        memory = psutil.virtual_memory()

        return {
            'total_gb': memory.total // (2 ** 30),
            'available_gb': memory.available // (2 ** 30),
            'percent_used': memory.percent,
            'used_gb': memory.used // (2 ** 30)
        }
    except:
        return {'error': 'Unable to get memory usage'}


def generate_faculty_pdf_bytes(faculty: Faculty) -> Optional[bytes]:
    """Generate PDF bytes for a faculty member"""
    try:
        from django.template.loader import render_to_string
        import pdfkit

        # Prepare context
        context = {
            'faculty': faculty,
            'subjects': faculty.get_subjects_list(),
            'current_date': date.today().strftime('%d-%m-%Y'),
            'college_name': 'ANURAG ENGINEERING COLLEGE',
        }

        # Render HTML
        html_string = render_to_string('faculty/pdf_template.html', context)

        # Generate PDF
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
        }

        config = pdfkit.configuration()
        if hasattr(settings, 'WKHTMLTOPDF_PATH'):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

        pdf = pdfkit.from_string(html_string, False, options=options, configuration=config)
        return pdf

    except Exception as e:
        logger.error(f"Error generating faculty PDF bytes: {str(e)}")
        return None