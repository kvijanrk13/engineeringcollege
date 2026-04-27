#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Student
from django.template.loader import render_to_string
from datetime import datetime
import traceback

def test_student_pdf(student_id=17):
    try:
        student = Student.objects.get(id=student_id)
        print(f"Student found: {student.student_name} ({student.ht_no})")
        
        # Minimal context
        context = {
            'student': student,
            'current_date': datetime.now(),
            'local_photo_path': None,
            'anurag_header_url': None,
        }
        
        # Render HTML
        html_string = render_to_string('dashboard/student_pdf.html', context)
        print("HTML rendered successfully")
        
        # Save HTML
        with open('test_student_output.html', 'w', encoding='utf-8') as f:
            f.write(html_string)
        print("HTML saved to test_student_output.html")
        
        # Test ReportLab directly (the fallback)
        print("\nTesting ReportLab PDF generation...")
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Simple test content
        story.append(Paragraph(f"Student Profile: {student.student_name}", styles['Title']))
        story.append(Paragraph(f"Hall Ticket No: {student.ht_no}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Add a simple table
        data = [
            ['Field', 'Value'],
            ['Name', student.student_name],
            ['Father Name', student.father_name],
            ['Email', student.email or 'N/A'],
        ]
        t = Table(data, colWidths=[2*72, 4*72])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save PDF
        output_file = f"test_student_{student.ht_no}.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        print(f"SUCCESS: ReportLab PDF saved to {output_file} ({len(pdf_bytes)} bytes)")
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_student_pdf(21)  # Use existing student ID
    input("\nPress Enter to exit...")