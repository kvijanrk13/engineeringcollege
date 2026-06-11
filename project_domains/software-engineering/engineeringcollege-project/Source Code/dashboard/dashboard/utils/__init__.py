# dashboard/utils/__init__.py

# Package init
default_app_config = 'dashboard.apps.DashboardConfig'

# Import all utility functions to make them available at package level
from .helpers import (
    calculate_experience,
    calculate_age,
    format_date,
    get_academic_year
)
from .pdf_utils import (
    generate_pdf_from_html,
    merge_pdfs,
    extract_text_from_pdf
)
from .validation import (
    validate_faculty_data,
    validate_student_data
)
from .notifications import send_email_notification
from .qr_utils import generate_qr_code
from .export_utils import export_to_excel

# Define what should be available when importing from dashboard.utils
__all__ = [
    'calculate_experience',
    'calculate_age',
    'format_date',
    'get_academic_year',
    'generate_pdf_from_html',
    'merge_pdfs',
    'extract_text_from_pdf',
    'validate_faculty_data',
    'validate_student_data',
    'send_email_notification',
    'generate_qr_code',
    'export_to_excel',
]