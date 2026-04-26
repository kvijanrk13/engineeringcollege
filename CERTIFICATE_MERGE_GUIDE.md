# Certificate Merge Quick Reference Guide

## How It Works

The student and faculty certificate merge system automatically combines all uploaded certificates (both images and PDFs) from Cloudinary into a single comprehensive PDF file along with the profile information.

## Key Components

### 1. **collect_student_files(student)**
Downloads all student certificates and photo from Cloudinary or local storage.

**Returns:**
- `photo_path`: Path to student's photo
- `image_files`: List of image certificate paths
- `pdf_files`: List of PDF certificate paths  
- `temp_files`: List of temporary files created (for cleanup)

### 2. **download_remote_asset(url, default_suffix='.pdf')**
Downloads a single file from a URL (especially Cloudinary URLs) with fallback mechanisms.

**Returns:**
- `temp_file_path`: Path to downloaded temporary file
- `is_pdf`: Boolean indicating if file is PDF

**Features:**
- Handles Cloudinary 401/403 errors
- Auto-detects file type
- Retries with alternative resource types
- 30-second timeout protection

### 3. **merge_student_certificates_with_pdf_bytes(pdf_bytes, student)**
Merges a student PDF with all their certificates into single PDF.

**Input:**
- `pdf_bytes`: The main student profile PDF as bytes
- `student`: Student object with certificate references

**Output:**
- `merged_pdf_bytes`: Combined PDF as bytes ready for download/upload

**Process:**
1. Creates new PDF writer
2. Adds main profile PDF
3. Downloads all certificates
4. Converts images to PDF pages
5. Merges all pages
6. Cleans up temporary files
7. Returns final PDF

### 4. **generate_student_pdf(student, return_bytes=False)**
Complete student PDF generation with merged certificates.

**Parameters:**
- `student`: Student object
- `return_bytes`: If True, returns PDF as bytes; if False, returns URL

**Returns:**
- PDF bytes (if return_bytes=True)
- Cloudinary URL (if return_bytes=False)

## Usage Workflow

### Step 1: View/Generate Student PDF
```
Navigate to: /student/<id>/pdf/
Triggers: generate_student_pdf_view()
```

### Step 2: Automatic Certificate Collection
```
- Function: collect_student_files()
- Downloads from:
  * Cloudinary URLs
  * Local file storage
- Handles both images and PDFs
```

### Step 3: Certificate Merging
```
- Function: merge_student_certificates_with_pdf_bytes()
- Converts images to PDF pages
- Maintains proper formatting
- Creates single unified PDF
```

### Step 4: Upload to Cloudinary (Optional)
```
- Saves merged PDF to Cloudinary
- Stores URL in student.pdf_url
- Updates student record
```

## Certificate Types Supported

1. **Achievement Certificate**
   - Field: `cert_achieve` / `cert_achieve_url`
   - Use: Academic achievements, awards, honors

2. **Internship Certificate**
   - Field: `cert_intern` / `cert_intern_url`
   - Use: Internship experience documentation

3. **Course Certificate**
   - Field: `cert_courses` / `cert_courses_url`
   - Use: Online/offline course completion

4. **SDP Certificate**
   - Field: `cert_sdp` / `cert_sdp_url`
   - Use: Skill development programs

5. **Extra-Curricular Certificate**
   - Field: `cert_extra` / `cert_extra_url`
   - Use: Sports, cultural, club activities

6. **Placement Certificate**
   - Field: `cert_placement` / `cert_placement_url`
   - Use: Job placement evidence

7. **National Exam Certificate**
   - Field: `cert_national` / `cert_national_url`
   - Use: National level exam certifications

## File Format Support

### Images
- ✅ JPG / JPEG
- ✅ PNG
- ✅ GIF
- ✅ BMP
- ✅ WEBP (converted to RGB)

### Documents
- ✅ PDF
- ✅ DOC/DOCX (if converted to PDF)
- ✅ TXT (if converted to PDF)

### Automatic Conversion
- All images are converted to PDF pages
- Maintains aspect ratio
- Centers content on page
- Preserves quality

## Error Handling Examples

### Scenario 1: Cloudinary Download Fails
```
Initial attempt: https://res.cloudinary.com/.../raw/upload/cert.pdf
Fallback 1: Try image/upload/ instead of raw/upload/
Fallback 2: Try Cloudinary API to get fresh URL
Fallback 3: Try manual URL construction
Final: Skip file if all attempts fail, continue with others
```

### Scenario 2: Image File Corrupted
```
Attempt: Open image file
Error: Image library throws exception
Handling: Log warning, skip this file, continue with next
Result: Merge completes with available files
```

### Scenario 3: PDF Invalid
```
Attempt: Read PDF headers
Check: Verify %PDF magic bytes
If invalid: Skip file, continue processing
Result: Partial merge with valid files
```

## Performance Tips

1. **Batch Processing**
   - Merge multiple students' PDFs in batch
   - Use background job queues
   - Schedule during off-peak hours

2. **Caching**
   - Cache downloaded files temporarily
   - Reuse for multiple merges
   - Clean up after batch completion

3. **Network Optimization**
   - Use connection pooling
   - Set appropriate timeouts
   - Retry on transient failures

4. **Storage Management**
   - Delete temporary files promptly
   - Monitor disk space
   - Implement cleanup jobs

## Troubleshooting Checklist

### Certificates Not Showing in Merged PDF

**Check:**
- [ ] Student has certificates uploaded
- [ ] Certificates are in Cloudinary or local storage
- [ ] Certificate field names are correct
- [ ] File permissions allow reading
- [ ] Cloudinary credentials are valid
- [ ] Files aren't corrupted

**Debug:**
```python
# Check if certificates exist
student = Student.objects.get(id=student_id)
print(f"Achievement cert: {student.cert_achieve}")
print(f"Achievement URL: {student.cert_achieve_url}")

# Check if they're accessible
photo_path, images, pdfs, temp = collect_student_files(student)
print(f"Collected images: {len(images)}")
print(f"Collected PDFs: {len(pdfs)}")
```

### Merge Process Fails

**Check:**
- [ ] PDF generation succeeds on its own
- [ ] Individual certificates download properly
- [ ] Storage space available for temp files
- [ ] No file permission issues
- [ ] Libraries installed (reportlab, pypdf, Pillow)

**Debug:**
```python
# Test PDF generation
pdf_bytes = generate_student_pdf(student, return_bytes=True)
print(f"PDF size: {len(pdf_bytes)} bytes")

# Test merge separately
merged = merge_student_certificates_with_pdf_bytes(pdf_bytes, student)
print(f"Merged PDF size: {len(merged)} bytes")
```

### Cloudinary Upload Issues

**Check:**
- [ ] Cloudinary credentials in settings
- [ ] API rate limits not exceeded
- [ ] Storage quota available
- [ ] Network connectivity
- [ ] File size within limits

**Debug:**
```python
import cloudinary
cloudinary.api.ping()  # Test connection
usage = cloudinary.api.usage()  # Check storage
print(f"Storage used: {usage['resources_count']}")
```

## Configuration

### Required Environment Variables
```
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Django Settings
```python
CLOUDINARY_CONFIGURED = True
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
```

## Best Practices

1. **Always Validate Input**
   - Check student exists
   - Verify certificate URLs
   - Validate file formats

2. **Handle Failures Gracefully**
   - Continue if individual files fail
   - Log all errors
   - Return partial results when possible

3. **Clean Up Resources**
   - Always clean temporary files
   - Even in error cases
   - Monitor disk usage

4. **Monitor Performance**
   - Log merge duration
   - Track success rates
   - Monitor storage usage

5. **Security**
   - Validate file types
   - Check file sizes
   - Sanitize file names
   - Use secure URLs

## API Reference

### View Function
```
URL: /student/<student_id>/pdf/
Method: GET
Auth: Required (student session or admin)
Returns: PDF file download
```

### Merge Function
```
merge_student_certificates_with_pdf_bytes(pdf_bytes, student)
Input: PDF bytes, Student object
Output: Merged PDF bytes or None
Errors: Logged, returns None on failure
```

### Collection Function
```
collect_student_files(student)
Returns: (photo_path, image_files, pdf_files, temp_files)
Errors: Returns empty lists if nothing found
```

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Certificates missing | Not uploaded | Upload via form |
| Download fails | Cloudinary auth error | Check credentials |
| Merge hangs | Large files | Increase timeout |
| Temp files not deleted | Cleanup error | Manual cleanup |
| PDF corrupt | Invalid file | Re-upload |
| Size too large | Too many certs | Compress files |

## Support & Feedback

For issues:
1. Check logs: `django_log.txt`
2. Enable DEBUG mode in settings
3. Test individual functions
4. Check Cloudinary status
5. Contact administrator

---

**Last Updated**: April 2026
**Version**: 1.0.0
**Supported Django**: 3.2+
**Supported Python**: 3.8+

