# dashboard/utils/pdf_utils.py
from pypdf import PdfMerger, PdfReader, PdfWriter
import tempfile
import os


def generate_pdf_from_html(html_string, output_path=None):
    """Generate PDF from HTML string"""
    try:
        import pdfkit
        if output_path:
            pdfkit.from_string(html_string, output_path)
            return output_path
        else:
            pdf_bytes = pdfkit.from_string(html_string, False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                return tmp.name
    except ImportError:
        # Fallback to reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        if not output_path:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            output_path = tmp.name
            tmp.close()

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(html_string.replace('\n', '<br/>'), styles['Normal'])]
        doc.build(story)
        return output_path


def merge_pdfs(pdf_list, output_path=None):
    """Merge multiple PDF files"""
    merger = PdfMerger()
    temp_files = []

    for pdf in pdf_list:
        if pdf:
            merger.append(pdf)

    if output_path:
        merger.write(output_path)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            merger.write(tmp.name)
            output_path = tmp.name
            temp_files.append(output_path)

    merger.close()
    return output_path, temp_files


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"