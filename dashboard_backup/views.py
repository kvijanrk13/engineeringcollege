# faculty/dashboard/views.py
import os
import json
import tempfile
import logging
from datetime import datetime, date, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Any
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, FileResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.urls import reverse
import pdfkit
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import cloudinary
import cloudinary.uploader
import cloudinary.api
from .models import Faculty, Certificate, FacultyLog, CloudinaryUpload
from .forms import FacultyForm, CertificateForm, LoginForm, BulkUploadForm
from .utils import (
    calculate_experience, generate_pdf_from_html,
    merge_pdfs, extract_text_from_pdf, validate_faculty_data,
    calculate_age, format_date, get_academic_year
)

# Configure logging
logger = logging.getLogger(__name__)


# ==================== HOME & AUTHENTICATION ====================

def home(request):
    """Home page view"""
    return render(request, 'home.html', {
        'title': 'Faculty Management System - Home',
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')
    })


def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html', {'title': 'Login'})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Dashboard view"""
    with_phd_count = Faculty.objects.filter(
        phd_degree='Completed'
    ).count()

    context = {
        'total_faculty': Faculty.objects.count(),
        'with_phd': with_phd_count,
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')),
        'recent_uploads': Faculty.objects.order_by('-created_at')[:5],
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def faculty_list(request):
    """List all faculty members"""
    faculties = Faculty.objects.all().order_by('department', 'name')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        faculties = faculties.filter(
            Q(name__icontains=search_query) |
            Q(employee_code__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Filter by department
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        faculties = faculties.filter(department=dept_filter)

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        faculties = faculties.filter(is_active=True)
    elif status_filter == 'inactive':
        faculties = faculties.filter(is_active=False)

    departments = Faculty.objects.values_list('department', flat=True).distinct()

    return render(request, 'faculty/list.html', {
        'title': 'Faculty Directory',
        'faculties': faculties,
        'departments': departments,
        'search_query': search_query,
        'dept_filter': dept_filter,
        'status_filter': status_filter,
        'total_count': faculties.count()
    })


@login_required
def faculty_detail(request, faculty_id):
    """View faculty details"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Get certificates for this faculty
    certificates = faculty.faculty_certificates.all()

    # Calculate experience
    experience = calculate_experience(faculty.joining_date)

    # Get subjects as list
    subjects = faculty.get_subjects_list()

    # Check Cloudinary status
    cloudinary_status = {
        'has_pdf': bool(faculty.cloudinary_pdf_url),
        'has_photo': bool(faculty.cloudinary_photo_url),
    }

    return render(request, 'faculty/detail.html', {
        'title': f'Faculty - {faculty.name}',
        'faculty': faculty,
        'certificates': certificates,
        'experience': experience,
        'subjects': subjects,
        'cloudinary_status': cloudinary_status,
    })


@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def add_faculty(request):
    """Add new faculty"""
    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'Faculty {faculty.name} added successfully!')

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Created',
                details=f'New faculty added: {faculty.employee_code}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return redirect('faculty_detail', faculty_id=faculty.id)
    else:
        form = FacultyForm()

    return render(request, 'faculty/add.html', {
        'title': 'Add New Faculty',
        'form': form
    })


@login_required
@permission_required('dashboard.change_faculty', raise_exception=True)
def edit_faculty(request, faculty_id):
    """Edit faculty details"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES, instance=faculty)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'Faculty {faculty.name} updated successfully!')

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Updated',
                details=f'Faculty details updated: {faculty.employee_code}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return redirect('faculty_detail', faculty_id=faculty.id)
    else:
        form = FacultyForm(instance=faculty)

    return render(request, 'faculty/edit.html', {
        'title': f'Edit Faculty - {faculty.name}',
        'form': form,
        'faculty': faculty
    })


@login_required
@permission_required('dashboard.delete_faculty', raise_exception=True)
def delete_faculty(request, faculty_id):
    """Delete faculty (soft delete by marking inactive)"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        faculty.is_active = False
        faculty.save()

        messages.success(request, f'Faculty {faculty.name} has been deactivated.')

        # Log the action
        FacultyLog.objects.create(
            faculty=faculty,
            action='Deactivated',
            details=f'Faculty deactivated: {faculty.employee_code}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return redirect('faculty_list')

    return render(request, 'faculty/delete.html', {
        'title': 'Delete Faculty',
        'faculty': faculty
    })


@csrf_exempt
def save_faculty_details(request):
    """Save faculty details from PDF parsing"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            employee_code = data.get('employee_code')

            # Check if faculty already exists
            faculty, created = Faculty.objects.get_or_create(
                employee_code=employee_code,
                defaults={
                    'name': data.get('name', ''),
                    'department': data.get('department', ''),
                    'email': data.get('email', ''),
                    'mobile': data.get('mobile', ''),
                    'joining_date': data.get('joining_date'),
                    'dob': data.get('dob'),
                    'state': data.get('state', ''),
                    'caste': data.get('caste', ''),
                    'sub_caste': data.get('sub_caste', ''),
                    # Educational qualifications
                    'ssc_school': data.get('ssc_school', ''),
                    'ssc_year': data.get('ssc_year', ''),
                    'ssc_percent': float(data.get('ssc_percent', 0)),
                    'inter_college': data.get('inter_college', ''),
                    'inter_year': data.get('inter_year', ''),
                    'inter_percent': float(data.get('inter_percent', 0)),
                    'ug_college': data.get('ug_college', ''),
                    'ug_year': data.get('ug_year', ''),
                    'ug_percentage': float(data.get('ug_percentage', 0)),
                    'ug_spec': data.get('ug_spec', ''),
                    'pg_college': data.get('pg_college', ''),
                    'pg_year': data.get('pg_year', ''),
                    'pg_percentage': float(data.get('pg_percentage', 0)),
                    'pg_spec': data.get('pg_spec', ''),
                    'phd_university': data.get('phd_university', ''),
                    'phd_year': data.get('phd_year', ''),
                    'phd_degree': data.get('phd_degree', 'Not Started'),
                    'phd_spec': data.get('phd_spec', ''),
                    # Other details
                    'subjects_dealt': data.get('subjects_dealt', ''),
                    'about_yourself': data.get('about_yourself', ''),
                }
            )

            if not created:
                # Update existing faculty
                for key, value in data.items():
                    if hasattr(faculty, key):
                        setattr(faculty, key, value)
                faculty.save()

            # Log the action
            action = 'Created' if created else 'Updated'
            FacultyLog.objects.create(
                faculty=faculty,
                action=f'Auto-{action}',
                details=f'Faculty {action} from PDF parsing: {faculty.employee_code}',
                performed_by='System',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return JsonResponse({
                'success': True,
                'message': f'Faculty {action} successfully',
                'faculty_id': faculty.id,
                'employee_code': faculty.employee_code,
                'created': created
            })

        except Exception as e:
            logger.error(f"Error saving faculty details: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def process_faculty_pdf(request):
    """Process uploaded faculty PDF"""
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        try:
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                for chunk in pdf_file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            # Extract data from PDF (simplified - you'd use a proper PDF parser)
            extracted_data = extract_text_from_pdf(tmp_path)

            # Parse extracted data (this is simplified)
            faculty_data = parse_faculty_data(extracted_data)

            # Clean up temp file
            os.unlink(tmp_path)

            return JsonResponse({
                'success': True,
                'data': faculty_data,
                'message': 'PDF processed successfully'
            })

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error processing PDF: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'No PDF file provided'})


# ==================== PDF GENERATION & HANDLING ====================

def generate_faculty_pdf(request, faculty_id):
    """Generate PDF for a faculty member with ALL data included"""
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)

        # Prepare all data for the template
        context = {
            'faculty': faculty,
            'subjects': faculty.get_subjects_list(),
            'educational_details': [
                {
                    'degree': 'SSC',
                    'year': faculty.ssc_year,
                    'percent': faculty.ssc_percent,
                    'institution': faculty.ssc_school,
                    'board': 'State Board'
                },
                {
                    'degree': 'Intermediate',
                    'year': faculty.inter_year,
                    'percent': faculty.inter_percent,
                    'institution': faculty.inter_college,
                    'board': 'State Board'
                },
                {
                    'degree': 'B.Tech',
                    'year': faculty.ug_year,
                    'percent': faculty.ug_percentage,
                    'institution': faculty.ug_college,
                    'specialization': faculty.ug_spec,
                    'university': 'JNTUH'
                },
                {
                    'degree': 'M.Tech',
                    'year': faculty.pg_year,
                    'percent': faculty.pg_percentage,
                    'institution': faculty.pg_college,
                    'specialization': faculty.pg_spec,
                    'university': 'JNTUH'
                },
                {
                    'degree': 'Ph.D',
                    'year': faculty.phd_year,
                    'status': faculty.phd_degree,
                    'specialization': faculty.phd_spec,
                    'institution': faculty.phd_university,
                    'university': faculty.phd_university.split(',')[-1].strip() if faculty.phd_university else ''
                },
            ],
            'personal_details': {
                'dob': faculty.dob,
                'gender': faculty.gender,
                'state': faculty.state,
                'caste': faculty.caste,
                'sub_caste': faculty.sub_caste,
                'aadhar': faculty.aadhar,
                'pan': faculty.pan,
                'mobile': faculty.mobile,
                'email': faculty.email,
                'address': faculty.address,
                'father_name': faculty.father_name,
            },
            'professional_details': {
                'employee_code': faculty.employee_code,
                'department': faculty.department,
                'joining_date': faculty.joining_date,
                'experience_anurag': faculty.exp_anurag,
                'experience_other': faculty.exp_other,
                'jntuh_id': faculty.jntuh_id,
                'aicte_id': faculty.aicte_id,
                'orcid_id': faculty.orcid_id,
                'apaar_id': faculty.apaar_id,
            },
            'experience': calculate_experience(faculty.joining_date),
            'current_date': date.today().strftime('%d-%m-%Y'),
            'college_name': 'ANURAG ENGINEERING COLLEGE',
            'college_address': 'Anurag Nagar, Hyderabad, Telangana',
            'logo_url': request.build_absolute_uri('/static/images/college_logo.png'),
        }

        # Render HTML template with all data
        html_string = render_to_string('faculty/pdf_template.html', context)

        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
            'enable-local-file-access': '',  # Allow local file access for images
        }

        # Configure wkhtmltopdf path if needed
        config = pdfkit.configuration()
        if hasattr(settings, 'WKHTMLTOPDF_PATH'):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

        # Generate PDF
        pdf = pdfkit.from_string(html_string, False, options=options, configuration=config)

        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="faculty_{faculty.employee_code}.pdf"'

        # Log the action
        FacultyLog.objects.create(
            faculty=faculty,
            action='PDF Generated',
            details=f'PDF generated for faculty: {faculty.employee_code}',
            performed_by=request.user.username if request.user.is_authenticated else 'Anonymous',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return response

    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('faculty_detail', faculty_id=faculty_id)


def generate_pdf_with_data(request):
    """Generate PDF with custom data"""
    if request.method == 'POST':
        data = request.POST.dict()

        try:
            # Generate PDF from data
            html_string = render_to_string('faculty/custom_pdf_template.html', {'data': data})

            options = {
                'page-size': 'A4',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': "UTF-8",
            }

            pdf = pdfkit.from_string(html_string, False, options=options)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_document.pdf"'
            return response

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'faculty/generate_pdf_form.html')


@login_required
def preview_faculty_pdf(request, faculty_id):
    """Preview faculty PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Check if PDF exists in Cloudinary
    if faculty.cloudinary_pdf_url:
        return JsonResponse({
            'success': True,
            'pdf_url': faculty.cloudinary_pdf_url,
            'message': 'PDF available on Cloudinary'
        })

    # Check if local PDF exists
    if faculty.pdf_document and faculty.pdf_document.url:
        return JsonResponse({
            'success': True,
            'pdf_url': faculty.pdf_document.url,
            'message': 'Local PDF available'
        })

    return JsonResponse({
        'success': False,
        'error': 'No PDF available. Please generate one first.'
    })


def preview_pdf_template(request):
    """Preview PDF template"""
    return render(request, 'faculty/pdf_preview.html')


@login_required
def download_faculty_pdf(request, faculty_id):
    """Download faculty PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Check Cloudinary first
    if faculty.cloudinary_pdf_url:
        return redirect(faculty.cloudinary_pdf_url)

    # Check local file
    if faculty.pdf_document and faculty.pdf_document.url:
        response = HttpResponse(faculty.pdf_document, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="faculty_{faculty.employee_code}.pdf"'
        return response

    # Generate PDF if not exists
    return generate_faculty_pdf(request, faculty_id)


@login_required
def download_merged_pdf(request, faculty_id):
    """Download merged PDF with certificates"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        # Generate faculty PDF
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            messages.error(request, "Failed to generate faculty PDF")
            return redirect('faculty_detail', faculty_id=faculty_id)

        # Merge with certificates
        merged_pdf = merge_certificates_with_pdf_bytes(pdf_bytes, faculty)

        if merged_pdf:
            response = HttpResponse(merged_pdf, content_type='application/pdf')
            response[
                'Content-Disposition'] = f'attachment; filename="faculty_{faculty.employee_code}_with_certificates.pdf"'

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Merged PDF Downloaded',
                details=f'Merged PDF with certificates downloaded: {faculty.employee_code}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return response
        else:
            messages.error(request, "Failed to merge certificates")
            return redirect('faculty_detail', faculty_id=faculty_id)

    except Exception as e:
        logger.error(f"Error downloading merged PDF: {str(e)}")
        messages.error(request, f"Error: {str(e)}")
        return redirect('faculty_detail', faculty_id=faculty_id)


# ==================== CLOUDINARY INTEGRATION ====================

@login_required
@csrf_exempt
def upload_faculty_to_cloudinary(request, faculty_id):
    """Upload faculty PDF to Cloudinary"""
    if request.method == 'POST':
        try:
            faculty = get_object_or_404(Faculty, id=faculty_id)

            # First generate the PDF
            pdf_bytes = generate_faculty_pdf_bytes(faculty)

            if not pdf_bytes:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate PDF'
                })

            # Save PDF to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file_path = tmp_file.name

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                tmp_file_path,
                resource_type="raw",
                folder="faculty_pdfs",
                public_id=f"faculty_{faculty.employee_code}",
                overwrite=True,
                tags=[f"faculty_{faculty.employee_code}", faculty.department, "pdf"]
            )

            # Save Cloudinary URL to faculty record
            faculty.cloudinary_pdf_url = cloudinary_response['secure_url']
            faculty.save()

            # Record the upload
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='pdf',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                format=cloudinary_response.get('format', 'pdf'),
                bytes=cloudinary_response['bytes'],
                raw_response=cloudinary_response,
                uploaded_by=request.user.username
            )

            # Clean up temp file
            os.unlink(tmp_file_path)

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='PDF Uploaded to Cloudinary',
                details=f'PDF uploaded to Cloudinary: {faculty.employee_code}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return JsonResponse({
                'success': True,
                'pdf_url': faculty.cloudinary_pdf_url,
                'public_id': cloudinary_response['public_id'],
                'message': 'PDF uploaded to Cloudinary successfully'
            })

        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def upload_faculty_photo(request):
    """Upload faculty photo to Cloudinary"""
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            employee_code = request.POST.get('employee_code')
            faculty = get_object_or_404(Faculty, employee_code=employee_code)
            photo_file = request.FILES['photo']

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                photo_file,
                folder="faculty_photos",
                public_id=f"faculty_{employee_code}",
                overwrite=True,
                transformation=[
                    {'width': 300, 'height': 300, 'crop': 'fill'},
                    {'quality': 'auto:good'}
                ]
            )

            # Save Cloudinary URL
            faculty.cloudinary_photo_url = cloudinary_response['secure_url']
            faculty.save()

            # Record the upload
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='photo',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                format=cloudinary_response.get('format', 'jpg'),
                bytes=cloudinary_response['bytes'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )

            return JsonResponse({
                'success': True,
                'photo_url': faculty.cloudinary_photo_url,
                'message': 'Photo uploaded successfully'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No photo file provided'})


@csrf_exempt
def upload_faculty_pdf(request):
    """Upload existing PDF to Cloudinary"""
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        try:
            employee_code = request.POST.get('employee_code')
            faculty = get_object_or_404(Faculty, employee_code=employee_code)
            pdf_file = request.FILES['pdf_file']

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                pdf_file,
                resource_type="raw",
                folder="faculty_pdfs",
                public_id=f"faculty_{employee_code}",
                overwrite=True
            )

            # Save Cloudinary URL
            faculty.cloudinary_pdf_url = cloudinary_response['secure_url']
            faculty.save()

            # Record the upload
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='pdf',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                format='pdf',
                bytes=cloudinary_response['bytes'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )

            return JsonResponse({
                'success': True,
                'pdf_url': faculty.cloudinary_pdf_url,
                'message': 'PDF uploaded to Cloudinary successfully'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No PDF file provided'})


@login_required
def cloudinary_status(request):
    """Check Cloudinary connection status"""
    try:
        # Test Cloudinary connection
        result = cloudinary.api.ping()
        status = result.get('status') == 'ok'

        # Get Cloudinary usage
        usage = cloudinary.api.usage()

        # Count uploaded files
        uploaded_count = CloudinaryUpload.objects.count()
        faculty_with_pdf = Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
            cloudinary_pdf_url='').count()
        faculty_with_photo = Faculty.objects.exclude(cloudinary_photo_url__isnull=True).exclude(
            cloudinary_photo_url='').count()

        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status',
            'connected': status,
            'usage': usage,
            'uploaded_count': uploaded_count,
            'faculty_with_pdf': faculty_with_pdf,
            'faculty_with_photo': faculty_with_photo,
            'total_faculty': Faculty.objects.count(),
            'recent_uploads': CloudinaryUpload.objects.order_by('-upload_date')[:10]
        })

    except Exception as e:
        messages.error(request, f"Cloudinary connection error: {str(e)}")
        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status',
            'connected': False,
            'error': str(e)
        })


@login_required
def sync_to_cloudinary(request, faculty_id):
    """Sync faculty data to Cloudinary"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Sync PDF
    if not faculty.cloudinary_pdf_url:
        return upload_faculty_to_cloudinary(request, faculty_id)

    # Sync photo if exists
    if faculty.photo and not faculty.cloudinary_photo_url:
        try:
            with faculty.photo.open('rb') as photo_file:
                cloudinary_response = cloudinary.uploader.upload(
                    photo_file,
                    folder="faculty_photos",
                    public_id=f"faculty_{faculty.employee_code}",
                    overwrite=True
                )
                faculty.cloudinary_photo_url = cloudinary_response['secure_url']
                faculty.save()

                CloudinaryUpload.objects.create(
                    faculty=faculty,
                    upload_type='photo',
                    cloudinary_url=cloudinary_response['secure_url'],
                    public_id=cloudinary_response['public_id'],
                    resource_type=cloudinary_response['resource_type'],
                    format=cloudinary_response.get('format', 'jpg'),
                    bytes=cloudinary_response['bytes'],
                    uploaded_by=request.user.username
                )
        except Exception as e:
            logger.error(f"Error syncing photo: {str(e)}")

    messages.success(request, f"Faculty {faculty.employee_code} synced to Cloudinary")
    return redirect('faculty_detail', faculty_id=faculty_id)


@login_required
def get_cloudinary_url(request, faculty_id):
    """Get Cloudinary URL for faculty"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    urls = {
        'pdf_url': faculty.cloudinary_pdf_url,
        'photo_url': faculty.cloudinary_photo_url,
        'employee_code': faculty.employee_code,
        'has_pdf': bool(faculty.cloudinary_pdf_url),
        'has_photo': bool(faculty.cloudinary_photo_url),
    }

    return JsonResponse(urls)


# ==================== CERTIFICATE MANAGEMENT ====================

@login_required
def upload_certificate(request, faculty_id):
    """Upload certificate for faculty"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.faculty = faculty

            # Upload certificate file to Cloudinary
            if 'certificate_file' in request.FILES:
                cert_file = request.FILES['certificate_file']

                try:
                    cloudinary_response = cloudinary.uploader.upload(
                        cert_file,
                        resource_type="raw",
                        folder=f"certificates/{faculty.employee_code}",
                        public_id=f"cert_{certificate.certificate_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=False
                    )

                    certificate.cloudinary_url = cloudinary_response['secure_url']

                    # Record the upload
                    CloudinaryUpload.objects.create(
                        faculty=faculty,
                        upload_type='certificate',
                        cloudinary_url=cloudinary_response['secure_url'],
                        public_id=cloudinary_response['public_id'],
                        resource_type=cloudinary_response['resource_type'],
                        format='pdf',
                        bytes=cloudinary_response['bytes'],
                        uploaded_by=request.user.username
                    )

                except Exception as e:
                    logger.error(f"Error uploading certificate to Cloudinary: {str(e)}")
                    # Still save locally even if Cloudinary upload fails

            certificate.save()

            messages.success(request, 'Certificate uploaded successfully!')

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Certificate Uploaded',
                details=f'Certificate uploaded: {certificate.certificate_type}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return redirect('view_certificates', faculty_id=faculty_id)
    else:
        form = CertificateForm()

    return render(request, 'certificates/upload.html', {
        'title': f'Upload Certificate - {faculty.name}',
        'form': form,
        'faculty': faculty
    })


@login_required
def upload_certificates_bulk(request):
    """Bulk upload certificates"""
    if request.method == 'POST' and request.FILES.getlist('certificate_files'):
        employee_code = request.POST.get('employee_code')
        faculty = get_object_or_404(Faculty, employee_code=employee_code)

        files = request.FILES.getlist('certificate_files')
        uploaded_count = 0

        for cert_file in files:
            try:
                # Extract certificate type from filename
                cert_type = os.path.splitext(cert_file.name)[0].replace('_', ' ').title()

                # Upload to Cloudinary
                cloudinary_response = cloudinary.uploader.upload(
                    cert_file,
                    resource_type="raw",
                    folder=f"certificates/{employee_code}",
                    public_id=f"cert_{cert_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=False
                )

                # Create certificate record
                Certificate.objects.create(
                    faculty=faculty,
                    certificate_type=cert_type,
                    certificate_file=cert_file,
                    cloudinary_url=cloudinary_response['secure_url'],
                    issued_by='Unknown',
                    issue_date=date.today(),
                    description=f'Uploaded in bulk on {date.today().strftime("%Y-%m-%d")}'
                )

                uploaded_count += 1

            except Exception as e:
                logger.error(f"Error uploading certificate {cert_file.name}: {str(e)}")

        messages.success(request, f'{uploaded_count} certificates uploaded successfully!')
        return redirect('view_certificates', faculty_id=faculty.id)

    return render(request, 'certificates/bulk_upload.html', {
        'title': 'Bulk Upload Certificates'
    })


@login_required
def view_certificates(request, faculty_id):
    """View all certificates for a faculty"""
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certificates = Certificate.objects.filter(faculty=faculty).order_by('-issue_date')

    return render(request, 'certificates/list.html', {
        'title': f'Certificates - {faculty.name}',
        'faculty': faculty,
        'certificates': certificates
    })


@login_required
def delete_certificate(request, certificate_id):
    """Delete a certificate"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    faculty_id = certificate.faculty.id

    if request.method == 'POST':
        # Delete from Cloudinary if URL exists
        if certificate.cloudinary_url:
            try:
                public_id = certificate.cloudinary_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id, resource_type="raw")
            except Exception as e:
                logger.error(f"Error deleting from Cloudinary: {str(e)}")

        certificate.delete()
        messages.success(request, 'Certificate deleted successfully!')

        # Log the action
        FacultyLog.objects.create(
            faculty=certificate.faculty,
            action='Certificate Deleted',
            details=f'Certificate deleted: {certificate.certificate_type}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return redirect('view_certificates', faculty_id=faculty_id)

    return render(request, 'certificates/delete.html', {
        'title': 'Delete Certificate',
        'certificate': certificate
    })


@login_required
def edit_certificate(request, certificate_id):
    """Edit certificate details"""
    certificate = get_object_or_404(Certificate, id=certificate_id)

    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificate updated successfully!')
            return redirect('view_certificates', faculty_id=certificate.faculty.id)
    else:
        form = CertificateForm(instance=certificate)

    return render(request, 'certificates/edit.html', {
        'title': 'Edit Certificate',
        'form': form,
        'certificate': certificate
    })


@login_required
def merge_certificates(request, faculty_id):
    """Merge certificates into a single PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certificates = Certificate.objects.filter(faculty=faculty)

    if not certificates.exists():
        messages.error(request, 'No certificates found to merge.')
        return redirect('view_certificates', faculty_id=faculty_id)

    try:
        merger = PdfMerger()

        # Add faculty PDF if exists
        if faculty.cloudinary_pdf_url:
            # Download from Cloudinary
            import requests
            response = requests.get(faculty.cloudinary_pdf_url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name
                merger.append(tmp_file_path)
                os.unlink(tmp_file_path)

        # Add certificates
        for certificate in certificates:
            if certificate.certificate_file:
                # Local file
                merger.append(certificate.certificate_file.path)
            elif certificate.cloudinary_url:
                # Cloudinary URL
                import requests
                response = requests.get(certificate.cloudinary_url)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(response.content)
                        tmp_file_path = tmp_file.name
                    merger.append(tmp_file_path)
                    os.unlink(tmp_file_path)

        # Create merged PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as merged_file:
            merger.write(merged_file.name)

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                merged_file.name,
                resource_type="raw",
                folder="merged_certificates",
                public_id=f"merged_{faculty.employee_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overwrite=False
            )

            # Save merged PDF URL
            merged_url = cloudinary_response['secure_url']

            # Clean up
            merger.close()
            os.unlink(merged_file.name)

        # Log the action
        FacultyLog.objects.create(
            faculty=faculty,
            action='Certificates Merged',
            details=f'Certificates merged: {certificates.count()} certificates',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return JsonResponse({
            'success': True,
            'merged_url': merged_url,
            'message': f'{certificates.count()} certificates merged successfully'
        })

    except Exception as e:
        logger.error(f"Error merging certificates: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def merge_certificates_with_pdf(request, faculty_id):
    """Merge certificates with faculty PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        # Generate faculty PDF
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate faculty PDF'
            })

        # Get certificates
        certificates = Certificate.objects.filter(faculty=faculty)

        # Merge
        merged_pdf = merge_certificates_with_pdf_bytes(pdf_bytes, faculty)

        if merged_pdf:
            # Save merged PDF temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(merged_pdf)
                tmp_file_path = tmp_file.name

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                tmp_file_path,
                resource_type="raw",
                folder="merged_documents",
                public_id=f"faculty_certs_{faculty.employee_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overwrite=False
            )

            # Clean up
            os.unlink(tmp_file_path)

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Certificates Merged with PDF',
                details=f'Certificates merged with faculty PDF: {certificates.count()} certificates',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return JsonResponse({
                'success': True,
                'merged_url': cloudinary_response['secure_url'],
                'message': f'PDF merged with {certificates.count()} certificates'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to merge certificates'
            })

    except Exception as e:
        logger.error(f"Error merging certificates with PDF: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def preview_merged_pdf(request, faculty_id):
    """Preview merged PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Check for existing merged PDF
    recent_upload = CloudinaryUpload.objects.filter(
        faculty=faculty,
        upload_type__in=['merged', 'pdf'],
        public_id__contains='merged'
    ).order_by('-upload_date').first()

    if recent_upload:
        return JsonResponse({
            'success': True,
            'pdf_url': recent_upload.cloudinary_url,
            'message': 'Merged PDF available'
        })

    return JsonResponse({
        'success': False,
        'error': 'No merged PDF found. Please merge certificates first.'
    })


# ==================== EXAM BRANCH ====================

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Exam Branch').exists() or u.is_superuser)
def exam_branch(request):
    """Exam branch dashboard"""
    faculties = Faculty.objects.filter(is_active=True).order_by('department', 'name')

    # Statistics
    stats = {
        'total': faculties.count(),
        'with_pdf': faculties.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='').count(),
        'without_pdf': faculties.filter(Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url='')).count(),
        'by_department': faculties.values('department').annotate(
            count=Count('id'),
            with_pdf=Count('id', filter=~Q(cloudinary_pdf_url__isnull=True) & ~Q(cloudinary_pdf_url=''))
        ).order_by('department')
    }

    return render(request, 'exambranch/dashboard.html', {
        'title': 'Exam Branch - Faculty Management',
        'faculties': faculties,
        'stats': stats,
        'total_faculty': faculties.count()
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Exam Branch').exists() or u.is_superuser)
def exam_branch_faculty_list(request):
    """Exam branch faculty list with download options"""
    faculties = Faculty.objects.filter(is_active=True).order_by('department', 'name')

    # Add PDF status to each faculty
    for faculty in faculties:
        faculty.has_cloudinary_pdf = bool(faculty.cloudinary_pdf_url)
        faculty.pdf_status = 'Available' if faculty.cloudinary_pdf_url else 'Not Available'

    return render(request, 'exambranch/faculty_list.html', {
        'title': 'Exam Branch - Faculty List',
        'faculties': faculties,
        'total_count': faculties.count(),
        'available_pdfs': sum(1 for f in faculties if f.has_cloudinary_pdf)
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Exam Branch').exists() or u.is_superuser)
def download_all_pdfs(request):
    """Download all faculty PDFs as zip"""
    faculties = Faculty.objects.filter(is_active=True).exclude(
        Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url='')
    )

    if not faculties.exists():
        messages.error(request, 'No PDFs available for download.')
        return redirect('exam_branch')

    try:
        import zipfile
        import requests
        from io import BytesIO

        # Create zip file in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for faculty in faculties:
                try:
                    # Download PDF from Cloudinary
                    response = requests.get(faculty.cloudinary_pdf_url)
                    if response.status_code == 200:
                        # Add to zip
                        filename = f"faculty_{faculty.employee_code}_{faculty.name.replace(' ', '_')}.pdf"
                        zf.writestr(filename, response.content)
                except Exception as e:
                    logger.error(f"Error downloading PDF for {faculty.employee_code}: {str(e)}")
                    continue

        memory_file.seek(0)

        # Create response
        response = HttpResponse(memory_file.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="faculty_pdfs.zip"'

        # Log the action
        FacultyLog.objects.create(
            faculty=None,
            action='All PDFs Downloaded',
            details=f'All faculty PDFs downloaded by {request.user.username}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return response

    except Exception as e:
        logger.error(f"Error creating zip file: {str(e)}")
        messages.error(request, f"Error creating download: {str(e)}")
        return redirect('exam_branch')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Exam Branch').exists() or u.is_superuser)
def generate_exam_branch_report(request):
    """Generate exam branch report"""
    faculties = Faculty.objects.filter(is_active=True).order_by('department', 'name')

    # Prepare report data
    report_data = []
    for faculty in faculties:
        report_data.append({
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'pdf_available': bool(faculty.cloudinary_pdf_url),
            'pdf_url': faculty.cloudinary_pdf_url,
            'subjects': faculty.subjects_dealt,
            'qualification': f"{faculty.ug_spec} (UG), {faculty.pg_spec} (PG)" if faculty.pg_spec else faculty.ug_spec,
        })

    # Generate report (could be PDF, Excel, etc.)
    if request.GET.get('format') == 'pdf':
        # Generate PDF report
        html_string = render_to_string('exambranch/report_pdf.html', {
            'faculties': report_data,
            'total_count': len(report_data),
            'available_pdfs': sum(1 for f in report_data if f['pdf_available']),
            'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'generated_by': request.user.username
        })

        pdf = pdfkit.from_string(html_string, False)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exam_branch_report.pdf"'
        return response

    elif request.GET.get('format') == 'excel':
        # Generate Excel report
        import pandas as pd
        from io import BytesIO

        df = pd.DataFrame(report_data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Faculty Report', index=False)

        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="exam_branch_report.xlsx"'
        return response

    else:
        # HTML view
        return render(request, 'exambranch/report.html', {
            'title': 'Exam Branch Report',
            'report_data': report_data,
            'total_count': len(report_data),
            'available_pdfs': sum(1 for f in report_data if f['pdf_available'])
        })


# ==================== REPORTS & ANALYTICS ====================

@login_required
def reports_dashboard(request):
    """Reports dashboard"""
    return render(request, 'reports/dashboard.html', {
        'title': 'Reports & Analytics'
    })


@login_required
def faculty_summary_report(request):
    """Faculty summary report"""
    faculties = Faculty.objects.all()

    # Statistics
    stats = {
        'total': faculties.count(),
        'active': faculties.filter(is_active=True).count(),
        'male': faculties.filter(gender='Male').count(),
        'female': faculties.filter(gender='Female').count(),
        'with_phd': faculties.filter(phd_degree='Completed').count(),
        'avg_experience': None,  # Calculate average experience
        'by_department': faculties.values('department').annotate(count=Count('id')).order_by('-count'),
        'by_qualification': faculties.values('ug_spec').annotate(count=Count('id')).order_by('-count'),
    }

    return render(request, 'reports/faculty_summary.html', {
        'title': 'Faculty Summary Report',
        'stats': stats,
        'faculties': faculties
    })


@login_required
def department_wise_report(request):
    """Department-wise report"""
    departments = Faculty.objects.values('department').annotate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True)),
        male=Count('id', filter=Q(gender='Male')),
        female=Count('id', filter=Q(gender='Female')),
        with_phd=Count('id', filter=Q(phd_degree='Completed')),
        avg_ug_percentage=Avg('ug_percentage'),
        avg_pg_percentage=Avg('pg_percentage')
    ).order_by('department')

    return render(request, 'reports/department_wise.html', {
        'title': 'Department-wise Report',
        'departments': departments,
        'total_faculty': Faculty.objects.count()
    })


@login_required
def qualification_wise_report(request):
    """Qualification-wise report"""
    qualifications = []

    # UG qualifications
    ug_stats = Faculty.objects.values('ug_spec').annotate(
        count=Count('id'),
        avg_percentage=Avg('ug_percentage')
    ).order_by('-count')

    # PG qualifications
    pg_stats = Faculty.objects.values('pg_spec').annotate(
        count=Count('id'),
        avg_percentage=Avg('pg_percentage')
    ).order_by('-count')

    # PhD status
    phd_stats = Faculty.objects.values('phd_degree').annotate(
        count=Count('id')
    ).order_by('-count')

    return render(request, 'reports/qualification_wise.html', {
        'title': 'Qualification-wise Report',
        'ug_stats': ug_stats,
        'pg_stats': pg_stats,
        'phd_stats': phd_stats
    })


@login_required
def experience_wise_report(request):
    """Experience-wise report"""
    # Group by experience ranges
    experience_ranges = [
        {'range': '0-5 years', 'min': 0, 'max': 5},
        {'range': '6-10 years', 'min': 6, 'max': 10},
        {'range': '11-15 years', 'min': 11, 'max': 15},
        {'range': '16-20 years', 'min': 16, 'max': 20},
        {'range': '21+ years', 'min': 21, 'max': 100}
    ]

    experience_data = []
    for exp_range in experience_ranges:
        # Calculate based on joining date
        from datetime import timedelta
        max_date = date.today() - timedelta(days=exp_range['min'] * 365)
        min_date = date.today() - timedelta(days=exp_range['max'] * 365) if exp_range['max'] < 100 else None

        if min_date:
            count = Faculty.objects.filter(
                joining_date__lte=max_date,
                joining_date__gt=min_date
            ).count()
        else:
            count = Faculty.objects.filter(
                joining_date__lte=max_date
            ).count()

        experience_data.append({
            'range': exp_range['range'],
            'count': count
        })

    return render(request, 'reports/experience_wise.html', {
        'title': 'Experience-wise Report',
        'experience_data': experience_data,
        'total_faculty': Faculty.objects.count()
    })


# ==================== API ENDPOINTS ====================

@csrf_exempt
def api_faculty_list(request):
    """API: Get faculty list"""
    faculties = Faculty.objects.filter(is_active=True)

    # Filters
    department = request.GET.get('department')
    if department:
        faculties = faculties.filter(department=department)

    search = request.GET.get('search')
    if search:
        faculties = faculties.filter(
            Q(name__icontains=search) |
            Q(employee_code__icontains=search) |
            Q(email__icontains=search)
        )

    # Format response
    data = []
    for faculty in faculties:
        data.append({
            'id': faculty.id,
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'photo_url': faculty.cloudinary_photo_url or (faculty.photo.url if faculty.photo else None),
            'pdf_url': faculty.cloudinary_pdf_url,
            'subjects': faculty.get_subjects_list(),
        })

    return JsonResponse({'success': True, 'data': data, 'count': len(data)})


@csrf_exempt
def api_faculty_detail(request, faculty_id):
    """API: Get faculty details"""
    try:
        faculty = Faculty.objects.get(id=faculty_id)

        data = {
            'id': faculty.id,
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'joining_date': faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else None,
            'dob': faculty.dob.strftime('%Y-%m-%d') if faculty.dob else None,
            'gender': faculty.gender,
            'address': faculty.address,
            'photo_url': faculty.cloudinary_photo_url or (faculty.photo.url if faculty.photo else None),
            'pdf_url': faculty.cloudinary_pdf_url,
            'subjects': faculty.get_subjects_list(),
            'educational_qualifications': {
                'ssc': {
                    'year': faculty.ssc_year,
                    'percentage': float(faculty.ssc_percent),
                    'school': faculty.ssc_school
                },
                'inter': {
                    'year': faculty.inter_year,
                    'percentage': float(faculty.inter_percent),
                    'college': faculty.inter_college
                },
                'ug': {
                    'year': faculty.ug_year,
                    'percentage': float(faculty.ug_percentage),
                    'college': faculty.ug_college,
                    'specialization': faculty.ug_spec
                },
                'pg': {
                    'year': faculty.pg_year,
                    'percentage': float(faculty.pg_percentage),
                    'college': faculty.pg_college,
                    'specialization': faculty.pg_spec
                },
                'phd': {
                    'status': faculty.phd_degree,
                    'year': faculty.phd_year,
                    'university': faculty.phd_university,
                    'specialization': faculty.phd_spec
                }
            }
        }

        return JsonResponse({'success': True, 'data': data})

    except Faculty.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Faculty not found'}, status=404)


@csrf_exempt
def api_faculty_by_code(request, employee_code):
    """API: Get faculty by employee code"""
    try:
        faculty = Faculty.objects.get(employee_code=employee_code.upper())
        return api_faculty_detail(request, faculty.id)
    except Faculty.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Faculty not found'}, status=404)


@csrf_exempt
def api_generate_pdf(request):
    """API: Generate PDF"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            faculty_id = data.get('faculty_id')

            if not faculty_id:
                return JsonResponse({'success': False, 'error': 'faculty_id is required'})

            # Generate PDF
            faculty = Faculty.objects.get(id=faculty_id)
            pdf_response = generate_faculty_pdf(request, faculty_id)

            if isinstance(pdf_response, HttpResponse):
                # Convert to base64 or return URL if uploaded to Cloudinary
                if faculty.cloudinary_pdf_url:
                    return JsonResponse({
                        'success': True,
                        'pdf_url': faculty.cloudinary_pdf_url,
                        'message': 'PDF already exists in Cloudinary'
                    })
                else:
                    # Return PDF as base64
                    import base64
                    pdf_base64 = base64.b64encode(pdf_response.content).decode('utf-8')
                    return JsonResponse({
                        'success': True,
                        'pdf_base64': pdf_base64,
                        'message': 'PDF generated successfully'
                    })
            else:
                return JsonResponse({'success': False, 'error': 'Failed to generate PDF'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def api_upload_pdf_to_cloudinary(request):
    """API: Upload PDF to Cloudinary"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            faculty_id = data.get('faculty_id')

            if not faculty_id:
                return JsonResponse({'success': False, 'error': 'faculty_id is required'})

            # Upload to Cloudinary
            faculty = Faculty.objects.get(id=faculty_id)
            response = upload_faculty_to_cloudinary(request, faculty_id)

            if isinstance(response, JsonResponse):
                response_data = json.loads(response.content)
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'error': 'Upload failed'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def api_status(request):
    """API: System status"""
    status = {
        'system': 'online',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if Faculty.objects.exists() else 'empty',
        'cloudinary': 'configured' if hasattr(settings, 'CLOUDINARY_URL') else 'not_configured',
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'pdfs_in_cloudinary': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
            cloudinary_pdf_url='').count(),
    }

    return JsonResponse({'success': True, 'status': status})


@csrf_exempt
def api_stats(request):
    """API: Statistics"""
    stats = {
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')).count(),
        'with_phd': Faculty.objects.filter(phd_degree='Completed').count(),
        'with_cloudinary_pdf': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
            cloudinary_pdf_url='').count(),
        'with_cloudinary_photo': Faculty.objects.exclude(cloudinary_photo_url__isnull=True).exclude(
            cloudinary_photo_url='').count(),
        'gender_distribution': {
            'male': Faculty.objects.filter(gender='Male').count(),
            'female': Faculty.objects.filter(gender='Female').count(),
            'other': Faculty.objects.filter(gender='Other').count(),
        },
        'recent_uploads': CloudinaryUpload.objects.count(),
    }

    return JsonResponse({'success': True, 'stats': stats})


# ==================== UTILITY ROUTES ====================

@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def import_faculty_data(request):
    """Import faculty data from CSV/Excel"""
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_type = form.cleaned_data['file_type']

            try:
                import pandas as pd

                if file_type == 'csv':
                    df = pd.read_csv(file)
                else:  # excel
                    df = pd.read_excel(file)

                imported_count = 0
                errors = []

                for index, row in df.iterrows():
                    try:
                        # Create or update faculty
                        faculty, created = Faculty.objects.get_or_create(
                            employee_code=str(row.get('employee_code', '')).strip().upper(),
                            defaults={
                                'name': str(row.get('name', '')).strip(),
                                'department': str(row.get('department', '')).strip(),
                                'email': str(row.get('email', '')).strip().lower(),
                                'mobile': str(row.get('mobile', '')).strip(),
                                'joining_date': pd.to_datetime(row.get('joining_date', None)).date() if pd.notna(
                                    row.get('joining_date', None)) else None,
                                'is_active': True,
                            }
                        )

                        if created:
                            imported_count += 1

                    except Exception as e:
                        errors.append(f"Row {index + 1}: {str(e)}")

                messages.success(request, f'Successfully imported {imported_count} faculty records.')
                if errors:
                    messages.warning(request, f'{len(errors)} records had errors.')

                return redirect('faculty_list')

            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = BulkUploadForm()

    return render(request, 'utils/import.html', {
        'title': 'Import Faculty Data',
        'form': form
    })


@login_required
def export_faculty_data(request):
    """Export faculty data"""
    format = request.GET.get('format', 'csv')
    faculties = Faculty.objects.all()

    if format == 'csv':
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Employee Code', 'Name', 'Department', 'Email', 'Mobile',
            'Joining Date', 'Date of Birth', 'Gender', 'Address',
            'SSC Percentage', 'Inter Percentage', 'UG Percentage', 'PG Percentage',
            'Subjects Dealt', 'Status'
        ])

        # Write data
        for faculty in faculties:
            writer.writerow([
                faculty.employee_code,
                faculty.name,
                faculty.department,
                faculty.email,
                faculty.mobile,
                faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else '',
                faculty.dob.strftime('%Y-%m-%d') if faculty.dob else '',
                faculty.gender,
                faculty.address or '',
                float(faculty.ssc_percent),
                float(faculty.inter_percent),
                float(faculty.ug_percentage),
                float(faculty.pg_percentage),
                faculty.subjects_dealt or '',
                'Active' if faculty.is_active else 'Inactive'
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="faculty_data.csv"'
        return response

    else:
        # Default to HTML view
        return render(request, 'utils/export.html', {
            'title': 'Export Faculty Data',
            'faculties': faculties,
            'total_count': faculties.count()
        })


@login_required
def export_to_excel(request):
    """Export faculty data to Excel"""
    try:
        import pandas as pd
        from io import BytesIO

        # Prepare data
        data = []
        for faculty in Faculty.objects.all():
            data.append({
                'Employee Code': faculty.employee_code,
                'Name': faculty.name,
                'Department': faculty.department,
                'Email': faculty.email,
                'Mobile': faculty.mobile,
                'Joining Date': faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else '',
                'Date of Birth': faculty.dob.strftime('%Y-%m-%d') if faculty.dob else '',
                'Gender': faculty.gender,
                'Address': faculty.address or '',
                'SSC %': float(faculty.ssc_percent),
                'Inter %': float(faculty.inter_percent),
                'UG %': float(faculty.ug_percentage),
                'PG %': float(faculty.pg_percentage),
                'PhD Status': faculty.phd_degree,
                'Subjects': faculty.subjects_dealt or '',
                'Status': 'Active' if faculty.is_active else 'Inactive',
                'Cloudinary PDF': 'Yes' if faculty.cloudinary_pdf_url else 'No',
                'Cloudinary Photo': 'Yes' if faculty.cloudinary_photo_url else 'No'
            })

        df = pd.DataFrame(data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Faculty Data', index=False)

        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="faculty_data.xlsx"'
        return response

    except Exception as e:
        messages.error(request, f'Error exporting to Excel: {str(e)}')
        return redirect('export_faculty_data')


@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def backup_data(request):
    """Backup database data"""
    try:
        import json
        from django.core import serializers

        # Backup faculty data
        faculty_data = serializers.serialize('json', Faculty.objects.all())
        certificate_data = serializers.serialize('json', Certificate.objects.all())

        backup = {
            'timestamp': datetime.now().isoformat(),
            'faculty': json.loads(faculty_data),
            'certificates': json.loads(certificate_data),
        }

        # Create backup file
        backup_json = json.dumps(backup, indent=2)
        response = HttpResponse(backup_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="faculty_backup.json"'
        return response

    except Exception as e:
        messages.error(request, f'Error creating backup: {str(e)}')
        return redirect('dashboard')


@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def restore_data(request):
    """Restore data from backup"""
    if request.method == 'POST' and request.FILES.get('backup_file'):
        backup_file = request.FILES['backup_file']

        try:
            import json
            from django.core.serializers import deserialize

            backup_data = json.loads(backup_file.read().decode('utf-8'))

            # Restore faculty data
            faculty_count = 0
            for obj in backup_data.get('faculty', []):
                try:
                    deserialize('json', json.dumps([obj]))
                    faculty_count += 1
                except:
                    pass

            # Restore certificate data
            cert_count = 0
            for obj in backup_data.get('certificates', []):
                try:
                    deserialize('json', json.dumps([obj]))
                    cert_count += 1
                except:
                    pass

            messages.success(request, f'Restored {faculty_count} faculty records and {cert_count} certificates.')
            return redirect('faculty_list')

        except Exception as e:
            messages.error(request, f'Error restoring backup: {str(e)}')

    return render(request, 'utils/restore.html', {'title': 'Restore Data'})


@login_required
def settings_view(request):
    """System settings"""
    return render(request, 'settings/index.html', {
        'title': 'Settings',
        'cloudinary_configured': hasattr(settings, 'CLOUDINARY_URL'),
        'pdfkit_configured': hasattr(settings, 'WKHTMLTOPDF_PATH'),
        'debug_mode': settings.DEBUG,
    })


@login_required
def cloudinary_settings(request):
    """Cloudinary settings"""
    config = {
        'cloud_name': getattr(cloudinary.config(), 'cloud_name', 'Not configured'),
        'api_key': 'Configured' if getattr(cloudinary.config(), 'api_key', None) else 'Not configured',
        'api_secret': 'Configured' if getattr(cloudinary.config(), 'api_secret', None) else 'Not configured',
        'secure': getattr(cloudinary.config(), 'secure', True),
    }

    return render(request, 'settings/cloudinary.html', {
        'title': 'Cloudinary Settings',
        'config': config
    })


@login_required
def pdf_settings(request):
    """PDF generation settings"""
    config = {
        'wkhtmltopdf_path': getattr(settings, 'WKHTMLTOPDF_PATH', 'Not configured'),
        'default_page_size': 'A4',
        'default_margins': '0.75in',
    }

    return render(request, 'settings/pdf.html', {
        'title': 'PDF Settings',
        'config': config
    })


# ==================== AJAX ENDPOINTS ====================

@csrf_exempt
def ajax_get_faculty_data(request):
    """AJAX: Get faculty data for autocomplete"""
    search = request.GET.get('search', '')

    if search:
        faculties = Faculty.objects.filter(
            Q(name__icontains=search) |
            Q(employee_code__icontains=search) |
            Q(email__icontains=search)
        )[:10]
    else:
        faculties = Faculty.objects.none()

    data = []
    for faculty in faculties:
        data.append({
            'id': faculty.id,
            'text': f"{faculty.employee_code} - {faculty.name} ({faculty.department})",
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
        })

    return JsonResponse({'results': data})


@csrf_exempt
def ajax_check_faculty_code(request):
    """AJAX: Check if employee code exists"""
    employee_code = request.GET.get('employee_code', '').upper()

    exists = Faculty.objects.filter(employee_code=employee_code).exists()

    return JsonResponse({
        'exists': exists,
        'employee_code': employee_code
    })


@csrf_exempt
def ajax_search_faculty(request):
    """AJAX: Search faculty"""
    search = request.GET.get('search', '')
    department = request.GET.get('department', '')

    faculties = Faculty.objects.all()

    if search:
        faculties = faculties.filter(
            Q(name__icontains=search) |
            Q(employee_code__icontains=search) |
            Q(email__icontains=search)
        )

    if department:
        faculties = faculties.filter(department=department)

    # Format results
    results = []
    for faculty in faculties[:20]:  # Limit to 20 results
        results.append({
            'id': faculty.id,
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'has_pdf': bool(faculty.cloudinary_pdf_url),
            'pdf_url': faculty.cloudinary_pdf_url,
        })

    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results)
    })


@csrf_exempt
def ajax_generate_pdf(request):
    """AJAX: Generate PDF"""
    if request.method == 'POST':
        try:
            faculty_id = request.POST.get('faculty_id')
            faculty = get_object_or_404(Faculty, id=faculty_id)

            # Generate PDF
            pdf_response = generate_faculty_pdf(request, faculty_id)

            if isinstance(pdf_response, HttpResponse):
                # Return success with download URL
                return JsonResponse({
                    'success': True,
                    'message': 'PDF generated successfully',
                    'download_url': reverse('download_faculty_pdf', args=[faculty_id])
                })
            else:
                return JsonResponse({'success': False, 'error': 'Failed to generate PDF'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def ajax_upload_pdf(request):
    """AJAX: Upload PDF to Cloudinary"""
    if request.method == 'POST':
        try:
            faculty_id = request.POST.get('faculty_id')
            faculty = get_object_or_404(Faculty, id=faculty_id)

            # Upload to Cloudinary
            response = upload_faculty_to_cloudinary(request, faculty_id)

            if isinstance(response, JsonResponse):
                response_data = json.loads(response.content)
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'error': 'Upload failed'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def ajax_check_pdf_status(request, faculty_id):
    """AJAX: Check PDF status"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    status = {
        'has_local_pdf': bool(faculty.pdf_document),
        'has_cloudinary_pdf': bool(faculty.cloudinary_pdf_url),
        'cloudinary_url': faculty.cloudinary_pdf_url,
        'last_upload': None,
    }

    # Get last upload date
    last_upload = CloudinaryUpload.objects.filter(
        faculty=faculty,
        upload_type='pdf'
    ).order_by('-upload_date').first()

    if last_upload:
        status['last_upload'] = last_upload.upload_date.isoformat()

    return JsonResponse({'success': True, 'status': status})


@csrf_exempt
def ajax_upload_certificate(request):
    """AJAX: Upload certificate"""
    if request.method == 'POST' and request.FILES.get('certificate_file'):
        try:
            faculty_id = request.POST.get('faculty_id')
            faculty = get_object_or_404(Faculty, id=faculty_id)

            certificate_type = request.POST.get('certificate_type', 'Certificate')
            cert_file = request.FILES['certificate_file']

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                cert_file,
                resource_type="raw",
                folder=f"certificates/{faculty.employee_code}",
                public_id=f"cert_{certificate_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overwrite=False
            )

            # Create certificate record
            certificate = Certificate.objects.create(
                faculty=faculty,
                certificate_type=certificate_type,
                certificate_file=cert_file,
                cloudinary_url=certificate.cloudinary_url,
                issued_by=request.POST.get('issued_by', 'Unknown'),
                issue_date=request.POST.get('issue_date', date.today()),
                expiry_date=request.POST.get('expiry_date'),
                description=request.POST.get('description', ''),
                is_verified=False
            )

            return JsonResponse({
                'success': True,
                'certificate_id': certificate.id,
                'certificate_type': certificate.certificate_type,
                'cloudinary_url': certificate.cloudinary_url,
                'message': 'Certificate uploaded successfully'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No certificate file provided'})


@csrf_exempt
def ajax_merge_certificates(request):
    """AJAX: Merge certificates"""
    if request.method == 'POST':
        try:
            faculty_id = request.POST.get('faculty_id')
            response = merge_certificates(request, faculty_id)

            if isinstance(response, JsonResponse):
                response_data = json.loads(response.content)
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'error': 'Merge failed'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ==================== TEMPLATE VIEWS ====================

def pdf_template_view(request):
    """PDF template preview"""
    # Sample faculty for template preview
    sample_faculty = {
        'employee_code': '7001',
        'name': 'KAMBHAMPATI VIJAY KUMAR',
        'department': 'INFORMATION TECHNOLOGY',
        'joining_date': '2010-12-10',
        'email': 'hod.inf@anurag.ac.in',
        'mobile': '9553122276',
        'dob': '1984-05-24',
        'gender': 'Male',
        'state': 'Telangana',
        'caste': 'BC-D',
        'sub_caste': 'MUNNURUKAPU',
        'address': 'H.No:6-35/12, MARUTHI NAGAR, WARANGAL CROSS ROAD, YEDULAPURAM, KHAMMAM - 507163',
        'father_name': 'KAMBHAMPATI KANAKA DURGA RAO',
        'ssc_school': 'SES VV CENTRAL PUBLIC SCHOOL, KHAMMAM',
        'ssc_year': '2000',
        'ssc_percent': 56.2,
        'inter_college': 'EXCELLENT JUNIOR COLLEGE, KHAMMAM',
        'inter_year': '2002',
        'inter_percent': 57.1,
        'ug_college': 'SREE KAVITHA ENGINEERING COLLEGE, KAREPALLY, KHAMMAM',
        'ug_year': '2006',
        'ug_percentage': 55.6,
        'ug_spec': 'INFORMATION TECHNOLOGY',
        'pg_college': 'SREE KAVITHA ENGINEERING COLLEGE, KAREPALLY, KHAMMAM',
        'pg_year': '2010',
        'pg_percentage': 72.4,
        'pg_spec': 'SOFTWARE ENGINEERING',
        'phd_university': 'KLU, VIJAYAWADA',
        'phd_year': '',
        'phd_degree': 'Pursuing',
        'phd_spec': 'COMPUTER SCIENCE & ENGINEERING',
        'exp_anurag': '15Y 1M 8D',
        'exp_other': '1 Year',
        'subjects_dealt': 'DATA WAREHOUSING AND DATA MINING, DATA STRUCTURES, PROGRAMMING FOR PROBLEM SOLVING, DISCRETE MATHEMATICS, INFORMATION SECURITY, DESIGN AND ANALYSIS OF ALGORITHMS',
        'about_yourself': 'I WAS PROMOTED AS HOD OF IT ON 08-12-2023',
        'jntuh_id': '1',
        'aicte_id': '1-468376653',
        'pan': 'ARXPK1671R',
        'aadhar': '846452283847',
        'orcid_id': '0000-0002-9791-8445',
        'apaar_id': '7',
    }

    return render(request, 'faculty/pdf_template.html', {
        'faculty': type('Faculty', (), sample_faculty)(),  # Mock object
        'subjects': sample_faculty['subjects_dealt'].split(', '),
        'educational_details': [
            {'degree': 'SSC', 'year': '2000', 'percent': 56.2, 'institution': sample_faculty['ssc_school']},
            {'degree': 'Intermediate', 'year': '2002', 'percent': 57.1, 'institution': sample_faculty['inter_college']},
            {'degree': 'B.Tech', 'year': '2006', 'percent': 55.6, 'institution': sample_faculty['ug_college'],
             'specialization': sample_faculty['ug_spec']},
            {'degree': 'M.Tech', 'year': '2010', 'percent': 72.4, 'institution': sample_faculty['pg_college'],
             'specialization': sample_faculty['pg_spec']},
            {'degree': 'Ph.D', 'year': '', 'status': 'Pursuing', 'institution': sample_faculty['phd_university'],
             'specialization': sample_faculty['phd_spec']},
        ],
        'current_date': date.today().strftime('%d-%m-%Y'),
        'college_name': 'ANURAG ENGINEERING COLLEGE',
        'logo_url': request.build_absolute_uri('/static/images/college_logo.png'),
    })


def pdf_template_preview(request):
    """PDF template preview page"""
    return render(request, 'faculty/pdf_preview.html', {
        'title': 'PDF Template Preview'
    })


# ==================== ERROR PAGES ====================

def error_404(request, exception=None):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', {
        'title': '404 - Page Not Found',
        'exception': str(exception) if exception else ''
    }, status=404)


def error_500(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', {
        'title': '500 - Server Error'
    }, status=500)


def custom_404(request, exception):
    """Custom 404 error handler"""
    return error_404(request, exception)


def custom_500(request):
    """Custom 500 error handler"""
    return error_500(request)


def custom_403(request, exception):
    """Custom 403 error handler"""
    return render(request, 'errors/403.html', {
        'title': '403 - Access Denied',
        'exception': str(exception) if exception else ''
    }, status=403)


def custom_400(request, exception):
    """Custom 400 error handler"""
    return render(request, 'errors/400.html', {
        'title': '400 - Bad Request',
        'exception': str(exception) if exception else ''
    }, status=400)


# ==================== ADMIN SPECIFIC ====================

@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def admin_faculty_bulk_upload(request):
    """Admin: Bulk upload faculty"""
    return import_faculty_data(request)


@login_required
@permission_required('dashboard.delete_faculty', raise_exception=True)
def admin_cleanup_data(request):
    """Admin: Cleanup old data"""
    if request.method == 'POST':
        days = int(request.POST.get('days', 30))
        cutoff_date = datetime.now() - timedelta(days=days)

        # Delete old logs
        deleted_logs = FacultyLog.objects.filter(created_at__lt=cutoff_date).delete()[0]

        # Delete old Cloudinary upload records
        deleted_uploads = CloudinaryUpload.objects.filter(upload_date__lt=cutoff_date).delete()[0]

        messages.success(request,
                         f'Cleaned up {deleted_logs} logs and {deleted_uploads} upload records older than {days} days.')
        return redirect('dashboard')

    return render(request, 'admin/cleanup.html', {'title': 'Data Cleanup'})


@login_required
@permission_required('dashboard.view_facultylog', raise_exception=True)
def admin_system_logs(request):
    """Admin: View system logs"""
    logs = FacultyLog.objects.all().order_by('-created_at')[:100]

    return render(request, 'admin/logs.html', {
        'title': 'System Logs',
        'logs': logs,
        'total_logs': FacultyLog.objects.count()
    })


@login_required
@permission_required('dashboard.view_facultylog', raise_exception=True)
def admin_audit_trail(request):
    """Admin: Audit trail"""
    # Get all changes for a specific faculty or all
    faculty_id = request.GET.get('faculty_id')

    if faculty_id:
        logs = FacultyLog.objects.filter(faculty_id=faculty_id).order_by('-created_at')
    else:
        logs = FacultyLog.objects.all().order_by('-created_at')[:200]

    return render(request, 'admin/audit_trail.html', {
        'title': 'Audit Trail',
        'logs': logs,
        'faculties': Faculty.objects.all()
    })


# ==================== CUSTOM DOWNLOAD ROUTES ====================

def download_faculty_pdf_by_code(request, employee_code):
    """Download faculty PDF by employee code"""
    try:
        faculty = Faculty.objects.get(employee_code=employee_code.upper())
        return download_faculty_pdf(request, faculty.id)
    except Faculty.DoesNotExist:
        messages.error(request, f'Faculty with code {employee_code} not found.')
        return redirect('home')


def download_from_cloudinary(request, public_id):
    """Download file directly from Cloudinary"""
    try:
        # Construct Cloudinary URL
        cloudinary_url = f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/raw/upload/{public_id}"

        # Redirect to Cloudinary URL
        return redirect(cloudinary_url)

    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('home')


# ==================== HEALTH & MONITORING ====================

def health_check(request):
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': 'up' if Faculty.objects.exists() or True else 'down',
            'cloudinary': 'configured' if hasattr(settings, 'CLOUDINARY_URL') else 'not_configured',
            'pdf_generation': 'available' if hasattr(settings, 'WKHTMLTOPDF_PATH') else 'not_configured',
        },
        'statistics': {
            'faculty_count': Faculty.objects.count(),
            'active_faculty': Faculty.objects.filter(is_active=True).count(),
            'pdf_count': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
                cloudinary_pdf_url='').count(),
        }
    }

    return JsonResponse(health_status)


@login_required
def system_status(request):
    """System status page"""
    return render(request, 'system/status.html', {
        'title': 'System Status',
        'faculty_count': Faculty.objects.count(),
        'certificate_count': Certificate.objects.count(),
        'log_count': FacultyLog.objects.count(),
        'cloudinary_upload_count': CloudinaryUpload.objects.count(),
        'disk_usage': get_disk_usage(),
        'memory_usage': get_memory_usage(),
    })


@login_required
@permission_required('dashboard.view_facultylog', raise_exception=True)
def view_logs(request):
    """View system logs"""
    return admin_system_logs(request)


# ==================== WEBHOOKS ====================

@csrf_exempt
def cloudinary_webhook(request):
    """Cloudinary webhook endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event = data.get('event')

            logger.info(f"Cloudinary webhook received: {event}")

            # Handle different events
            if event == 'upload':
                public_id = data.get('public_id')
                secure_url = data.get('secure_url')

                # Update faculty record if this is a faculty PDF
                if public_id.startswith('faculty_'):
                    employee_code = public_id.replace('faculty_', '').split('.')[0]

                    try:
                        faculty = Faculty.objects.get(employee_code=employee_code)
                        faculty.cloudinary_pdf_url = secure_url
                        faculty.save()

                        # Record the webhook
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='pdf_webhook',
                            cloudinary_url=secure_url,
                            public_id=public_id,
                            resource_type=data.get('resource_type', 'raw'),
                            format=data.get('format', 'pdf'),
                            bytes=data.get('bytes', 0),
                            raw_response=data,
                            uploaded_by='webhook'
                        )

                    except Faculty.DoesNotExist:
                        logger.warning(f"Faculty not found for employee_code: {employee_code}")

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Error processing Cloudinary webhook: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def pdf_generation_webhook(request):
    """PDF generation webhook"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            status = data.get('status')

            logger.info(f"PDF generation webhook: task={task_id}, status={status}")

            # Update task status in database if you have a task model

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Error processing PDF generation webhook: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


# ==================== BATCH PROCESSING ====================

@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def batch_generate_all_pdfs(request):
    """Batch generate PDFs for all faculty"""
    faculties = Faculty.objects.filter(is_active=True)

    if request.method == 'POST':
        generated_count = 0
        failed_count = 0

        for faculty in faculties:
            try:
                # Generate PDF
                pdf_response = generate_faculty_pdf(request, faculty.id)
                if isinstance(pdf_response, HttpResponse):
                    generated_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error generating PDF for {faculty.employee_code}: {str(e)}")
                failed_count += 1

        messages.success(request, f'Generated {generated_count} PDFs, {failed_count} failed.')
        return redirect('faculty_list')

    return render(request, 'batch/generate_pdfs.html', {
        'title': 'Batch Generate PDFs',
        'faculty_count': faculties.count(),
        'with_pdf_count': faculties.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='').count()
    })


@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def batch_upload_all_to_cloudinary(request):
    """Batch upload all PDFs to Cloudinary"""
    faculties = Faculty.objects.filter(is_active=True).filter(
        Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url='')
    )

    if request.method == 'POST':
        uploaded_count = 0
        failed_count = 0

        for faculty in faculties:
            try:
                response = upload_faculty_to_cloudinary(request, faculty.id)
                if isinstance(response, JsonResponse):
                    response_data = json.loads(response.content)
                    if response_data.get('success'):
                        uploaded_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error uploading {faculty.employee_code} to Cloudinary: {str(e)}")
                failed_count += 1

        messages.success(request, f'Uploaded {uploaded_count} PDFs to Cloudinary, {failed_count} failed.')
        return redirect('faculty_list')

    return render(request, 'batch/upload_cloudinary.html', {
        'title': 'Batch Upload to Cloudinary',
        'faculty_count': faculties.count()
    })


@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def batch_process_pending(request):
    """Batch process pending tasks"""
    # Get faculty without PDFs
    faculties_no_pdf = Faculty.objects.filter(
        is_active=True
    ).filter(
        Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url='')
    )

    # Get faculty without photos
    faculties_no_photo = Faculty.objects.filter(
        is_active=True
    ).filter(
        Q(cloudinary_photo_url__isnull=True) | Q(cloudinary_photo_url='')
    ).exclude(photo__isnull=True).exclude(photo='')

    pending_tasks = {
        'pdf_generation': faculties_no_pdf.count(),
        'photo_upload': faculties_no_photo.count(),
        'certificate_merge': Certificate.objects.count(),
    }

    return render(request, 'batch/pending_tasks.html', {
        'title': 'Pending Tasks',
        'pending_tasks': pending_tasks,
        'faculties_no_pdf': faculties_no_pdf,
        'faculties_no_photo': faculties_no_photo,
    })


# ==================== EXPORT FORMATS ====================

@login_required
def export_faculty_csv(request):
    """Export faculty data as CSV"""
    return export_faculty_data(request)


@login_required
def export_faculty_json(request):
    """Export faculty data as JSON"""
    faculties = Faculty.objects.all()

    data = []
    for faculty in faculties:
        data.append({
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'joining_date': faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else None,
            'dob': faculty.dob.strftime('%Y-%m-%d') if faculty.dob else None,
            'gender': faculty.gender,
            'address': faculty.address,
            'educational_qualifications': {
                'ssc': {
                    'year': faculty.ssc_year,
                    'percentage': float(faculty.ssc_percent),
                    'school': faculty.ssc_school
                },
                'inter': {
                    'year': faculty.inter_year,
                    'percentage': float(faculty.inter_percent),
                    'college': faculty.inter_college
                },
                'ug': {
                    'year': faculty.ug_year,
                    'percentage': float(faculty.ug_percentage),
                    'college': faculty.ug_college,
                    'specialization': faculty.ug_spec
                },
                'pg': {
                    'year': faculty.pg_year,
                    'percentage': float(faculty.pg_percentage),
                    'college': faculty.pg_college,
                    'specialization': faculty.pg_spec
                },
                'phd': {
                    'status': faculty.phd_degree,
                    'year': faculty.phd_year,
                    'university': faculty.phd_university,
                    'specialization': faculty.phd_spec
                }
            },
            'subjects': faculty.get_subjects_list(),
            'cloudinary_pdf_url': faculty.cloudinary_pdf_url,
            'cloudinary_photo_url': faculty.cloudinary_photo_url,
            'is_active': faculty.is_active
        })

    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="faculty_data.json"'
    return response


@login_required
def export_faculty_xml(request):
    """Export faculty data as XML"""
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    root = ET.Element('faculty_data')

    for faculty in Faculty.objects.all():
        faculty_elem = ET.SubElement(root, 'faculty')

        ET.SubElement(faculty_elem, 'employee_code').text = faculty.employee_code
        ET.SubElement(faculty_elem, 'name').text = faculty.name
        ET.SubElement(faculty_elem, 'department').text = faculty.department
        ET.SubElement(faculty_elem, 'email').text = faculty.email
        ET.SubElement(faculty_elem, 'mobile').text = faculty.mobile
        ET.SubElement(faculty_elem, 'joining_date').text = faculty.joining_date.strftime(
            '%Y-%m-%d') if faculty.joining_date else ''
        ET.SubElement(faculty_elem, 'status').text = 'Active' if faculty.is_active else 'Inactive'

    # Pretty print XML
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    response = HttpResponse(pretty_xml, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="faculty_data.xml"'
    return response


@login_required
def export_faculty_pdf_bundle(request):
    """Export all faculty PDFs as a bundle"""
    return download_all_pdfs(request)


# ==================== SEARCH & FILTER ====================

@login_required
def search_faculty(request):
    """Search faculty"""
    query = request.GET.get('q', '')

    if query:
        faculties = Faculty.objects.filter(
            Q(name__icontains=query) |
            Q(employee_code__icontains=query) |
            Q(department__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile__icontains=query) |
            Q(subjects_dealt__icontains=query)
        ).order_by('name')
    else:
        faculties = Faculty.objects.none()

    return render(request, 'search/results.html', {
        'title': f'Search Results for "{query}"',
        'faculties': faculties,
        'query': query,
        'result_count': faculties.count()
    })


@login_required
def filter_faculty(request):
    """Filter faculty"""
    filters = {}

    department = request.GET.get('department')
    if department:
        filters['department'] = department

    gender = request.GET.get('gender')
    if gender:
        filters['gender'] = gender

    phd_status = request.GET.get('phd_status')
    if phd_status:
        filters['phd_degree'] = phd_status

    pdf_available = request.GET.get('pdf_available')
    if pdf_available == 'yes':
        filters['cloudinary_pdf_url__isnull'] = False
        filters['cloudinary_pdf_url__ne'] = ''
    elif pdf_available == 'no':
        filters['cloudinary_pdf_url__isnull'] = True

    status = request.GET.get('status')
    if status == 'active':
        filters['is_active'] = True
    elif status == 'inactive':
        filters['is_active'] = False

    faculties = Faculty.objects.filter(**filters).order_by('name')

    return render(request, 'search/filter.html', {
        'title': 'Filter Faculty',
        'faculties': faculties,
        'departments': Faculty.objects.values_list('department', flat=True).distinct(),
        'filter_count': faculties.count(),
        'applied_filters': request.GET.dict()
    })


@login_required
def advanced_search(request):
    """Advanced search"""
    return render(request, 'search/advanced.html', {
        'title': 'Advanced Search',
        'departments': Faculty.objects.values_list('department', flat=True).distinct(),
        'qualifications': Faculty.objects.values_list('ug_spec', flat=True).distinct(),
    })


# ==================== UTILITY FUNCTIONS ====================

def generate_faculty_pdf_bytes(faculty):
    """Generate PDF bytes for a faculty"""
    try:
        # This is a simplified version - you would use the actual PDF generation logic
        from io import BytesIO

        # Create a simple PDF (in reality, use your PDF generation code)
        buffer = BytesIO()

        # For now, return None - actual implementation would generate PDF
        return None

    except Exception as e:
        logger.error(f"Error generating PDF bytes: {str(e)}")
        return None


def merge_certificates_with_pdf_bytes(pdf_bytes, faculty):
    """Merge certificates with PDF bytes"""
    try:
        merger = PdfMerger()

        # Add faculty PDF
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file_path = tmp_file.name
            merger.append(tmp_file_path)

        # Add certificates
        certificates = Certificate.objects.filter(faculty=faculty)
        for certificate in certificates:
            if certificate.certificate_file:
                merger.append(certificate.certificate_file.path)

        # Write merged PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as merged_file:
            merger.write(merged_file.name)
            merger.close()

            # Read merged PDF
            with open(merged_file.name, 'rb') as f:
                merged_pdf = f.read()

            # Clean up
            os.unlink(merged_file.name)
            if pdf_bytes:
                os.unlink(tmp_file_path)

        return merged_pdf

    except Exception as e:
        logger.error(f"Error merging certificates: {str(e)}")
        return None


def parse_faculty_data(text):
    """Parse faculty data from text (simplified)"""
    # This is a simplified parser - you would implement actual parsing logic
    data = {}

    # Example parsing logic
    lines = text.split('\n')
    for line in lines:
        if 'Employee Code' in line:
            data['employee_code'] = line.split(':')[-1].strip()
        elif 'Name' in line:
            data['name'] = line.split(':')[-1].strip()
        # Add more parsing logic as needed

    return data


def get_disk_usage():
    """Get disk usage statistics"""
    try:
        import shutil

        total, used, free = shutil.disk_usage("/")

        return {
            'total_gb': total // (2 ** 30),
            'used_gb': used // (2 ** 30),
            'free_gb': free // (2 ** 30),
            'percent_used': (used / total) * 100
        }
    except:
        return {'error': 'Unable to get disk usage'}


def get_memory_usage():
    """Get memory usage statistics"""
    try:
        import psutil

        memory = psutil.virtual_memory()

        return {
            'total_gb': memory.total // (2 ** 30),
            'available_gb': memory.available // (2 ** 30),
            'percent_used': memory.percent,
            'used_gb': memory.used // (2 ** 30)
        }
    except:
        return {'error': 'Unable to get memory usage'}


def redirect_to_dashboard(request):
    """Redirect from old URLs"""
    return redirect('faculty:dashboard')


# ==================== TESTING ROUTES (development only) ====================

if settings.DEBUG:
    def test_pdf_generation(request):
        """Test PDF generation"""
        faculty = Faculty.objects.first()
        if faculty:
            return generate_faculty_pdf(request, faculty.id)
        else:
            return HttpResponse("No faculty found for testing")


    def test_cloudinary_upload(request):
        """Test Cloudinary upload"""
        faculty = Faculty.objects.first()
        if faculty:
            return upload_faculty_to_cloudinary(request, faculty.id)
        else:
            return JsonResponse({'success': False, 'error': 'No faculty found'})


    def test_certificate_merge(request):
        """Test certificate merging"""
        faculty = Faculty.objects.first()
        if faculty:
            return merge_certificates(request, faculty.id)
        else:
            return JsonResponse({'success': False, 'error': 'No faculty found'})


# ==================== ADDED NEW FUNCTIONALITIES ====================

@login_required
def faculty_analytics(request):
    """Faculty analytics dashboard"""
    total_faculty = Faculty.objects.count()
    active_faculty = Faculty.objects.filter(is_active=True).count()

    # Department distribution
    dept_distribution = Faculty.objects.values('department').annotate(
        count=Count('id'),
        active=Count('id', filter=Q(is_active=True)),
        with_pdf=Count('id', filter=~Q(cloudinary_pdf_url__isnull=True) & ~Q(cloudinary_pdf_url=''))
    ).order_by('-count')

    # Qualification statistics
    qualification_stats = {
        'phd_completed': Faculty.objects.filter(phd_degree='Completed').count(),
        'phd_pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
        'pg_completed': Faculty.objects.filter(pg_year__isnull=False).count(),
        'ug_completed': Faculty.objects.filter(ug_year__isnull=False).count(),
    }

    # Experience distribution
    experience_distribution = []
    for i in range(0, 31, 5):
        start = i
        end = i + 4 if i < 30 else 100
        count = Faculty.objects.filter(
            joining_date__lte=date.today() - timedelta(days=start * 365),
            joining_date__gte=date.today() - timedelta(days=end * 365) if end < 100 else None
        ).count()
        experience_distribution.append({
            'range': f'{start}-{end} years' if end < 100 else '30+ years',
            'count': count
        })

    # Gender distribution
    gender_distribution = Faculty.objects.values('gender').annotate(
        count=Count('id')
    ).order_by('-count')

    return render(request, 'analytics/dashboard.html', {
        'title': 'Faculty Analytics',
        'total_faculty': total_faculty,
        'active_faculty': active_faculty,
        'dept_distribution': dept_distribution,
        'qualification_stats': qualification_stats,
        'experience_distribution': experience_distribution,
        'gender_distribution': gender_distribution,
        'pdf_coverage': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
            cloudinary_pdf_url='').count() / total_faculty * 100 if total_faculty > 0 else 0
    })


@login_required
def faculty_timeline(request, faculty_id):
    """View faculty activity timeline"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Get all activities for this faculty
    logs = FacultyLog.objects.filter(faculty=faculty).order_by('-created_at')
    certificates = Certificate.objects.filter(faculty=faculty).order_by('-issue_date')
    uploads = CloudinaryUpload.objects.filter(faculty=faculty).order_by('-upload_date')

    # Combine all activities
    timeline_events = []

    # Add faculty creation
    timeline_events.append({
        'date': faculty.created_at,
        'type': 'faculty_created',
        'title': 'Faculty Profile Created',
        'description': f'Faculty {faculty.employee_code} was added to the system',
        'user': 'System'
    })

    # Add logs
    for log in logs:
        timeline_events.append({
            'date': log.created_at,
            'type': 'log',
            'title': f'{log.action}',
            'description': log.details,
            'user': log.performed_by
        })

    # Add certificates
    for cert in certificates:
        timeline_events.append({
            'date': cert.issue_date,
            'type': 'certificate',
            'title': f'Certificate Added: {cert.certificate_type}',
            'description': f'Certificate issued by {cert.issued_by}',
            'user': 'System'
        })

    # Add uploads
    for upload in uploads:
        timeline_events.append({
            'date': upload.upload_date,
            'type': 'upload',
            'title': f'{upload.upload_type.title()} Uploaded',
            'description': f'{upload.upload_type} uploaded to Cloudinary',
            'user': upload.uploaded_by
        })

    # Sort by date
    timeline_events.sort(key=lambda x: x['date'], reverse=True)

    return render(request, 'faculty/timeline.html', {
        'title': f'Activity Timeline - {faculty.name}',
        'faculty': faculty,
        'timeline_events': timeline_events,
        'total_events': len(timeline_events)
    })


@login_required
def faculty_comparison(request):
    """Compare multiple faculty members"""
    faculty_ids = request.GET.getlist('faculty_ids')

    if not faculty_ids:
        faculties = Faculty.objects.none()
        return render(request, 'comparison/select.html', {
            'title': 'Compare Faculty',
            'faculties': Faculty.objects.all().order_by('department', 'name')
        })

    faculties = Faculty.objects.filter(id__in=faculty_ids).order_by('department', 'name')

    # Prepare comparison data
    comparison_data = []
    for faculty in faculties:
        comparison_data.append({
            'id': faculty.id,
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'experience': calculate_experience(faculty.joining_date),
            'qualification': faculty.phd_degree if faculty.phd_degree != 'Not Started' else faculty.pg_spec,
            'subjects': faculty.get_subjects_list(),
            'pdf_available': bool(faculty.cloudinary_pdf_url),
            'photo_available': bool(faculty.cloudinary_photo_url),
            'certificate_count': Certificate.objects.filter(faculty=faculty).count(),
            'joining_date': faculty.joining_date,
            'email': faculty.email,
            'mobile': faculty.mobile,
        })

    return render(request, 'comparison/results.html', {
        'title': 'Faculty Comparison',
        'comparison_data': comparison_data,
        'selected_count': len(comparison_data)
    })


@login_required
@permission_required('dashboard.add_faculty', raise_exception=True)
def faculty_bulk_actions(request):
    """Perform bulk actions on faculty"""
    if request.method == 'POST':
        action = request.POST.get('action')
        faculty_ids = request.POST.getlist('faculty_ids')

        if not faculty_ids:
            messages.error(request, 'Please select at least one faculty member.')
            return redirect('faculty_list')

        faculties = Faculty.objects.filter(id__in=faculty_ids)

        if action == 'generate_pdfs':
            generated = 0
            for faculty in faculties:
                try:
                    # Generate PDF for each faculty
                    generate_faculty_pdf(request, faculty.id)
                    generated += 1
                except Exception as e:
                    logger.error(f"Error generating PDF for {faculty.employee_code}: {str(e)}")

            messages.success(request, f'Generated PDFs for {generated} faculty members.')

        elif action == 'upload_to_cloudinary':
            uploaded = 0
            for faculty in faculties:
                try:
                    # Upload to Cloudinary
                    response = upload_faculty_to_cloudinary(request, faculty.id)
                    if isinstance(response, JsonResponse):
                        uploaded += 1
                except Exception as e:
                    logger.error(f"Error uploading {faculty.employee_code} to Cloudinary: {str(e)}")

            messages.success(request, f'Uploaded {uploaded} faculty PDFs to Cloudinary.')

        elif action == 'export_data':
            # Export selected faculty data
            return export_selected_faculty_data(request, faculty_ids)

        elif action == 'mark_inactive':
            faculties.update(is_active=False)
            messages.success(request, f'Marked {faculties.count()} faculty members as inactive.')

        return redirect('faculty_list')

    return render(request, 'bulk/actions.html', {
        'title': 'Bulk Actions',
        'faculties': Faculty.objects.filter(is_active=True).order_by('department', 'name')
    })


def export_selected_faculty_data(request, faculty_ids):
    """Export data for selected faculty"""
    faculties = Faculty.objects.filter(id__in=faculty_ids)

    format = request.POST.get('format', 'csv')

    if format == 'csv':
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Employee Code', 'Name', 'Department', 'Email', 'Mobile',
            'Joining Date', 'Experience', 'Subjects', 'PDF Available'
        ])

        # Write data
        for faculty in faculties:
            writer.writerow([
                faculty.employee_code,
                faculty.name,
                faculty.department,
                faculty.email,
                faculty.mobile,
                faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else '',
                calculate_experience(faculty.joining_date),
                ', '.join(faculty.get_subjects_list()),
                'Yes' if faculty.cloudinary_pdf_url else 'No'
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="selected_faculty_data.csv"'
        return response

    else:
        # Default to JSON
        data = []
        for faculty in faculties:
            data.append({
                'employee_code': faculty.employee_code,
                'name': faculty.name,
                'department': faculty.department,
                'email': faculty.email,
                'mobile': faculty.mobile,
                'joining_date': faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else None,
                'experience': calculate_experience(faculty.joining_date),
                'subjects': faculty.get_subjects_list(),
                'pdf_url': faculty.cloudinary_pdf_url,
                'photo_url': faculty.cloudinary_photo_url,
            })

        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="selected_faculty_data.json"'
        return response


@login_required
def faculty_quick_view(request):
    """Quick view modal for faculty"""
    faculty_id = request.GET.get('faculty_id')
    faculty = get_object_or_404(Faculty, id=faculty_id)

    context = {
        'faculty': faculty,
        'experience': calculate_experience(faculty.joining_date),
        'subjects': faculty.get_subjects_list()[:5],  # First 5 subjects
        'has_pdf': bool(faculty.cloudinary_pdf_url),
        'has_photo': bool(faculty.cloudinary_photo_url),
        'certificate_count': Certificate.objects.filter(faculty=faculty).count(),
    }

    return render(request, 'faculty/quick_view.html', context)


@login_required
def faculty_export_package(request, faculty_id):
    """Export complete faculty package (PDF + certificates)"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        import zipfile
        import requests
        from io import BytesIO

        # Create zip file in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Add faculty PDF if available
            if faculty.cloudinary_pdf_url:
                try:
                    response = requests.get(faculty.cloudinary_pdf_url)
                    if response.status_code == 200:
                        filename = f"faculty_{faculty.employee_code}.pdf"
                        zf.writestr(filename, response.content)
                except Exception as e:
                    logger.error(f"Error downloading PDF: {str(e)}")

            # Add certificates
            certificates = Certificate.objects.filter(faculty=faculty)
            for cert in certificates:
                if cert.cloudinary_url:
                    try:
                        response = requests.get(cert.cloudinary_url)
                        if response.status_code == 200:
                            filename = f"certificate_{cert.certificate_type.replace(' ', '_')}.pdf"
                            zf.writestr(filename, response.content)
                    except Exception as e:
                        logger.error(f"Error downloading certificate: {str(e)}")
                elif cert.certificate_file:
                    # Add local certificate file
                    try:
                        with open(cert.certificate_file.path, 'rb') as f:
                            filename = f"certificate_{cert.certificate_type.replace(' ', '_')}.pdf"
                            zf.writestr(filename, f.read())
                    except Exception as e:
                        logger.error(f"Error reading certificate file: {str(e)}")

            # Add faculty data as JSON
            faculty_data = {
                'employee_code': faculty.employee_code,
                'name': faculty.name,
                'department': faculty.department,
                'email': faculty.email,
                'mobile': faculty.mobile,
                'joining_date': faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else None,
                'experience': calculate_experience(faculty.joining_date),
                'subjects': faculty.get_subjects_list(),
            }
            zf.writestr('faculty_info.json', json.dumps(faculty_data, indent=2))

        memory_file.seek(0)

        # Create response
        response = HttpResponse(memory_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="faculty_package_{faculty.employee_code}.zip"'

        # Log the action
        FacultyLog.objects.create(
            faculty=faculty,
            action='Package Exported',
            details=f'Complete faculty package exported: {faculty.employee_code}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return response

    except Exception as e:
        logger.error(f"Error creating faculty package: {str(e)}")
        messages.error(request, f'Error creating package: {str(e)}')
        return redirect('faculty_detail', faculty_id=faculty_id)


@login_required
def faculty_reminders(request):
    """View and manage faculty reminders"""
    today = date.today()

    # Get faculty with upcoming certificate expirations
    expiring_certificates = Certificate.objects.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=30)
    ).select_related('faculty')

    # Get faculty with missing PDFs
    missing_pdfs = Faculty.objects.filter(
        is_active=True,
        cloudinary_pdf_url__isnull=True
    )

    # Get faculty with missing photos
    missing_photos = Faculty.objects.filter(
        is_active=True,
        cloudinary_photo_url__isnull=True
    ).exclude(photo__isnull=True).exclude(photo='')

    # Get recent activities needing follow-up
    recent_activities = FacultyLog.objects.filter(
        created_at__gte=today - timedelta(days=7)
    ).order_by('-created_at')[:10]

    return render(request, 'reminders/dashboard.html', {
        'title': 'Faculty Reminders',
        'expiring_certificates': expiring_certificates,
        'missing_pdfs': missing_pdfs,
        'missing_photos': missing_photos,
        'recent_activities': recent_activities,
        'today': today,
    })


@login_required
@csrf_exempt
def faculty_api_webhook(request):
    """Webhook for external systems to update faculty data"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key = request.headers.get('X-API-Key')

            # Verify API key (configure in settings)
            if not api_key or api_key != getattr(settings, 'FACULTY_API_KEY', ''):
                return JsonResponse({'error': 'Invalid API key'}, status=401)

            action = data.get('action')
            employee_code = data.get('employee_code')

            if not employee_code:
                return JsonResponse({'error': 'Employee code is required'}, status=400)

            faculty, created = Faculty.objects.get_or_create(
                employee_code=employee_code.upper(),
                defaults={
                    'name': data.get('name', ''),
                    'department': data.get('department', ''),
                    'email': data.get('email', ''),
                    'mobile': data.get('mobile', ''),
                    'is_active': True,
                }
            )

            if action == 'update':
                # Update faculty fields
                for field in ['name', 'department', 'email', 'mobile', 'joining_date', 'dob']:
                    if field in data and hasattr(faculty, field):
                        setattr(faculty, field, data[field])
                faculty.save()

            elif action == 'upload_pdf':
                # Handle PDF upload via URL
                pdf_url = data.get('pdf_url')
                if pdf_url:
                    faculty.cloudinary_pdf_url = pdf_url
                    faculty.save()

            elif action == 'upload_certificate':
                # Handle certificate upload
                certificate_data = data.get('certificate', {})
                Certificate.objects.create(
                    faculty=faculty,
                    certificate_type=certificate_data.get('type', 'Certificate'),
                    issued_by=certificate_data.get('issued_by', 'Unknown'),
                    issue_date=certificate_data.get('issue_date', date.today()),
                    expiry_date=certificate_data.get('expiry_date'),
                    description=certificate_data.get('description', ''),
                    is_verified=False
                )

            return JsonResponse({
                'success': True,
                'faculty_id': faculty.id,
                'employee_code': faculty.employee_code,
                'created': created,
                'action': action
            })

        except Exception as e:
            logger.error(f"API webhook error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def faculty_qrcode(request, faculty_id):
    """Generate QR code for faculty profile"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        import qrcode
        from io import BytesIO
        import base64

        # Create QR code data
        qr_data = {
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'profile_url': request.build_absolute_uri(reverse('faculty_detail', args=[faculty.id])),
            'pdf_url': faculty.cloudinary_pdf_url,
        }

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render(request, 'faculty/qrcode.html', {
            'title': f'QR Code - {faculty.name}',
            'faculty': faculty,
            'qr_code': qr_base64,
            'qr_data': qr_data,
        })

    except ImportError:
        messages.error(request, 'QR code generation requires qrcode library')
        return redirect('faculty_detail', faculty_id=faculty_id)
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        messages.error(request, f'Error generating QR code: {str(e)}')
        return redirect('faculty_detail', faculty_id=faculty_id)


@login_required
def faculty_print_view(request, faculty_id):
    """Print-friendly faculty view"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    context = {
        'faculty': faculty,
        'experience': calculate_experience(faculty.joining_date),
        'subjects': faculty.get_subjects_list(),
        'certificates': Certificate.objects.filter(faculty=faculty),
        'educational_details': [
            {'degree': 'SSC', 'year': faculty.ssc_year, 'percent': faculty.ssc_percent,
             'institution': faculty.ssc_school},
            {'degree': 'Intermediate', 'year': faculty.inter_year, 'percent': faculty.inter_percent,
             'institution': faculty.inter_college},
            {'degree': 'B.Tech', 'year': faculty.ug_year, 'percent': faculty.ug_percentage,
             'institution': faculty.ug_college, 'specialization': faculty.ug_spec},
            {'degree': 'M.Tech', 'year': faculty.pg_year, 'percent': faculty.pg_percentage,
             'institution': faculty.pg_college, 'specialization': faculty.pg_spec},
            {'degree': 'Ph.D', 'year': faculty.phd_year, 'status': faculty.phd_degree,
             'institution': faculty.phd_university, 'specialization': faculty.phd_spec},
        ],
        'current_date': date.today().strftime('%d-%m-%Y'),
        'print_mode': True,
    }

    return render(request, 'faculty/print.html', context)


@login_required
def faculty_search_advanced_api(request):
    """Advanced search API for faculty"""
    query = request.GET.get('q', '')
    department = request.GET.get('department', '')
    qualification = request.GET.get('qualification', '')
    min_experience = request.GET.get('min_experience', 0)
    has_pdf = request.GET.get('has_pdf', '')

    faculties = Faculty.objects.filter(is_active=True)

    if query:
        faculties = faculties.filter(
            Q(name__icontains=query) |
            Q(employee_code__icontains=query) |
            Q(email__icontains=query) |
            Q(subjects_dealt__icontains=query)
        )

    if department:
        faculties = faculties.filter(department__icontains=department)

    if qualification:
        if qualification == 'phd':
            faculties = faculties.filter(phd_degree='Completed')
        elif qualification == 'pg':
            faculties = faculties.filter(pg_year__isnull=False)
        elif qualification == 'ug':
            faculties = faculties.filter(ug_year__isnull=False)

    if min_experience:
        try:
            min_years = int(min_experience)
            cutoff_date = date.today() - timedelta(days=min_years * 365)
            faculties = faculties.filter(joining_date__lte=cutoff_date)
        except ValueError:
            pass

    if has_pdf == 'yes':
        faculties = faculties.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='')
    elif has_pdf == 'no':
        faculties = faculties.filter(Q(cloudinary_pdf_url__isnull=True) | Q(cloudinary_pdf_url=''))

    # Format results
    results = []
    for faculty in faculties[:50]:  # Limit to 50 results
        results.append({
            'id': faculty.id,
            'employee_code': faculty.employee_code,
            'name': faculty.name,
            'department': faculty.department,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'experience': calculate_experience(faculty.joining_date),
            'subjects': faculty.get_subjects_list(),
            'has_pdf': bool(faculty.cloudinary_pdf_url),
            'pdf_url': faculty.cloudinary_pdf_url,
            'has_photo': bool(faculty.cloudinary_photo_url),
            'photo_url': faculty.cloudinary_photo_url,
        })

    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results)
    })