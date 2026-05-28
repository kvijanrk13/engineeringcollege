"""Stable entry points for student and faculty PDF generation."""

from .assets import (
    FACULTY_PDF_TEMPLATE,
    PDF_HEADER_IMAGE_FILENAME,
    STUDENT_PDF_TEMPLATE,
    get_pdf_header_image_path,
)
from .faculty import (
    build_faculty_profile_context,
    build_faculty_profile_pdf_bytes,
    persist_faculty_profile_pdf,
)
from .student import (
    generate_student_profile_pdf,
    generate_student_profile_pdf_bytes,
)

__all__ = [
    'FACULTY_PDF_TEMPLATE',
    'PDF_HEADER_IMAGE_FILENAME',
    'STUDENT_PDF_TEMPLATE',
    'build_faculty_profile_context',
    'build_faculty_profile_pdf_bytes',
    'generate_student_profile_pdf',
    'generate_student_profile_pdf_bytes',
    'get_pdf_header_image_path',
    'persist_faculty_profile_pdf',
]
