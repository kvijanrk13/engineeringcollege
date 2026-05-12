# Student Profile Management Guide

## Overview
This system automatically initializes new student profiles with proper certificate field structure. All new students automatically get 7 certificate slots ready for photos and documents.

## Quick Start

### 1. Create a Single Student
```bash
python manage.py create_student \
  --ht-no=23C11A1220 \
  --name="Student Twenty" \
  --email=student20@college.edu \
  --phone=9876543220 \
  --year=4 \
  --sem=7
```

### 2. Create Students from CSV File
```bash
python manage.py create_student --from-csv=students.csv
```

**CSV Format (required columns):**
```
ht_no,student_name,email,phone,year,sem,cgpa
23C11A1220,STUDENT TWENTY,student20@college.edu,9876543220,4,7,8.0
23C11A1221,STUDENT TWENTY-ONE,student21@college.edu,9876543221,3,5,7.8
```

### 3. Create Sample Students
```bash
python manage.py create_student --sample
```

This creates 3 sample students for testing.

### 4. List All Students
```bash
python manage.py create_student --list
```

### 5. Verify Student Structures
```bash
python manage.py create_student --verify
```

## Student Certificate Slots

Each student automatically has 7 certificate slots available:

| Slot | Field | Description |
|------|-------|-------------|
| 1 | `cert_achieve` | Achievement Certificates |
| 2 | `cert_intern` | Internship Certificates |
| 3 | `cert_courses` | Course Certificates |
| 4 | `cert_sdp` | SDP/Training Certificates |
| 5 | `cert_extra` | Extra/Miscellaneous Certificates |
| 6 | `cert_placement` | Placement/Job Certificates |
| 7 | `cert_national` | National Level Certificates |

Each slot has:
- A **file field** for local uploads (e.g., `cert_achieve`)
- A **URL field** for Cloudinary URLs (e.g., `cert_achieve_url`)

## Automatic Initialization (Django Signals)

When a new student is created, the system automatically:

1. ✓ Initializes all 7 certificate field slots
2. ✓ Sets up photo field with local and URL options
3. ✓ Prepares PDF generation fields
4. ✓ Logs the creation for audit trail
5. ✓ Tracks any changes to the student record

**Signal Handler Location:** `dashboard/signals.py`

### Signal Features:
- **`auto_initialize_student_profile`**: Runs on student creation
  - Verifies all certificate fields exist
  - Logs student profile creation
  - Confirms 7 certificate slots are ready
  
- **`track_student_changes`**: Runs on student updates
  - Tracks changes to name, photo, and certificates
  - Maintains audit trail for compliance

## Programmatic Creation

### Python Script
```python
from dashboard.models import Student

# Create single student
student, created = Student.objects.get_or_create(
    ht_no='23C11A1220',
    defaults={
        'student_name': 'STUDENT TWENTY',
        'email': 'student20@college.edu',
        'student_phone': '9876543220',
        'year': 4,
        'sem': 7,
    }
)

if created:
    print(f"✓ Created: {student.student_name}")
else:
    print(f"⚠ Already exists: {student.student_name}")
```

### Bulk Creation
```python
from dashboard.models import Student

students_data = [
    {
        'ht_no': '23C11A1220',
        'student_name': 'STUDENT TWENTY',
        'email': 'student20@college.edu',
        'year': 4,
        'sem': 7,
    },
    # Add more students...
]

for data in students_data:
    Student.objects.get_or_create(
        ht_no=data['ht_no'],
        defaults=data
    )
```

## Certificate Upload System

Once a student is created, they can upload:

### Student Dashboard
- Access: `/student-login/` → `/student-dashboard/`
- Upload photo
- Upload certificates to any of the 7 slots
- Generate merged PDF with all certificates

### Admin Dashboard
- Manage all student records
- Upload on behalf of students
- View certificate status
- Generate PDFs

## PDF Generation

When student has photo + certificates:
1. Photo is added as first page
2. Certificates are merged in order
3. Final PDF uploaded to Cloudinary
4. URL saved in student record

**Merge Endpoint:** `POST /merge-student-certificates/<student_id>/`

## Data Structure

### Student Model Fields
```python
# Basic Information
ht_no                  # Unique identifier (e.g., 23C11A1215)
student_name          # Full name
email                 # Email address
student_phone         # Phone number
year                  # Year of study (1-4)
sem                   # Semester (1-8)
cgpa                  # CGPA

# Photo (2 options)
photo                 # Local file upload
photo_url            # Cloudinary URL

# Certificates (7 slots x 2 options each)
cert_achieve         # Local file
cert_achieve_url     # Cloudinary URL
cert_intern          # Local file
cert_intern_url      # Cloudinary URL
cert_courses         # Local file
cert_courses_url     # Cloudinary URL
cert_sdp             # Local file
cert_sdp_url         # Cloudinary URL
cert_extra           # Local file
cert_extra_url       # Cloudinary URL
cert_placement       # Local file
cert_placement_url   # Cloudinary URL
cert_national        # Local file
cert_national_url    # Cloudinary URL

# PDF Generation
pdf_file             # Generated merged PDF
pdf_url              # Cloudinary URL for PDF
pdf_generated        # Boolean flag
pdf_generation_time  # Timestamp
```

## Troubleshooting

### Q: I created a student but they don't appear in the list
**A:** Run verification command:
```bash
python manage.py create_student --verify
```

### Q: Student created but HT No is wrong
**A:** HT No is unique and cannot be changed directly. You must delete the student and recreate with correct HT No.

### Q: How to delete a student
**A:** Using Django shell:
```bash
python manage.py shell
>>> from dashboard.models import Student
>>> student = Student.objects.get(ht_no='23C11A1215')
>>> student.delete()
```

### Q: Certificate upload not showing in student dashboard
**A:** Verify:
1. Student has photo or certificates
2. Check browser console for JavaScript errors
3. Check Django logs for backend errors

## API Endpoints for Student Management

### List Students (Admin)
```
GET /admin/dashboard/student/
```

### View Student Detail
```
GET /student/<student_id>/
```

### Merge Certificates
```
POST /merge-student-certificates/<student_id>/
```

## Integration Points

### With Django Admin
Students can be managed via:
```
Admin Dashboard → Dashboard → Students
```

### With CSV Import
Place CSV file in project root:
```bash
python manage.py create_student --from-csv=my_students.csv
```

### With Web Upload
Admin can upload student data through web interface.

## Best Practices

1. **Always use HT Number as unique identifier**
   - Format: `23C11A1215` (batch + roll number)
   - Ensure it's unique before creating

2. **Verify CSV format before bulk import**
   - Check headers match expected columns
   - Validate data types (year/sem are integers)
   - Remove duplicates

3. **Monitor certificate uploads**
   - Verify photos are under 5MB
   - Ensure certificates are PDFs
   - Check Cloudinary quota regularly

4. **Regular backups**
   - Back up database before bulk operations
   - Export student data monthly
   - Keep audit logs for compliance

## Support

For issues or questions:
1. Check Django logs: `django_log.txt`
2. Run verification: `python manage.py create_student --verify`
3. Check signals are loaded: Verify `apps.py` imports signals
4. Review model fields in `dashboard/models.py`

## Files Reference

- **Models:** `dashboard/models.py` (Student model)
- **Signals:** `dashboard/signals.py` (Auto-initialization)
- **Management Command:** `dashboard/management/commands/create_student.py`
- **Creation Script:** `create_student_profiles.py` (Bulk creation)
- **CSV Template:** `students_template.csv` (Example format)
