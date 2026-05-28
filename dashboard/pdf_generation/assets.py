"""PDF generation assets and template names.

Keep shared PDF filenames here so page views and templates do not own PDF
identity. Student and faculty generators should import from this module.
"""

import os

from django.conf import settings


PDF_HEADER_IMAGE_FILENAME = 'NEW ANURAG 25.png'
STUDENT_PDF_TEMPLATE = 'dashboard/student_pdf.html'
FACULTY_PDF_TEMPLATE = 'dashboard/faculty_pdf.html'


def get_pdf_header_image_path():
    return os.path.join(settings.BASE_DIR, 'static', 'images', PDF_HEADER_IMAGE_FILENAME)
