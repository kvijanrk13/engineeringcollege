# Certificate Merge API Examples

## Overview
This document provides practical examples of how to use the certificate merge functionality in your Django application.

## Python Code Examples

### Example 1: Generate Student PDF with Merged Certificates

```python
from dashboard.models import Student
from dashboard.views import generate_student_pdf

# Get a student
student = Student.objects.get(ht_no='23C11A1201')

# Generate PDF with all certificates merged
pdf_url = generate_student_pdf(student)
print(f"PDF generated and uploaded: {pdf_url}")

# Save URL to student record
student.pdf_url = pdf_url
student.save()
```

### Example 2: Get PDF Bytes Instead of URL

```python
from dashboard.models import Student
from dashboard.views import generate_student_pdf

student = Student.objects.get(id=1)

# Get PDF as bytes for immediate download
pdf_bytes = generate_student_pdf(student, return_bytes=True)

# Send as response
from django.http import HttpResponse
response = HttpResponse(pdf_bytes, content_type='application/pdf')
response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
return response
```

### Example 3: Manual Certificate Collection

```python
from dashboard.models import Student
from dashboard.views import collect_student_files

student = Student.objects.get(id=1)

# Collect all certificates
photo_path, image_files, pdf_files, temp_files = collect_student_files(student)

print(f"Photo: {photo_path}")
print(f"Image certificates: {len(image_files)}")
print(f"PDF certificates: {len(pdf_files)}")

# Do something with collected files...

# Important: Clean up temporary files
import os
for temp_file in temp_files:
    try:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except:
        pass
```

### Example 4: Merge Certificates with Custom PDF

```python
from dashboard.models import Student
from dashboard.views import merge_student_certificates_with_pdf_bytes
import io

student = Student.objects.get(id=1)

# Create custom PDF (example with reportlab)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)
c.drawString(100, 750, f"Student: {student.student_name}")
c.drawString(100, 730, f"Hall Ticket: {student.ht_no}")
c.showPage()
c.save()

# Get PDF bytes
custom_pdf_bytes = buffer.getvalue()

# Merge with certificates
merged_pdf_bytes = merge_student_certificates_with_pdf_bytes(custom_pdf_bytes, student)

# Save or upload
if merged_pdf_bytes:
    with open(f'student_{student.ht_no}.pdf', 'wb') as f:
        f.write(merged_pdf_bytes)
    print("Merged PDF saved successfully!")
else:
    print("Error during merge")
```

### Example 5: Download and Process Remote Asset

```python
from dashboard.views import download_remote_asset

# Download a certificate from Cloudinary
url = "https://res.cloudinary.com/your-cloud/image/upload/student_cert.pdf"
temp_path, is_pdf = download_remote_asset(url)

if temp_path:
    print(f"Downloaded to: {temp_path}")
    print(f"Is PDF: {is_pdf}")
    
    # Process the file
    if is_pdf:
        from pypdf import PdfReader
        reader = PdfReader(temp_path)
        print(f"PDF has {len(reader.pages)} pages")
    else:
        from PIL import Image
        img = Image.open(temp_path)
        print(f"Image size: {img.size}")
    
    # Clean up
    import os
    os.remove(temp_path)
```

### Example 6: Batch Process Multiple Students

```python
from dashboard.models import Student
from dashboard.views import generate_student_pdf

# Get all students
students = Student.objects.all()

# Process each student
successful = 0
failed = 0

for student in students:
    try:
        pdf_url = generate_student_pdf(student)
        if pdf_url:
            successful += 1
            print(f"✓ {student.student_name}")
        else:
            failed += 1
            print(f"✗ {student.student_name} - PDF generation failed")
    except Exception as e:
        failed += 1
        print(f"✗ {student.student_name} - {str(e)}")

print(f"\nResults: {successful} successful, {failed} failed")
```

### Example 7: Conditional Certificate Merge

```python
from dashboard.models import Student
from dashboard.views import merge_student_certificates_with_pdf_bytes
import io

student = Student.objects.get(id=1)

# Check if student has certificates worth merging
has_certificates = bool(
    student.cert_achieve or student.cert_intern or student.cert_courses or
    student.cert_sdp or student.cert_extra or student.cert_placement or
    student.cert_national or
    student.cert_achieve_url or student.cert_intern_url or 
    student.cert_courses_url or student.cert_sdp_url or 
    student.cert_extra_url or student.cert_placement_url or 
    student.cert_national_url
)

if has_certificates:
    # Generate profile PDF
    profile_pdf_bytes = b'...'  # Your profile PDF bytes
    
    # Merge with certificates
    merged = merge_student_certificates_with_pdf_bytes(profile_pdf_bytes, student)
    
    if merged:
        student.pdf_url = upload_to_cloudinary(merged)
        student.save()
        print("Merged PDF saved!")
else:
    print("No certificates to merge")
```

### Example 8: Error Recovery Example

```python
from dashboard.views import download_remote_asset, merge_student_certificates_with_pdf_bytes
from dashboard.models import Student

student = Student.objects.get(id=1)

# Generate profile PDF
try:
    profile_pdf_bytes = b'...'  # Your PDF generation
except Exception as e:
    print(f"Profile PDF generation failed: {e}")
    profile_pdf_bytes = None

# Attempt merge with error handling
if profile_pdf_bytes:
    try:
        merged = merge_student_certificates_with_pdf_bytes(profile_pdf_bytes, student)
        
        if merged:
            print(f"Success! Merged PDF size: {len(merged)} bytes")
        else:
            print("Merge failed - returned None")
            
    except Exception as e:
        print(f"Merge error: {e}")
        # Continue with profile PDF only
        merged = profile_pdf_bytes
else:
    # If no profile PDF, try collecting and merging certificates only
    try:
        photo_path, images, pdfs, temps = collect_student_files(student)
        if pdfs or images:
            print("Certificates available for manual processing")
    except Exception as e:
        print(f"Certificate collection failed: {e}")
```

## Django View Examples

### Example 1: Custom Merge View

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from dashboard.models import Student
from dashboard.views import generate_student_pdf

@login_required
def custom_pdf_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    try:
        # Generate PDF with merged certificates
        pdf_bytes = generate_student_pdf(student, return_bytes=True)
        
        if pdf_bytes:
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
            return response
        else:
            messages.error(request, "Failed to generate PDF")
            return redirect('student_detail', student_id=student_id)
            
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('student_detail', student_id=student_id)
```

### Example 2: Batch Generation View

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from dashboard.models import Student
from dashboard.views import generate_student_pdf

@login_required
def batch_pdf_generation(request):
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        
        if not student_ids:
            messages.error(request, 'No students selected')
            return redirect('student_list')
        
        successful = []
        failed = []
        
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                pdf_url = generate_student_pdf(student)
                
                if pdf_url:
                    successful.append(student.student_name)
                else:
                    failed.append(student.student_name)
                    
            except Exception as e:
                failed.append(f"{student.student_name}: {str(e)}")
        
        if successful:
            messages.success(request, f"Generated PDFs for {len(successful)} students")
        if failed:
            messages.warning(request, f"Failed for {len(failed)} students")
        
        return redirect('student_list')
    
    return render(request, 'batch_pdf_generation.html')
```

### Example 3: AJAX Merge Request

```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from dashboard.models import Student
from dashboard.views import generate_student_pdf
import logging

logger = logging.getLogger(__name__)

@login_required
@require_POST
def ajax_generate_pdf(request):
    try:
        student_id = request.POST.get('student_id')
        student = Student.objects.get(id=student_id)
        
        # Generate PDF
        pdf_url = generate_student_pdf(student)
        
        if pdf_url:
            return JsonResponse({
                'success': True,
                'pdf_url': pdf_url,
                'student_name': student.student_name,
                'message': 'PDF generated successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate PDF'
            })
            
    except Student.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Student not found'
        }, status=404)
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

## Template Examples

### Example 1: Download Button

```html
<!-- student_detail.html -->
<div class="pdf-section">
    <h3>Download Profile with Certificates</h3>
    
    {% if student.pdf_url %}
        <p>PDF generated on: {{ student.pdf_generation_time }}</p>
        <a href="{{ student.pdf_url }}" class="btn btn-primary" target="_blank">
            Download PDF
        </a>
    {% else %}
        <p>PDF not yet generated</p>
        <form method="POST" action="{% url 'generate_student_pdf' student.id %}">
            {% csrf_token %}
            <button type="submit" class="btn btn-success">
                Generate PDF with Certificates
            </button>
        </form>
    {% endif %}
</div>
```

### Example 2: Progress Indicator

```html
<!-- batch_generation.html -->
<div id="progress-container" style="display:none;">
    <div class="progress">
        <div id="progress-bar" class="progress-bar" style="width: 0%"></div>
    </div>
    <p id="status-text">Generating PDFs...</p>
</div>

<script>
document.getElementById('batch-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    var formData = new FormData(this);
    var container = document.getElementById('progress-container');
    container.style.display = 'block';
    
    fetch('{% url "ajax_generate_pdf" %}', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('progress-bar').style.width = '100%';
            document.getElementById('status-text').textContent = 'Complete!';
        } else {
            document.getElementById('status-text').textContent = 'Error: ' + data.error;
        }
    });
});
</script>
```

## Troubleshooting Examples

### Example 1: Debug PDF Generation

```python
from django.core.management.base import BaseCommand
from dashboard.models import Student
from dashboard.views import generate_student_pdf, collect_student_files
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug PDF generation for a student'
    
    def add_arguments(self, parser):
        parser.add_argument('student_id', type=int)
    
    def handle(self, *args, **options):
        student_id = options['student_id']
        student = Student.objects.get(id=student_id)
        
        self.stdout.write(f"Student: {student.student_name}")
        
        # Check certificates
        photo_path, images, pdfs, temps = collect_student_files(student)
        self.stdout.write(f"Photo: {photo_path}")
        self.stdout.write(f"Images: {len(images)}")
        self.stdout.write(f"PDFs: {len(pdfs)}")
        
        # Try generating PDF
        try:
            pdf_url = generate_student_pdf(student)
            if pdf_url:
                self.stdout.write(self.style.SUCCESS(f"PDF URL: {pdf_url}"))
            else:
                self.stdout.write(self.style.WARNING("PDF generation returned None"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
```

### Example 2: Test Cloudinary Connection

```python
from django.core.management.base import BaseCommand
import cloudinary
import cloudinary.api

class Command(BaseCommand):
    help = 'Test Cloudinary connectivity'
    
    def handle(self, *args, **options):
        try:
            result = cloudinary.api.ping()
            self.stdout.write(self.style.SUCCESS(f"Connected: {result}"))
            
            usage = cloudinary.api.usage()
            self.stdout.write(f"Resources: {usage['resources_count']}")
            self.stdout.write(f"Bytes used: {usage['bytes_used']}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
```

## Configuration Examples

### Example 1: .env File

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# PDF Generation
PDF_GENERATION_TIMEOUT=300
TEMP_FILE_CLEANUP_INTERVAL=3600

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=django_log.txt
```

### Example 2: settings.py Configuration

```python
# Cloudinary
CLOUDINARY_CONFIGURED = os.environ.get('CLOUDINARY_CONFIGURED', 'True') == 'True'
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

# PDF Generation
PDF_TIMEOUT = int(os.environ.get('PDF_GENERATION_TIMEOUT', 300))
TEMP_FILES_CLEANUP = int(os.environ.get('TEMP_FILE_CLEANUP_INTERVAL', 3600))

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'class': 'logging.FileHandler',
            'filename': 'django_log.txt',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
}
```

---

**These examples provide practical starting points for implementing certificate merge functionality in your application.**

For more detailed information, refer to:
- `CERTIFICATE_MERGE_IMPLEMENTATION.md` - Technical details
- `CERTIFICATE_MERGE_GUIDE.md` - Usage guide
- `IMPLEMENTATION_SUMMARY.md` - Overview and architecture

