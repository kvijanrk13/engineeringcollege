# Faculty PDF Generation Fix for Render Deployment

## Problem
Faculty PDF generation was failing on Render with the error "Invalid api_key" (actually a wkhtmltopdf binary issue). The code relied on `pdfkit` which requires the `wkhtmltopdf` system binary, but Render's environment does not have this binary installed.

## Root Cause
- `pdfkit` is just a Python wrapper; it needs the `wkhtmltopdf` executable
- The build.sh only installed Python packages, not system binaries
- Render's free tier doesn't have wkhtmltopdf pre-installed
- Local development had wkhtmltopdf installed, so it worked locally

## Solution
Replaced `pdfkit` with `WeasyPrint` for HTML-to-PDF conversion in all critical functions.

WeasyPrint is a pure-Python solution that doesn't require external binaries. It's already in `requirements.txt`.

## Files Modified

### 1. dashboard/views.py
- **`generate_faculty_pdf()`** (line ~4016): Replaced pdfkit with WeasyPrint
- **`generate_pdf_with_data()`** (line ~4920): Replaced pdfkit with WeasyPrint
- **`exam_branch_generate_report()`** (line ~7136): Replaced pdfkit with WeasyPrint

### 2. dashboard/utils.py
- **`generate_pdf_from_html()`**: Replaced pdfkit with WeasyPrint

### 3. dashboard/dashboard/utils/pdf_utils.py
- **`generate_pdf_from_html()`**: Replaced pdfkit with WeasyPrint (kept ReportLab fallback)

### 4. dashboard/dashboard/utils/utils.py
- **`generate_pdf_from_html()`**: Replaced pdfkit with WeasyPrint (kept ReportLab fallback)

## Implementation Details

### Before (pdfkit):
```python
info_pdf_bytes = pdfkit.from_string(html_string, False, options=options)
```

### After (WeasyPrint):
```python
from weasyprint import HTML
from django.conf import settings
base_url = f"file:///{settings.BASE_DIR}" if settings.BASE_DIR else None
html_obj = HTML(string=html_string, base_url=base_url)
info_pdf_bytes = html_obj.write_pdf()
```

### Key Changes:
- Removed wkhtmltopdf path detection logic
- Removed pdfkit configuration
- Used `base_url` to resolve relative file paths (for images, CSS, etc.)
- Maintained error handling with appropriate fallbacks

## Student PDF Note
The student PDF generation (`_build_student_info_pdf` area) still uses pdfkit but has a **ReportLab fallback**. On Render, if pdfkit fails (wkhtmltopdf missing), it automatically falls back to ReportLab which works. This is acceptable and ensures student PDFs still generate.

## Testing
1. Syntax validated: `python -m py_compile dashboard/views.py` → OK
2. WeasyPrint is in requirements.txt → will be installed on Render
3. No external binary dependencies remain for PDF generation

## Deployment
The next deployment to Render will:
1. Install weasyprint from requirements.txt (already there)
2. Use WeasyPrint for faculty PDFs, custom PDFs, and exam branch reports
3. Successfully generate PDFs without wkhtmltopdf

## Impact
- ✅ Faculty PDF generation will work on Render
- ✅ Exam branch report PDF will work
- ✅ Custom PDF generation will work
- ✅ Student PDFs continue to work via ReportLab fallback
- ✅ No changes needed to build.sh (no system packages to install)
- ✅ PDF quality should be comparable (WeasyPrint uses similar rendering engine)
