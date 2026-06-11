"""Stable entry points for student and faculty PDF generation."""

from .assets import (
    FACULTY_PDF_TEMPLATE,
    STUDENT_PDF_TEMPLATE,
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
    'STUDENT_PDF_TEMPLATE',
    'build_faculty_profile_context',
    'build_faculty_profile_pdf_bytes',
    'generate_student_profile_pdf',
    'generate_student_profile_pdf_bytes',
    'persist_faculty_profile_pdf',
]
