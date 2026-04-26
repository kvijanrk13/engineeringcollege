# Quick Code Reference - Certificate Merge

## Essential Code Snippets

### 1. Generate Student PDF with Certificates

```python
from dashboard.views import generate_student_pdf
from dashboard.models import Student

# Get student
student = Student.objects.get(id=1)

# Generate PDF (automatically merges all certificates)
pdf_url = generate_student_pdf(student)

# Returns: Cloudinary URL
print(f"PDF: {pdf_url}")
```

**Output:**
```
PDF: https://res.cloudinary.com/.../student_23C11A1201.pdf
```

---

### 2. Get PDF as Bytes for Download

```python
from django.http import HttpResponse
from dashboard.views import generate_student_pdf
from dashboard.models import Student

student = Student.objects.get(id=1)

# Get PDF as bytes
pdf_bytes = generate_student_pdf(student, return_bytes=True)

# Send as download
response = HttpResponse(pdf_bytes, content_type='application/pdf')
response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
return response
```

---

### 3. Check What Files Will Be Merged

```python
from dashboard.views import collect_student_files
from dashboard.models import Student
import os

student = Student.objects.get(id=1)

# Collect all files
photo_path, image_files, pdf_files, temp_files = collect_student_files(student)

# Print what will be merged
print(f"Photo: {os.path.basename(photo_path) if photo_path else 'None'}")
print(f"Image Certificates: {len(image_files)}")
for img in image_files:
    print(f"  - {os.path.basename(img)}")
print(f"PDF Certificates: {len(pdf_files)}")
for pdf in pdf_files:
    print(f"  - {os.path.basename(pdf)}")

# IMPORTANT: Clean up temp files
for temp_file in temp_files:
    try:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except:
        pass
```

**Output:**
```
Photo: student_photo.jpg
Image Certificates: 2
  - cert_achieve.png
  - cert_extra.jpg
PDF Certificates: 3
  - cert_intern.pdf
  - cert_courses.pdf
  - cert_placement.pdf
```

---

### 4. Merge Specific PDF with Certificates

```python
from dashboard.views import merge_student_certificates_with_pdf_bytes
from dashboard.models import Student

student = Student.objects.get(id=1)

# Your custom PDF as bytes
custom_pdf_bytes = b'%PDF-1.4...'  # Your PDF content

# Merge with student certificates
merged_pdf_bytes = merge_student_certificates_with_pdf_bytes(
    custom_pdf_bytes, 
    student
)

# Check result
if merged_pdf_bytes:
    print(f"Merged PDF size: {len(merged_pdf_bytes)} bytes")
    
    # Save to file
    with open(f'student_{student.ht_no}_merged.pdf', 'wb') as f:
        f.write(merged_pdf_bytes)
else:
    print("Merge failed")
```

---

### 5. Download File from Cloudinary

```python
from dashboard.views import download_remote_asset
import os

# URL to download
url = "https://res.cloudinary.com/.../certificate.pdf"

# Download to temp file
temp_path, is_pdf = download_remote_asset(url, default_suffix='.pdf')

if temp_path:
    print(f"Downloaded to: {temp_path}")
    print(f"File is PDF: {is_pdf}")
    
    # Do something with file...
    
    # Clean up
    os.remove(temp_path)
else:
    print("Download failed")
```

---

### 6. Batch Generate PDFs for Multiple Students

```python
from dashboard.views import generate_student_pdf
from dashboard.models import Student
from django.db.models import Count

# Get students with certificates
students_with_certs = Student.objects.filter(
    Q(cert_achieve__isnull=False) | 
    Q(cert_intern__isnull=False) |
    Q(cert_courses__isnull=False)
)

# Process each
results = {'success': 0, 'failed': 0}

for student in students_with_certs[:100]:  # Limit to 100
    try:
        pdf_url = generate_student_pdf(student)
        if pdf_url:
            results['success'] += 1
            print(f"✓ {student.student_name}")
        else:
            results['failed'] += 1
            print(f"✗ {student.student_name} - No PDF generated")
    except Exception as e:
        results['failed'] += 1
        print(f"✗ {student.student_name} - {str(e)}")

print(f"\nResults: {results['success']} OK, {results['failed']} Failed")
```

---

### 7. Django View Function

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.models import Student
from dashboard.views import generate_student_pdf

@login_required
def download_student_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    try:
        # Generate PDF with merged certificates
        pdf_bytes = generate_student_pdf(student, return_bytes=True)
        
        if not pdf_bytes:
            messages.error(request, "Failed to generate PDF")
            return redirect('student_detail', student_id=student_id)
        
        # Return as download
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
        return response
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('student_detail', student_id=student_id)
```

---

### 8. Management Command for Batch Processing

```python
from django.core.management.base import BaseCommand
from dashboard.models import Student
from dashboard.views import generate_student_pdf
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate PDFs for all students with certificates'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Number of students to process'
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        
        students = Student.objects.all()[:limit]
        
        success = 0
        failed = 0
        
        for student in students:
            try:
                pdf_url = generate_student_pdf(student)
                if pdf_url:
                    success += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {student.student_name}")
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.WARNING(f"✗ {student.student_name} - No PDF")
                    )
            except Exception as e:
                failed += 1
                logger.error(f"Error: {e}")
                self.stdout.write(
                    self.style.ERROR(f"✗ {student.student_name} - {str(e)}")
                )
        
        self.stdout.write(f"\nTotal: {success} OK, {failed} Failed")
```

**Usage:**
```bash
python manage.py generate_student_pdfs --limit 50
```

---

### 9. Error Handling Best Practice

```python
from dashboard.views import generate_student_pdf, collect_student_files
from dashboard.models import Student
import logging
import traceback

logger = logging.getLogger(__name__)

def safe_pdf_generation(student_id):
    """Generate PDF with comprehensive error handling"""
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        logger.error(f"Student not found: {student_id}")
        return None
    
    try:
        # Check for certificates first
        photo, images, pdfs, temps = collect_student_files(student)
        
        if not photo and not images and not pdfs:
            logger.warning(f"No files to merge for student {student.ht_no}")
        
        # Generate PDF
        pdf_url = generate_student_pdf(student)
        
        if pdf_url:
            logger.info(f"PDF generated for {student.ht_no}: {pdf_url}")
            return pdf_url
        else:
            logger.error(f"PDF generation returned None for {student.ht_no}")
            return None
            
    except Exception as e:
        logger.error(f"PDF generation failed for {student.ht_no}: {e}")
        logger.error(traceback.format_exc())
        return None
```

---

### 10. Configuration Template

```python
# settings.py

import os
from dotenv import load_dotenv

load_dotenv()

# Cloudinary Configuration
CLOUDINARY_CONFIGURED = True

CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# PDF Configuration
PDF_GENERATION_TIMEOUT = 300  # seconds
TEMP_FILE_CLEANUP_INTERVAL = 3600  # seconds

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django_log.txt',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

**Environment variables (.env):**
```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

### 11. Testing Individual Functions

```python
from dashboard.views import (
    download_remote_asset,
    collect_student_files,
    merge_student_certificates_with_pdf_bytes
)
from dashboard.models import Student

def test_certificate_merge():
    """Test certificate merge functionality"""
    
    # Get test student
    student = Student.objects.get(id=1)
    print(f"Testing with: {student.student_name}")
    
    # Test 1: Collect files
    print("\n[TEST 1] Collecting student files...")
    photo, images, pdfs, temps = collect_student_files(student)
    print(f"  Photo: {bool(photo)}")
    print(f"  Images: {len(images)}")
    print(f"  PDFs: {len(pdfs)}")
    
    # Test 2: Download single file
    if pdfs:
        print(f"\n[TEST 2] Testing file download...")
        url = student.cert_achieve_url
        if url:
            path, is_pdf = download_remote_asset(url)
            print(f"  Downloaded: {bool(path)}")
            print(f"  Is PDF: {is_pdf}")
    
    # Test 3: Merge (if we have a PDF)
    print(f"\n[TEST 3] Testing merge...")
    profile_pdf = b'%PDF-1.4'  # Dummy PDF
    merged = merge_student_certificates_with_pdf_bytes(profile_pdf, student)
    if merged:
        print(f"  Merge successful: {len(merged)} bytes")
    else:
        print(f"  Merge failed")
    
    print("\n[DONE] All tests completed")
```

---

### 12. URL Configuration

```python
# urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # PDF generation
    path('student/<int:student_id>/pdf/', 
         views.generate_student_pdf_view, 
         name='student_pdf'),
    
    path('faculty/<int:faculty_id>/pdf/', 
         views.generate_faculty_pdf, 
         name='faculty_pdf'),
    
    # Certificate merge
    path('student/<int:student_id>/merge-certs/', 
         views.merge_student_certificates, 
         name='merge_student_certs'),
    
    path('faculty/<int:faculty_id>/merge-certs/', 
         views.merge_faculty_certificates, 
         name='merge_faculty_certs'),
    
    # Download
    path('student/<int:student_id>/download-pdf/', 
         views.download_pdf, 
         name='download_pdf'),
]
```

---

## Common Patterns

### Pattern 1: Try/Catch with Logging

```python
try:
    result = generate_student_pdf(student)
    logger.info(f"Success: {result}")
except Exception as e:
    logger.error(f"Failed: {e}")
    # Fall back to something
```

### Pattern 2: Check and Cleanup

```python
temp_files = []
try:
    # Do work
    pass
finally:
    # Always cleanup
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except:
            pass
```

### Pattern 3: Batch Processing

```python
for item in items:
    try:
        process(item)
    except:
        continue  # Keep going
```

---

## Command Line Usage

### Generate PDF for One Student
```bash
python manage.py shell
>>> from dashboard.views import generate_student_pdf
>>> from dashboard.models import Student
>>> s = Student.objects.get(id=1)
>>> pdf = generate_student_pdf(s)
>>> print(pdf)
```

### Debug Certificate Collection
```bash
python manage.py shell
>>> from dashboard.views import collect_student_files
>>> from dashboard.models import Student
>>> s = Student.objects.get(id=1)
>>> photo, imgs, pdfs, temps = collect_student_files(s)
>>> print(f"Images: {len(imgs)}, PDFs: {len(pdfs)}")
```

---

## Troubleshooting Commands

### Check Cloudinary Connection
```python
import cloudinary
cloudinary.api.ping()
cloudinary.api.usage()
```

### View Recent Logs
```bash
tail -f django_log.txt | grep -i "certificate\|merge"
```

### Clear Temp Files
```bash
find /tmp -name "tmp*" -mtime +1 -delete
```

---

## Best Practices Summary

✓ Always use try/except around merge operations
✓ Clean up temporary files in finally block
✓ Log all operations for debugging
✓ Check if files exist before processing
✓ Use proper error messages for users
✓ Test with sample data first
✓ Monitor disk space for temp files
✓ Use batching for large operations
✓ Implement retry logic for network failures
✓ Return meaningful error messages

---

**Quick Reference Version:** 1.0.0
**Last Updated:** April 2026

**Need More Help?** See documentation files:
- API_EXAMPLES.md for more examples
- README_CERTIFICATE_MERGE.md for overview
- CERTIFICATE_MERGE_GUIDE.md for troubleshooting

