# dashboard/views.py - COMPLETE MERGED VERSION WITH ALL FUNCTIONS
from weasyprint import HTML
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
import tempfile
import os

import os
import json
import csv
import tempfile
import logging
import time
import uuid
import zipfile
from datetime import datetime, date, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Any
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, FileResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.urls import reverse
from django.utils import timezone
import pdfkit
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests

# Add these imports for students
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Faculty, Certificate, FacultyLog, CloudinaryUpload, Student, Subject, Department
from .forms import FacultyForm, CertificateForm, LoginForm, BulkUploadForm, SubjectForm, StudentForm
from .utils import (
    calculate_experience, generate_pdf_from_html,
    merge_pdfs, extract_text_from_pdf, validate_faculty_data,
    calculate_age, format_date, get_academic_year,
    send_email_notification, generate_qr_code,
    export_to_excel, validate_student_data
)

# Configure logging
logger = logging.getLogger(__name__)

# Safeguard optional libraries
try:
    import pandas as pd
except ImportError:
    pd = None
    logger.warning("Pandas library not installed. Bulk upload features will be limited.")

try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil library not installed. System monitoring features will be limited.")

try:
    import matplotlib

    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    plt = None
    np = None
    logger.warning("Matplotlib library not installed. Chart features will be limited.")

# Initialize Cloudinary if configured
if hasattr(settings, 'CLOUDINARY_CLOUD_NAME'):
    try:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        logger.info("Cloudinary initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Cloudinary: {str(e)}")
else:
    logger.warning("Cloudinary credentials not found in settings")


# ==================== CLOUDINARY SYNC FUNCTIONS (MERGED VERSION) ====================

@login_required
def sync_to_cloudinary(request, faculty_id):
    """
    Upload faculty PDF and photo to Cloudinary and store URLs.
    Updated merged version that handles both PDF and photo uploads.
    """
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # -------------------------------------------------
    # 1. UPLOAD PDF (if not already uploaded)
    # -------------------------------------------------
    if faculty.pdf_document and not faculty.cloudinary_pdf_url:
        try:
            with faculty.pdf_document.open("rb") as pdf_file:
                response = cloudinary.uploader.upload(
                    pdf_file,
                    folder="faculty_pdfs",
                    resource_type="raw",
                    public_id=f"faculty_{faculty.employee_code}_profile",
                    overwrite=True,
                )

                faculty.cloudinary_pdf_url = response["secure_url"]
                faculty.save()

                # CORRECTED: Removed format, bytes, raw_response
                CloudinaryUpload.objects.create(
                    faculty=faculty,
                    upload_type="pdf",
                    cloudinary_url=response["secure_url"],
                    public_id=response["public_id"],
                    resource_type=response["resource_type"],
                    uploaded_by=request.user.username,
                )
                logger.info(f"PDF uploaded to Cloudinary for faculty {faculty.employee_code}")

        except Exception as e:
            logger.error(f"PDF Cloudinary upload error: {str(e)}")
            messages.error(request, "Error uploading faculty PDF to Cloudinary")
            return redirect("dashboard:faculty_dashboard")

    # -------------------------------------------------
    # 2. UPLOAD PHOTO (if exists and not uploaded)
    # -------------------------------------------------
    if faculty.photo and not faculty.cloudinary_photo_url:
        try:
            with faculty.photo.open("rb") as photo_file:
                response = cloudinary.uploader.upload(
                    photo_file,
                    folder="faculty_photos",
                    public_id=f"faculty_{faculty.employee_code}_photo",
                    overwrite=True,
                    transformation=[
                        {'width': 300, 'height': 300, 'crop': 'fill'},
                        {'quality': 'auto:good'}
                    ]
                )

                faculty.cloudinary_photo_url = response["secure_url"]
                faculty.save()

                # CORRECTED: Record the upload - removed format, bytes, raw_response
                CloudinaryUpload.objects.create(
                    faculty=faculty,
                    upload_type="photo",
                    cloudinary_url=response["secure_url"],
                    public_id=response["public_id"],
                    resource_type=response["resource_type"],
                    uploaded_by=request.user.username,
                )
                logger.info(f"Photo uploaded to Cloudinary for faculty {faculty.employee_code}")

        except Exception as e:
            logger.error(f"Photo Cloudinary upload error: {str(e)}")
            messages.error(request, "Error uploading faculty photo to Cloudinary")
            return redirect("dashboard:faculty_dashboard")

    # Log the action
    FacultyLog.objects.create(
        faculty=faculty,
        action='Synced to Cloudinary',
        details=f'Faculty {faculty.employee_code} synced to Cloudinary (PDF: {bool(faculty.cloudinary_pdf_url)}, Photo: {bool(faculty.cloudinary_photo_url)})',
        performed_by=request.user.username,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(
        request,
        f"Faculty {faculty.employee_code} successfully synced to Cloudinary"
    )
    return redirect("dashboard:faculty_dashboard")


# =========================================================
# UPLOAD TO CLOUDINARY (ALIAS – REQUIRED FOR URLS)
# =========================================================

@login_required
def upload_to_cloudinary(request, faculty_id):
    """
    Alias for backward compatibility.
    DO NOT REMOVE – used by dashboard/urls.py
    """
    return sync_to_cloudinary(request, faculty_id)


# ==================== AUTHENTICATION FUNCTIONS ====================

def login_view(request):
    """Login selector page - Updated with explicit flags"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')

    return render(request, 'dashboard/login.html', {
        'title': 'Login - ANURAG ENGINEERING COLLEGE',
        'student_login': False,
        'admin_login': False,
    })


@csrf_protect
def admin_login(request):
    """Admin login page - Updated with proper authentication"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Admin login successful!')
            return redirect('dashboard:dashboard')
        else:
            error = 'Invalid admin credentials'
            messages.error(request, error)

    return render(request, 'dashboard/login.html', {
        'title': 'Admin Login - ANURAG ENGINEERING COLLEGE',
        'admin_login': True,
        'error': error,
    })


# =====================================================
# STUDENT LOGIN (MERGED VERSION)
# =====================================================
def student_login(request):
    """Dedicated student login with hardcoded credentials"""
    # If already logged in via session, redirect
    if request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')

    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Simple static login (as per your design)
        if username == "anrkitstudent" and password == "anrkitstudent":
            request.session["student_logged_in"] = True
            request.session["student_username"] = username
            messages.success(request, "Student login successful!")
            return redirect("dashboard:students_data")

        error = "Invalid student credentials"
        messages.error(request, error)
        return render(request, 'dashboard/login.html', {
            'student_login': True,
            'error': error,
            'title': 'Student Login - ANURAG ENGINEERING COLLEGE'
        })

    # Render student login template
    return render(request, 'dashboard/login.html', {
        'student_login': True,
        'error': error,
        'title': 'Student Login - ANURAG ENGINEERING COLLEGE'
    })


def logout_view(request):
    """Logout view - handles both admin and student logout"""
    # Logout Django user
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
    else:
        messages.success(request, 'Logged out successfully.')

    # Clear student session
    if 'student_logged_in' in request.session:
        del request.session['student_logged_in']
    if 'student_username' in request.session:
        del request.session['student_username']
    if 'student_role' in request.session:
        del request.session['student_role']

    return redirect('dashboard:login')


# =====================================================
# STUDENT LOGOUT (MERGED VERSION)
# =====================================================
from django.contrib import messages
from django.shortcuts import redirect

def student_logout(request):
    """
    Logout student safely by flushing session
    """
    request.session.flush()   # Clears entire session securely
    messages.success(request, "Student logged out successfully.")
    return redirect('dashboard:student_login')


def admin_logout(request):
    """Admin logout - logs out admin user"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
    return redirect('dashboard:admin_login')


# ==================== HOME & DASHBOARD ====================

def home(request):
    """Home page view"""
    # Get statistics for home page
    total_faculty = Faculty.objects.count()
    active_faculty = Faculty.objects.filter(is_active=True).count()
    total_students = Student.objects.count()
    departments = Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:5]

    # Get recent activities
    recent_activities = FacultyLog.objects.order_by('-created_at')[:5]

    return render(request, 'dashboard/home.html', {
        'title': 'Faculty Management System - Home',
        'total_faculty': total_faculty,
        'active_faculty': active_faculty,
        'total_students': total_students,
        'departments': departments,
        'recent_activities': recent_activities,
        'show_hero': True,
    })


@login_required
def dashboard(request):
    """Main dashboard - protected by login_required"""
    # Calculate statistics
    total_faculty = Faculty.objects.count()
    with_phd_count = Faculty.objects.filter(phd_degree='Completed').count()
    active_faculty = Faculty.objects.filter(is_active=True).count()
    total_certificates = Certificate.objects.count()

    # Department statistics
    departments = Faculty.objects.values('department').annotate(
        count=Count('id'),
        active=Count('id', filter=Q(is_active=True))
    ).order_by('-count')

    # Recent activities
    recent_logs = FacultyLog.objects.select_related('faculty').order_by('-created_at')[:10]

    # Recent uploads
    recent_uploads = Faculty.objects.select_related('department').order_by('-created_at')[:5]

    # Calculate experience distribution
    today = date.today()
    exp_distribution = {
        '0-5': 0,
        '5-10': 0,
        '10-15': 0,
        '15+': 0
    }

    for faculty in Faculty.objects.all():
        if faculty.joining_date:
            exp_years = (today - faculty.joining_date).days / 365.25
            if exp_years <= 5:
                exp_distribution['0-5'] += 1
            elif exp_years <= 10:
                exp_distribution['5-10'] += 1
            elif exp_years <= 15:
                exp_distribution['10-15'] += 1
            else:
                exp_distribution['15+'] += 1

    context = {
        'title': 'Dashboard',
        'total_faculty': total_faculty,
        'with_phd': with_phd_count,
        'active_faculty': active_faculty,
        'total_certificates': total_certificates,
        'departments': departments,
        'recent_uploads': recent_uploads,
        'recent_logs': recent_logs,
        'exp_distribution': exp_distribution,
        'today': today,
        'user': request.user,
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
def admin_dashboard(request):
    """Admin dashboard - separate from main dashboard"""
    # Only superusers can access admin dashboard
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard')

    # Get comprehensive statistics
    total_faculty = Faculty.objects.count()
    active_faculty = Faculty.objects.filter(is_active=True).count()
    with_phd_count = Faculty.objects.filter(phd_degree='Completed').count()
    total_students = Student.objects.count()
    total_certificates = Certificate.objects.count()
    cloudinary_uploads = CloudinaryUpload.objects.count()

    # Get recent activities
    recent_logs = FacultyLog.objects.all().order_by('-created_at')[:10]

    # Get system statistics if psutil is available
    system_stats = {}
    if psutil:
        try:
            system_stats = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            system_stats = {'error': str(e)}

    # Get user activity
    user_activity = {
        'total_users': User.objects.count(),
        'active_today': FacultyLog.objects.filter(
            created_at__date=date.today()
        ).values('performed_by').distinct().count(),
    }

    # Get department statistics
    departments = Faculty.objects.values('department').annotate(
        count=Count('id'),
        active=Count('id', filter=Q(is_active=True))
    ).order_by('-count')

    # Add percentage
    for dept in departments:
        dept['percentage'] = (dept['count'] / total_faculty * 100) if total_faculty > 0 else 0

    context = {
        'title': 'Admin Dashboard',
        'total_faculty': total_faculty,
        'active_faculty': active_faculty,
        'total_students': total_students,
        'total_certificates': total_certificates,
        'cloudinary_uploads': cloudinary_uploads,
        'with_phd': with_phd_count,
        'departments': departments,
        'recent_logs': recent_logs,
        'system_stats': system_stats,
        'user_activity': user_activity,
        'has_psutil': psutil is not None,
        'recent_uploads': Faculty.objects.order_by('-created_at')[:5],
    }

    return render(request, "dashboard/admin_dashboard.html", context)


def student_dashboard(request):
    """Student dashboard - separate from students data view"""
    # Check if student is logged in via session
    if not request.session.get('student_logged_in'):
        messages.error(request, 'Please login to access student dashboard')
        return redirect('dashboard:student_login')

    # Get student from session
    student_username = request.session.get('student_username', 'anrkitstudent')

    # Try to get student data
    try:
        student = Student.objects.filter(ht_no=student_username).first()
        if not student:
            # Create a dummy student if not found
            student = {
                'ht_no': student_username,
                'student_name': 'Student User',
                'year': 'II',
                'sem': 'II',
                'branch': 'Computer Science',
            }
    except Exception as e:
        logger.error(f"Error getting student data: {str(e)}")
        student = None

    # Get student statistics
    total_students = Student.objects.count()
    recent_students = Student.objects.order_by('-created_at')[:5]

    # Get student's certificates if available
    certificates = []
    if student and hasattr(student, 'id'):
        # Check for certificate fields
        cert_fields = ['achievement_certificate', 'internship_certificate',
                       'courses_certificate', 'sdp_certificate', 'extra_certificate',
                       'placement_offer', 'national_exam_certificate']

        for field in cert_fields:
            if getattr(student, field):
                certificates.append({
                    'type': field.replace('_', ' ').title(),
                    'has_file': True
                })

    context = {
        'student': student,
        'title': 'Student Dashboard',
        'total_students': total_students,
        'recent_students': recent_students,
        'certificates': certificates,
        'is_student': True,
    }

    return render(request, "dashboard/student_dashboard.html", context)


def redirect_to_dashboard(request):
    """Redirect to dashboard based on authentication"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('dashboard:admin_dashboard')
        else:
            return redirect('dashboard:dashboard')
    elif request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard')
    else:
        return redirect('dashboard:login')


# ==================== SINGLE PAGE FACULTY DASHBOARD - MERGED VERSION ====================

@login_required
def faculty_dashboard(request):
    """Single page faculty dashboard - uses new merged template structure"""
    # Check for PDF mode
    pdf_mode = request.GET.get("print") == "1"

    if pdf_mode:
        faculty_id = request.GET.get("id")
        if not faculty_id:
            return HttpResponseBadRequest("Faculty ID is required for PDF mode")

        faculty = get_object_or_404(Faculty, id=faculty_id)

        # Calculate experience
        experience = faculty.total_experience if hasattr(faculty, "total_experience") else calculate_experience(
            faculty.joining_date) if faculty.joining_date else "N/A"

        return render(request, "dashboard/faculty.html", {
            "faculty": faculty,
            "pdf_mode": pdf_mode,
            "current_date": timezone.now(),
            "experience": experience,
            "cloudinary_status": {
                "has_pdf": bool(faculty.cloudinary_pdf_url)
            }
        })

    # Non-PDF mode (existing logic)
    faculties = Faculty.objects.all().order_by('staff_name')

    faculty_id = request.GET.get('id')
    faculty = None

    if faculty_id:
        faculty = get_object_or_404(Faculty, id=faculty_id)
    elif faculties.exists():
        faculty = faculties.first()  # default selection

    # Check if analytics mode
    is_analytics = request.GET.get('analytics') == 'true' or (not faculty and faculties.exists())

    if is_analytics:
        return faculty_analytics(request)

    certificates = Certificate.objects.filter(faculty=faculty) if faculty else []

    # Calculate experience
    experience = calculate_experience(faculty.joining_date) if faculty and faculty.joining_date else "N/A"

    cloudinary_status = {
        'has_pdf': bool(faculty.cloudinary_pdf_url) if faculty else False,
        'has_photo': bool(faculty.cloudinary_photo_url) if faculty else False,
    }

    # Get current date
    current_date = timezone.now()

    return render(request, 'dashboard/faculty.html', {
        'faculties': faculties,
        'faculty': faculty,
        'certificates': certificates,
        'experience': experience,
        'cloudinary_status': cloudinary_status,
        'current_date': current_date,
        'is_analytics': False,
        'pdf_mode': pdf_mode,
        'title': f'Faculty Profile - {faculty.staff_name}' if faculty else 'Faculty Dashboard',
    })


@login_required
def faculty_analytics(request):
    """Faculty analytics dashboard"""
    total_faculty = Faculty.objects.count()

    # Qualification statistics
    qualification_stats = {
        'phd_completed': Faculty.objects.filter(phd_degree='Completed').count(),
        'phd_pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
        'pg_only': Faculty.objects.filter(
            pg_year__isnull=False,
            phd_degree__in=['', 'Not Started', 'None']
        ).count(),
        'ug_only': Faculty.objects.filter(
            ug_year__isnull=False,
            pg_year__isnull=True,
            phd_degree__in=['', 'Not Started', 'None']
        ).count(),
    }

    # Department statistics
    departments = Faculty.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    # Add percentage
    for dept in departments:
        dept['percentage'] = (dept['count'] / total_faculty * 100) if total_faculty > 0 else 0

    # Experience statistics
    today = date.today()
    experience_stats = {
        '0_5': 0,
        '5_10': 0,
        '10_plus': 0
    }

    faculties = Faculty.objects.all()
    for faculty in faculties:
        if faculty.joining_date:
            years_exp = today.year - faculty.joining_date.year
            if years_exp <= 5:
                experience_stats['0_5'] += 1
            elif years_exp <= 10:
                experience_stats['5_10'] += 1
            else:
                experience_stats['10_plus'] += 1

    context = {
        'is_analytics': True,
        'total_faculty': total_faculty,
        'qualification_stats': qualification_stats,
        'departments': departments,
        'experience_stats': experience_stats,
        'faculties': faculties[:10],  # Show recent 10
        'title': 'Faculty Analytics',
    }

    return render(request, 'dashboard/faculty.html', context)


# ==================== FACULTY LIST & MANAGEMENT ====================

@login_required
def faculty_list(request):
    """
    Display list of all faculty members with search and filters
    """
    # Get all faculty
    faculty_list = Faculty.objects.all().order_by('staff_name')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        faculty_list = faculty_list.filter(
            Q(staff_name__icontains=search_query) |
            Q(employee_code__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    # Filter by department
    department_filter = request.GET.get('department', '')
    if department_filter:
        faculty_list = faculty_list.filter(department__icontains=department_filter)

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'active':
            faculty_list = faculty_list.filter(is_active=True)
        elif status_filter == 'inactive':
            faculty_list = faculty_list.filter(is_active=False)

    # Filter by qualification
    qualification_filter = request.GET.get('qualification', '')
    if qualification_filter:
        if qualification_filter == 'phd':
            faculty_list = faculty_list.filter(phd_degree='Completed')
        elif qualification_filter == 'pg':
            faculty_list = faculty_list.filter(pg_year__isnull=False, phd_degree__in=['', 'Not Started', 'None'])

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(faculty_list, 20)  # 20 items per page

    try:
        faculties = paginator.page(page)
    except PageNotAnInteger:
        faculties = paginator.page(1)
    except EmptyPage:
        faculties = paginator.page(paginator.num_pages)

    # Get unique departments for filter dropdown
    departments = Faculty.objects.values_list('department', flat=True).distinct().order_by('department')

    context = {
        'faculties': faculties,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'qualification_filter': qualification_filter,
        'total_faculty': faculty_list.count(),
        'page_title': 'Faculty Directory',
        'active_page': 'faculty_list',
    }

    return render(request, 'dashboard/faculty_list.html', context)


@login_required
def add_faculty(request):
    """
    Add new faculty member
    """
    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                faculty = form.save()

                # Upload photo to Cloudinary if provided
                if 'photo' in request.FILES:
                    photo_file = request.FILES['photo']
                    try:
                        cloudinary_response = cloudinary.uploader.upload(
                            photo_file,
                            folder="faculty_photos",
                            public_id=f"faculty_{faculty.employee_code}",
                            overwrite=True,
                            transformation=[
                                {'width': 300, 'height': 300, 'crop': 'fill'},
                                {'quality': 'auto:good'}
                            ]
                        )
                        faculty.cloudinary_photo_url = cloudinary_response['secure_url']
                        faculty.save()

                        # CORRECTED: Record the upload - removed format, bytes
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='photo',
                            cloudinary_url=cloudinary_response['secure_url'],
                            public_id=cloudinary_response['public_id'],
                            resource_type=cloudinary_response['resource_type'],
                            uploaded_by=request.user.username
                        )
                    except Exception as e:
                        logger.error(f"Error uploading photo to Cloudinary: {str(e)}")
                        messages.warning(request, f"Photo saved locally but Cloudinary upload failed: {str(e)}")

                # Log the action
                FacultyLog.objects.create(
                    faculty=faculty,
                    action='Faculty Added',
                    details=f'New faculty member added: {faculty.staff_name} ({faculty.employee_code})',
                    performed_by=request.user.username,
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                messages.success(request, f'Faculty {faculty.staff_name} added successfully!')
                return redirect('dashboard:faculty_dashboard') + f'?id={faculty.id}'
            except Exception as e:
                logger.error(f"Error adding faculty: {str(e)}")
                messages.error(request, f'Error saving faculty: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FacultyForm()

    context = {
        'form': form,
        'page_title': 'Add New Faculty',
        'active_page': 'add_faculty',
    }

    return render(request, 'dashboard/faculty_form.html', context)


@login_required
def edit_faculty(request, faculty_id):
    """
    Edit existing faculty member
    """
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES, instance=faculty)
        if form.is_valid():
            try:
                old_data = {
                    'name': faculty.staff_name,
                    'department': faculty.department,
                    'designation': faculty.designation,
                }

                faculty = form.save()

                # Handle photo upload if new photo provided
                if 'photo' in request.FILES:
                    photo_file = request.FILES['photo']
                    try:
                        cloudinary_response = cloudinary.uploader.upload(
                            photo_file,
                            folder="faculty_photos",
                            public_id=f"faculty_{faculty.employee_code}",
                            overwrite=True,
                            transformation=[
                                {'width': 300, 'height': 300, 'crop': 'fill'},
                                {'quality': 'auto:good'}
                            ]
                        )
                        faculty.cloudinary_photo_url = cloudinary_response['secure_url']
                        faculty.save()

                        # CORRECTED: Record the upload - removed format, bytes
                        CloudinaryUpload.objects.create(
                            faculty=faculty,
                            upload_type='photo',
                            cloudinary_url=cloudinary_response['secure_url'],
                            public_id=cloudinary_response['public_id'],
                            resource_type=cloudinary_response['resource_type'],
                            uploaded_by=request.user.username
                        )
                    except Exception as e:
                        logger.error(f"Error uploading photo to Cloudinary: {str(e)}")
                        messages.warning(request, f"Photo saved locally but Cloudinary upload failed: {str(e)}")

                # Log the action
                changes = []
                if old_data['name'] != faculty.staff_name:
                    changes.append(f"Name changed from {old_data['name']} to {faculty.staff_name}")
                if old_data['department'] != faculty.department:
                    changes.append(f"Department changed from {old_data['department']} to {faculty.department}")
                if old_data['designation'] != faculty.designation:
                    changes.append(f"Designation changed from {old_data['designation']} to {faculty.designation}")

                FacultyLog.objects.create(
                    faculty=faculty,
                    action='Faculty Edited',
                    details=f'Faculty updated: {faculty.employee_code}. Changes: {", ".join(changes) if changes else "None"}',
                    performed_by=request.user.username,
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                messages.success(request, f'Faculty {faculty.staff_name} updated successfully!')
                return redirect('dashboard:faculty_dashboard') + f'?id={faculty.id}'
            except Exception as e:
                logger.error(f"Error updating faculty: {str(e)}")
                messages.error(request, f'Error updating faculty: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FacultyForm(instance=faculty)

    context = {
        'form': form,
        'faculty': faculty,
        'page_title': f'Edit {faculty.staff_name}',
        'active_page': 'edit_faculty',
    }

    return render(request, 'dashboard/faculty_form.html', context)


@login_required
def delete_faculty(request, faculty_id):
    """
    Delete faculty member (AJAX supported)
    """
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        faculty_name = faculty.staff_name
        employee_code = faculty.employee_code

        # Log before deletion
        FacultyLog.objects.create(
            faculty=None,  # Will be deleted
            action='Faculty Deleted',
            details=f'Faculty deleted: {faculty_name} ({employee_code})',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        faculty.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Faculty {faculty_name} deleted successfully.'
            })

        messages.success(request, f'Faculty {faculty_name} deleted successfully.')
        return redirect('dashboard:faculty_list')

    context = {
        'faculty': faculty,
        'page_title': f'Delete {faculty.staff_name}',
    }

    return render(request, 'dashboard/confirm_delete.html', context)


@login_required
def assign_subjects(request, faculty_id):
    """
    Assign subjects to faculty member
    """
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        subject_ids = request.POST.getlist('subjects')
        old_subjects = set(faculty.subjects.values_list('id', flat=True))
        new_subjects = set(map(int, subject_ids))

        # Update subjects
        faculty.subjects.set(Subject.objects.filter(id__in=subject_ids))

        # Calculate changes
        added = new_subjects - old_subjects
        removed = old_subjects - new_subjects

        # Log the action
        changes = []
        if added:
            added_names = Subject.objects.filter(id__in=added).values_list('name', flat=True)
            changes.append(f"Added subjects: {', '.join(added_names)}")
        if removed:
            removed_names = Subject.objects.filter(id__in=removed).values_list('name', flat=True)
            changes.append(f"Removed subjects: {', '.join(removed_names)}")

        FacultyLog.objects.create(
            faculty=faculty,
            action='Subjects Assigned',
            details=f'Subjects updated for {faculty.staff_name}. {"; ".join(changes) if changes else "No changes"}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'Subjects assigned to {faculty.staff_name} successfully!')
        return redirect('dashboard:faculty_dashboard') + f'?id={faculty.id}'

    # Get available subjects
    available_subjects = Subject.objects.all()

    context = {
        'faculty': faculty,
        'available_subjects': available_subjects,
        'assigned_subjects': faculty.subjects.all(),
        'page_title': f'Assign Subjects to {faculty.staff_name}',
        'active_page': 'assign_subjects',
    }

    return render(request, 'dashboard/assign_subjects.html', context)


# ==================== STUDENT MANAGEMENT ====================

def students(request):
    """Student registration form - protected by student login"""
    # Check if student is logged in via session
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:student_login')

    if request.method == "POST":
        try:
            # Upload photo to Cloudinary if provided
            photo_url = None

            if "photo" in request.FILES:
                upload = cloudinary.uploader.upload(
                    request.FILES["photo"],
                    folder="students/photos",
                    resource_type="image",
                    transformation=[
                        {"width": 300, "height": 300, "crop": "fill"},
                        {"quality": "auto:good"},
                    ],
                )
                photo_url = upload.get("secure_url")

            # Parse date string (DD-MM-YYYY) to Date object
            dob_str = request.POST.get("dob")
            dob = None
            if dob_str:
                try:
                    if '-' in dob_str:
                        day, month, year = map(int, dob_str.split('-'))
                    elif '/' in dob_str:
                        day, month, year = map(int, dob_str.split('/'))
                    else:
                        # Assume YYYY-MM-DD format
                        year, month, day = map(int, dob_str.split('-'))
                    dob = date(year, month, day)
                except Exception as e:
                    logger.error(f"Error parsing date {dob_str}: {str(e)}")
                    dob = None

            # Calculate age if dob is provided
            age = None
            if dob:
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            # Create student record
            student_data = {
                "ht_no": request.POST.get("ht_no", "").strip().upper(),
                "student_name": request.POST.get("student_name", "").strip().title(),
                "father_name": request.POST.get("father_name", "").strip().title(),
                "mother_name": request.POST.get("mother_name", "").strip().title(),
                "gender": request.POST.get("gender"),
                "dob": dob,
                "age": age,
                "nationality": request.POST.get("nationality", "Indian"),
                "category": request.POST.get("category"),
                "religion": request.POST.get("religion"),
                "blood_group": request.POST.get("blood_group"),
                "aadhar": request.POST.get("aadhar"),
                "apaar_id": request.POST.get("apaar_id"),
                "address": request.POST.get("address"),
                "parent_phone": request.POST.get("parent_phone"),
                "student_phone": request.POST.get("student_phone"),
                "email": request.POST.get("email"),
                "admission_type": request.POST.get("admission_type"),
                "other_admission_details": request.POST.get("other_admission_details"),
                "eamcet_rank": request.POST.get("eamcet_rank") or None,
                "year": request.POST.get("year") or None,
                "sem": request.POST.get("sem") or None,
                "branch": request.POST.get("branch"),
                "roll_number": request.POST.get("roll_number"),
                "ssc_marks": request.POST.get("ssc_marks") or None,
                "inter_marks": request.POST.get("inter_marks") or None,
                "cgpa": request.POST.get("cgpa") or None,
                "csi_registered": bool(request.POST.get("csi_registered")),
                "csi_membership_id": request.POST.get("csi_membership_id"),
                "rtrp_project_title": request.POST.get("rtrp_project_title"),  # ✅ FIXED: rtrp_title → rtrp_project_title
                "intern_title": request.POST.get("intern_title"),
                "final_project_title": request.POST.get("final_project_title"),
                "other_training": request.POST.get("other_training"),
            }

            # If photo was uploaded to Cloudinary, save URL
            if photo_url:
                student_data["photo_url"] = photo_url

            # Handle certificate file uploads
            certificate_mapping = {
                'achievement_certificate': 'cert_achieve',
                'internship_certificate': 'cert_intern',
                'courses_certificate': 'cert_courses',
                'sdp_certificate': 'cert_sdp',
                'extra_certificate': 'cert_extra',
                'placement_offer': 'cert_placement',
                'national_exam_certificate': 'cert_national'
            }

            # Check if student already exists
            student, created = Student.objects.update_or_create(
                ht_no=request.POST["ht_no"],
                defaults=student_data
            )

            # Save certificate files
            for model_field, form_field in certificate_mapping.items():
                if form_field in request.FILES:
                    file_obj = request.FILES[form_field]
                    setattr(student, model_field, file_obj)

            student.save()

            messages.success(request,
                             f"Student {student.student_name} {'registered' if created else 'updated'} successfully!")
            return redirect("dashboard:students_data")

        except Exception as e:
            logger.error(f"Error in student registration: {str(e)}")
            messages.error(request, f"Error registering student: {str(e)}")

    return render(request, "dashboard/students.html", {
        'title': 'Student Registration',
        'today': date.today().strftime('%Y-%m-%d'),
    })


# =====================================================
# STUDENTS DATA DASHBOARD (MERGED VERSION)
# =====================================================
def students_data(request):
    """
    Display student data - protected by student login
    """
    # -------------------------------------------------
    # SESSION CHECK (Student Login)
    # -------------------------------------------------
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:student_login')

    # -------------------------------------------------
    # BASE QUERYSET
    # -------------------------------------------------
    students_list = Student.objects.all().order_by("-created_at")

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------
    search_query = request.GET.get('search', '').strip()
    if search_query:
        students_list = students_list.filter(
            Q(student_name__icontains=search_query) |
            Q(ht_no__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(father_name__icontains=search_query)
        )

    # -------------------------------------------------
    # FILTERS
    # -------------------------------------------------
    # Filter by Year
    year_filter = request.GET.get('year', '').strip()
    if year_filter:
        students_list = students_list.filter(year=year_filter)

    # Filter by Branch
    branch_filter = request.GET.get('branch', '').strip()
    if branch_filter:
        students_list = students_list.filter(branch__icontains=branch_filter)

    # Filter by Gender
    gender_filter = request.GET.get('gender', '').strip()
    if gender_filter:
        students_list = students_list.filter(gender=gender_filter)

    # -------------------------------------------------
    # PAGINATION
    # -------------------------------------------------
    page = request.GET.get('page', 1)
    paginator = Paginator(students_list, 25)

    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)

    # -------------------------------------------------
    # STATISTICS
    # -------------------------------------------------
    total_students = students_list.count()
    male_count = students_list.filter(gender="Male").count()
    female_count = students_list.filter(gender="Female").count()
    pdf_generated_count = students_list.exclude(
        pdf_url__isnull=True
    ).exclude(pdf_url="").count()

    # -------------------------------------------------
    # CONTEXT
    # -------------------------------------------------
    context = {
        "students": students,
        "total_students": total_students,
        "male_count": male_count,
        "female_count": female_count,
        "pdf_generated_count": pdf_generated_count,
        "single_pdf": False,  # Web view mode

        # Filters state
        "search_query": search_query,
        "year_filter": year_filter,
        "branch_filter": branch_filter,
        "gender_filter": gender_filter,

        # Dropdown data
        "years": Student.objects.values_list(
            'year', flat=True
        ).distinct().order_by('year'),

        "branches": Student.objects.values_list(
            'branch', flat=True
        ).distinct().order_by('branch'),

        "title": "Students Data",
    }

    return render(request, "dashboard/students_data.html", context)


# =====================================================
# ADD STUDENT (MERGED VERSION)
# =====================================================
def add_student(request):
    """
    Add new student (Session-based protection)
    """

    # ✅ Session authentication check
    if not request.session.get('student_logged_in'):
        messages.error(request, "Please login first.")
        return redirect('dashboard:student_login')

    if request.method == "POST":
        try:
            student = Student.objects.create(
                ht_no=request.POST.get("ht_no"),
                student_name=request.POST.get("student_name"),
                father_name=request.POST.get("father_name"),
                mother_name=request.POST.get("mother_name"),
                gender=request.POST.get("gender"),
                dob=request.POST.get("dob"),
                age=request.POST.get("age"),
                nationality=request.POST.get("nationality"),
                category=request.POST.get("category"),
                religion=request.POST.get("religion"),
                blood_group=request.POST.get("blood_group"),
                aadhar=request.POST.get("aadhar"),
                apaar_id=request.POST.get("apaar_id"),
                address=request.POST.get("address"),
                parent_phone=request.POST.get("parent_phone"),
                student_phone=request.POST.get("student_phone"),
                email=request.POST.get("email"),
                task_registered=request.POST.get("task_registered"),
                task_username=request.POST.get("task_username"),
                csi_registered=request.POST.get("csi_registered"),
                csi_membership_id=request.POST.get("csi_membership_id"),
                admission_type=request.POST.get("admission_type"),
                other_admission_details=request.POST.get("other_admission_details"),
                eamcet_rank=request.POST.get("eamcet_rank"),
                year=request.POST.get("year"),
                sem=request.POST.get("sem"),
                ssc_marks=request.POST.get("ssc_marks"),
                inter_marks=request.POST.get("inter_marks"),
                cgpa=request.POST.get("cgpa"),

                # ✅ Correct field name (NOT rtrp_title)
                rtrp_project_title=request.POST.get("rtrp_project_title"),  # ✅ FIXED

                intern_title=request.POST.get("intern_title"),
                final_project_title=request.POST.get("final_project_title"),
                other_training=request.POST.get("other_training"),

                photo=request.FILES.get("photo"),
            )

            # ✅ Optional Logging
            FacultyLog.objects.create(
                faculty=None,
                action="Student Added",
                details=f"Student added: {student.student_name} ({student.ht_no})",
                performed_by=request.session.get('student_username', 'Student'),
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, "Student added successfully.")
            return redirect("dashboard:students_data")

        except Exception as e:
            logger.error(f"Error adding student: {str(e)}")
            messages.error(request, f"Error adding student: {str(e)}")
            return redirect("dashboard:add_student")

    return render(request, "dashboard/add_student.html", {
        "title": "Add Student"
    })


# =====================================================
# EDIT STUDENT (MERGED VERSION)
# =====================================================
def delete_student(request, student_id):
    """
    Delete student (Session based protection)
    """

    # ✅ Session authentication check
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')

    student = get_object_or_404(Student, id=student_id)
    student_name = student.student_name
    ht_no = student.ht_no

    # Log before deletion
    FacultyLog.objects.create(
        faculty=None,
        action='Student Deleted',
        details=f'Student deleted: {student_name} ({ht_no})',
        performed_by=request.session.get('student_username', 'Student'),
        ip_address=request.META.get('REMOTE_ADDR')
    )

    student.delete()
    return redirect('dashboard:students_data')


# =====================================================
# DELETE STUDENT (MERGED VERSION)
# =====================================================
@require_POST
def delete_student(request, student_id):
    """
    Delete student (Session based protection)
    """

    # ✅ Session authentication check
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')

    student = get_object_or_404(Student, id=student_id)
    student_name = student.student_name
    ht_no = student.ht_no

    if request.method == 'POST':
        student.delete()

        messages.success(
            request,
            f"Student {student_name} ({ht_no}) deleted successfully."
        )

    return redirect('dashboard:students_data')


# =====================================================
# GENERATE STUDENT PDF (MERGED VERSION)
# =====================================================
@login_required
def generate_student_pdf(request, student_id):
    from django.utils import timezone
    from cloudinary.uploader import upload
    import os

    student = get_object_or_404(Student, id=student_id)

    try:
        # 1️⃣ Generate PDF locally
        pdf_path = generate_student_pdf_file(student)

        # 2️⃣ Upload to Cloudinary
        upload_result = upload(
            pdf_path,
            resource_type="raw",
            folder="student_pdfs",
            public_id=f"{student.ht_no}_pdf",
            overwrite=True
        )

        # 3️⃣ Save Cloudinary URL
        student.pdf_url = upload_result.get("secure_url")
        student.pdf_generated = True
        student.pdf_generation_time = timezone.now()
        student.save()

        # 4️⃣ Save Upload Record
        CloudinaryUpload.objects.create(
            student=student,
            upload_type="Student PDF",
            cloudinary_url=upload_result.get("secure_url"),
            public_id=upload_result.get("public_id"),
            resource_type="raw",
            uploaded_by=request.user.username,
        )

        # 5️⃣ Delete Local File
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        messages.success(request, "PDF generated and uploaded successfully.")
        return redirect("dashboard:students_data")

    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect("dashboard:students_data")



import tempfile
import os
import requests
from datetime import datetime
from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


def generate_student_pdf_file(student):

    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name

        # Proper A4 Margins
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()
        story = []

        # ===============================
        # STYLES
        # ===============================

        college_style = ParagraphStyle(
            'CollegeStyle',
            parent=styles['Normal'],
            fontSize=18,
            alignment=1,
            textColor=colors.darkgreen,
            spaceAfter=4
        )

        dept_style = ParagraphStyle(
            'DeptStyle',
            parent=styles['Normal'],
            fontSize=14,
            alignment=1,
            textColor=colors.darkblue,
            spaceAfter=6
        )

        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            spaceAfter=10
        )

        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
        )

        # ===============================
        # HEADER WITH PHOTO RIGHT
        # ===============================

        header_text = [
            Paragraph("<b>ANURAG ENGINEERING COLLEGE</b>", college_style),
            Paragraph("INFORMATION TECHNOLOGY DEPARTMENT", dept_style),
            Paragraph("<b>STUDENT REGISTRATION DETAILS</b>", section_style)
        ]

        photo = None

        if student.photo:
            try:
                photo = Image(student.photo.path, 1.3 * inch, 1.3 * inch)
            except:
                photo = None

        elif student.photo_url:
            try:
                response = requests.get(student.photo_url)
                img_temp = tempfile.NamedTemporaryFile(delete=False)
                img_temp.write(response.content)
                img_temp.close()
                photo = Image(img_temp.name, 1.3 * inch, 1.3 * inch)
            except:
                photo = None

        header_table = Table(
            [[header_text, photo if photo else ""]],
            colWidths=[4.8 * inch, 1.3 * inch]
        )

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        story.append(header_table)
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 15))

        # ===============================
        # BASIC DETAILS TABLE
        # ===============================

        student_data = [
            ["Hall Ticket Number", student.ht_no, "Student Name", student.student_name],
            ["Father Name", student.father_name or "N/A", "Mother Name", student.mother_name or "N/A"],
            ["Gender", student.gender or "N/A",
             "DOB", student.dob.strftime("%d-%m-%Y") if student.dob else "N/A"],
            ["Year", student.year or "N/A",
             "Semester", student.sem or "N/A"],
            ["Phone", student.student_phone or "N/A",
             "Email", student.email or "N/A"],
            ["CGPA", student.cgpa or "N/A",
             "Nationality", student.nationality or "Indian"],
        ]

        table = Table(student_data, colWidths=[1.4 * inch, 2 * inch, 1.4 * inch, 2 * inch])

        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(table)
        story.append(Spacer(1, 20))

        # ===============================
        # ACADEMIC PERFORMANCE
        # ===============================

        story.append(Paragraph("ACADEMIC PERFORMANCE", section_style))
        story.append(Spacer(1, 8))

        academic_data = [
            ["SSC Marks (%)", student.ssc_marks or "N/A"],
            ["Inter Marks (%)", student.inter_marks or "N/A"],
            ["RTRP Project", student.rtrp_project_title or "N/A"],
            ["Internship", student.intern_title or "N/A"],
            ["Final Project", student.final_project_title or "N/A"],
        ]

        academic_table = Table(academic_data, colWidths=[3 * inch, 3 * inch])

        academic_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        story.append(academic_table)
        story.append(Spacer(1, 20))

        # ===============================
        # CERTIFICATES & DOCUMENTS (FIXED)
        # ===============================

        # Mapping of certificate display names to model field names
        certificate_fields = [
            ('Achievement Certificate', 'cert_achieve'),
            ('Internship Certificate', 'cert_intern'),
            ('Courses Certificate', 'cert_courses'),
            ('SDP Certificate', 'cert_sdp'),
            ('Extra Certificate', 'cert_extra'),
            ('Placement Offer', 'cert_placement'),
            ('National Exam Certificate', 'cert_national'),
        ]

        # Collect certificates that actually have a file
        available_certs = []
        for display_name, field_name in certificate_fields:
            file_field = getattr(student, field_name, None)
            if file_field and hasattr(file_field, 'path') and os.path.exists(file_field.path):
                available_certs.append((display_name, file_field.path))
            elif file_field and hasattr(file_field, 'url') and file_field.url:
                # Optionally try to download from remote URL (Cloudinary)
                try:
                    response = requests.get(file_field.url, timeout=5)
                    if response.status_code == 200:
                        img_temp = tempfile.NamedTemporaryFile(delete=False)
                        img_temp.write(response.content)
                        img_temp.close()
                        available_certs.append((display_name, img_temp.name))
                except:
                    pass

        if available_certs:
            story.append(Paragraph("CERTIFICATES & DOCUMENTS", section_style))
            story.append(Spacer(1, 10))

            for display_name, file_path in available_certs:
                story.append(Paragraph(f"<b>{display_name}</b>", normal_style))
                story.append(Spacer(1, 5))

                # Determine file type by extension
                ext = Path(file_path).suffix.lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    try:
                        # Try to open as image
                        cert_img = Image(file_path, width=3.5*inch, height=3*inch, kind='proportional')
                        story.append(cert_img)
                        story.append(Spacer(1, 15))
                    except Exception as e:
                        story.append(Paragraph(f"Unable to load certificate image: {str(e)}", normal_style))
                        story.append(Spacer(1, 10))
                elif ext == '.pdf':
                    # ReportLab cannot embed PDF pages directly; show a placeholder
                    story.append(Paragraph("PDF Document (attached separately)", normal_style))
                    story.append(Spacer(1, 10))
                else:
                    story.append(Paragraph(f"File type: {ext} (available)", normal_style))
                    story.append(Spacer(1, 10))
        else:
            # No certificates found – optional note
            pass

        # ===============================
        # FOOTER
        # ===============================

        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 8))

        footer = Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}<br/>"
            "This is an official document of ANURAG Engineering College",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1
            )
        )

        story.append(footer)

        # Build PDF
        doc.build(story)

        return pdf_path

    except Exception as e:
        raise Exception(f"PDF Generation Failed: {str(e)}")

def generate_simple_student_pdf(student):
    """Fallback simple PDF generation"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf_path = tmp_file.name

    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Student Profile - {student.student_name}")

    # College Info
    c.setFont("Helvetica", 10)
    c.drawString(100, 730, "ANURAG ENGINEERING COLLEGE")
    c.drawString(100, 715, "An Autonomous Institution")

    # Student Info
    c.setFont("Helvetica", 11)
    y = 680
    line_height = 20

    info_lines = [
        f"HT No: {student.ht_no}",
        f"Student Name: {student.student_name}",
        f"Father's Name: {student.father_name or 'N/A'}",
        f"Mother's Name: {student.mother_name or 'N/A'}",
        f"Date of Birth: {student.dob.strftime('%d-%m-%Y') if student.dob else 'N/A'}",
        f"Gender: {student.gender}",
        f"Category: {student.category or 'N/A'}",
        f"Year: {student.year}, Semester: {student.sem}",
        f"Branch: {student.branch}",
        f"Roll Number: {student.roll_number}",
        f"Email: {student.email or 'N/A'}",
        f"Phone: {student.student_phone or 'N/A'}",
    ]

    for line in info_lines:
        c.drawString(100, y, line)
        y -= line_height

    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(100, 100, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    c.drawString(100, 85, f"Document ID: STUD-{student.ht_no}")

    c.save()
    return pdf_path


# =====================================================
# VIEW PDF (MERGED VERSION)
# =====================================================
def view_pdf(request, student_id):
    """View student PDF"""
    student = get_object_or_404(Student, id=student_id)
    if not student.pdf_url:
        messages.error(request, "PDF not generated yet.")
        return redirect("dashboard:students_data")
    return redirect(student.pdf_url)


# =====================================================
# DOWNLOAD PDF (MERGED VERSION)
# =====================================================
def download_pdf(request, student_id):
    """Download student PDF"""
    student = get_object_or_404(Student, id=student_id)

    if not student.pdf_url:
        messages.error(request, "PDF not generated yet.")
        return redirect("dashboard:students_data")

    return redirect(student.pdf_url)




def edit_student(request, student_id):
    """
    Edit student (Session based protection)
    """

    # ✅ Session authentication check
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')

    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('dashboard:students_data')
    else:
        form = StudentForm(instance=student)

    return render(request, 'dashboard/add_student.html', {
        'form': form,
        'title': 'Edit Student'
    })


@login_required
def export_students_csv(request):
    """Export students data to CSV"""
    students = Student.objects.all().order_by('ht_no')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_export_{date.today().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)

    # Write header
    writer.writerow([
        'HT No', 'Student Name', 'Father Name', 'Mother Name',
        'Gender', 'Date of Birth', 'Age', 'Category', 'Religion',
        'Blood Group', 'Aadhar', 'APAAR ID', 'Address',
        'Parent Phone', 'Student Phone', 'Email',
        'Year', 'Semester', 'Branch', 'Roll Number',
        'SSC Marks', 'Inter Marks', 'CGPA',
        'Admission Type', 'EAMCET Rank',
        'RTRP Project Title', 'Internship Title', 'Final Project Title',  # ✅ FIXED: RTRP Title → RTRP Project Title
        'Created Date'
    ])

    # Write data
    for student in students:
        writer.writerow([
            student.ht_no,
            student.student_name,
            student.father_name,
            student.mother_name,
            student.gender,
            student.dob.strftime('%d-%m-%Y') if student.dob else '',
            student.age,
            student.category,
            student.religion or '',
            student.blood_group or '',
            student.aadhar or '',
            student.apaar_id or '',
            student.address,
            student.parent_phone,
            student.student_phone,
            student.email,
            student.year,
            student.sem,
            student.branch or '',
            student.roll_number or '',
            student.ssc_marks,
            student.inter_marks,
            student.cgpa,
            student.admission_type or '',
            student.eamcet_rank or '',
            student.rtrp_project_title or '',  # ✅ FIXED: rtrp_title → rtrp_project_title
            student.intern_title or '',
            student.final_project_title or '',
            student.created_at.strftime('%d-%m-%Y %H:%M:%S') if student.created_at else '',
        ])

    # Log the action
    FacultyLog.objects.create(
        faculty=None,
        action='Students CSV Export',
        details=f'Exported {students.count()} students to CSV',
        performed_by=request.user.username,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return response


# ==================== PDF GENERATION ====================

@login_required
def generate_faculty_pdf(request, faculty_id):
    """Generate PDF for a faculty member using merged template"""
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)

        # Calculate experience
        experience = calculate_experience(faculty.joining_date) if faculty.joining_date else "N/A"

        # Prepare context
        context = {
            'faculty': faculty,
            'experience': experience,
            'current_date': date.today(),
            'pdf_mode': True,  # This triggers PDF mode in template
        }

        # Render HTML template
        html_string = render_to_string('dashboard/faculty.html', context)

        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
            'enable-local-file-access': '',
        }

        # Configure wkhtmltopdf path
        config = pdfkit.configuration()
        if hasattr(settings, 'WKHTMLTOPDF_PATH'):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

        # Generate PDF
        pdf = pdfkit.from_string(html_string, False, options=options, configuration=config)

        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="faculty_{faculty.employee_code}_{date.today().strftime("%Y%m%d")}.pdf"'

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
        return redirect('dashboard:faculty_dashboard')


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
def bulk_generate_faculty_pdfs(request):
    """Generate PDFs for multiple faculty members"""
    if request.method == 'POST':
        faculty_ids = request.POST.getlist('faculty_ids')
        if not faculty_ids:
            messages.error(request, "No faculty selected.")
            return redirect('dashboard:faculty_list')

        try:
            # Create temporary directory for PDFs
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, f'faculty_pdfs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for faculty_id in faculty_ids:
                    try:
                        faculty = Faculty.objects.get(id=faculty_id)

                        # Generate PDF
                        experience = calculate_experience(faculty.joining_date) if faculty.joining_date else "N/A"

                        context = {
                            'faculty': faculty,
                            'experience': experience,
                            'current_date': date.today(),
                            'pdf_mode': True,
                        }

                        html_string = render_to_string('dashboard/faculty.html', context)

                        options = {
                            'page-size': 'A4',
                            'margin-top': '20mm',
                            'margin-right': '20mm',
                            'margin-bottom': '20mm',
                            'margin-left': '20mm',
                            'encoding': "UTF-8",
                        }

                        config = pdfkit.configuration()
                        if hasattr(settings, 'WKHTMLTOPDF_PATH'):
                            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

                        pdf = pdfkit.from_string(html_string, False, options=options, configuration=config)

                        # Save PDF to temp file
                        pdf_filename = f"faculty_{faculty.employee_code}.pdf"
                        pdf_path = os.path.join(temp_dir, pdf_filename)

                        with open(pdf_path, 'wb') as f:
                            f.write(pdf)

                        # Add to zip
                        zipf.write(pdf_path, pdf_filename)

                        # Clean up individual PDF
                        os.remove(pdf_path)

                    except Exception as e:
                        logger.error(f"Error generating PDF for faculty {faculty_id}: {str(e)}")
                        continue

            # Read zip file
            with open(zip_path, 'rb') as f:
                zip_data = f.read()

            # Create response
            response = HttpResponse(zip_data, content_type='application/zip')
            response[
                'Content-Disposition'] = f'attachment; filename="faculty_pdfs_{datetime.now().strftime("%Y%m%d")}.zip"'

            # Clean up
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

            # Log the action
            FacultyLog.objects.create(
                faculty=None,
                action='Bulk Faculty PDFs Generated',
                details=f'PDFs generated for {len(faculty_ids)} faculty members',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return response

        except Exception as e:
            logger.error(f"Error in bulk PDF generation: {str(e)}")
            messages.error(request, f"Error generating PDFs: {str(e)}")

    return redirect('dashboard:faculty_list')


# ==================== CLOUDINARY INTEGRATION ====================

@login_required
@csrf_exempt
def upload_faculty_to_cloudinary(request, faculty_id):
    """Upload faculty PDF to Cloudinary"""
    if request.method == 'POST':
        try:
            faculty = get_object_or_404(Faculty, id=faculty_id)

            # First, check if PDF already exists
            if faculty.cloudinary_pdf_url:
                return JsonResponse({
                    'success': True,
                    'pdf_url': faculty.cloudinary_pdf_url,
                    'message': 'PDF already exists on Cloudinary'
                })

            # Generate PDF
            pdf_response = generate_faculty_pdf(request, faculty_id)

            if not isinstance(pdf_response, HttpResponse):
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate PDF'
                })

            # Get PDF content
            pdf_content = pdf_response.content

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name

            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                tmp_file_path,
                resource_type="raw",
                folder="faculty_pdfs",
                public_id=f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}",
                overwrite=True,
                tags=[f"faculty_{faculty.employee_code}", faculty.department, "pdf"]
            )

            # Save Cloudinary URL to faculty record
            faculty.cloudinary_pdf_url = cloudinary_response['secure_url']
            faculty.save()

            # CORRECTED: Record the upload - removed format, bytes, raw_response
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='pdf',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
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

            # CORRECTED: Record the upload - removed format, bytes, raw_response
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='photo',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )

            return JsonResponse({
                'success': True,
                'photo_url': faculty.cloudinary_photo_url,
                'message': 'Photo uploaded successfully'
            })

        except Exception as e:
            logger.error(f"Error uploading photo: {str(e)}")
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

            # CORRECTED: Record the upload - removed format, bytes, raw_response
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='pdf',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )

            return JsonResponse({
                'success': True,
                'pdf_url': faculty.cloudinary_pdf_url,
                'message': 'PDF uploaded to Cloudinary successfully'
            })

        except Exception as e:
            logger.error(f"Error uploading PDF: {str(e)}")
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

        # Get recent uploads
        recent_uploads = CloudinaryUpload.objects.select_related('faculty', 'student').order_by('-upload_date')[:10]

        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status',
            'connected': status,
            'usage': usage,
            'uploaded_count': uploaded_count,
            'faculty_with_pdf': faculty_with_pdf,
            'faculty_with_photo': faculty_with_photo,
            'total_faculty': Faculty.objects.count(),
            'recent_uploads': recent_uploads,
            'cloudinary_config': {
                'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
            }
        })

    except Exception as e:
        logger.error(f"Cloudinary connection error: {str(e)}")
        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status',
            'connected': False,
            'error': str(e),
            'cloudinary_config': {
                'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
            }
        })


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


@login_required
def bulk_sync_to_cloudinary(request):
    """Bulk sync faculty data to Cloudinary"""
    if request.method == 'POST':
        faculty_ids = request.POST.getlist('faculty_ids')
        if not faculty_ids:
            messages.error(request, "No faculty selected.")
            return redirect('dashboard:faculty_list')

        success_count = 0
        error_count = 0

        for faculty_id in faculty_ids:
            try:
                faculty = Faculty.objects.get(id=faculty_id)

                # Sync PDF if not exists
                if not faculty.cloudinary_pdf_url:
                    try:
                        # Generate and upload PDF
                        pdf_response = generate_faculty_pdf(request, faculty_id)

                        if isinstance(pdf_response, HttpResponse):
                            pdf_content = pdf_response.content

                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                                tmp_file.write(pdf_content)
                                tmp_file_path = tmp_file.name

                            cloudinary_response = cloudinary.uploader.upload(
                                tmp_file_path,
                                resource_type="raw",
                                folder="faculty_pdfs",
                                public_id=f"faculty_{faculty.employee_code}",
                                overwrite=True
                            )

                            faculty.cloudinary_pdf_url = cloudinary_response['secure_url']
                            faculty.save()

                            # CORRECTED: Record the upload - removed format, bytes
                            CloudinaryUpload.objects.create(
                                faculty=faculty,
                                upload_type='pdf',
                                cloudinary_url=cloudinary_response['secure_url'],
                                public_id=cloudinary_response['public_id'],
                                resource_type=cloudinary_response['resource_type'],
                                uploaded_by=request.user.username
                            )

                            os.unlink(tmp_file_path)
                    except Exception as e:
                        logger.error(f"Error syncing PDF for faculty {faculty_id}: {str(e)}")

                # Sync photo if exists locally but not on Cloudinary
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

                            # CORRECTED: Record the upload - removed format, bytes
                            CloudinaryUpload.objects.create(
                                faculty=faculty,
                                upload_type='photo',
                                cloudinary_url=cloudinary_response['secure_url'],
                                public_id=cloudinary_response['public_id'],
                                resource_type=cloudinary_response['resource_type'],
                                uploaded_by=request.user.username
                            )
                    except Exception as e:
                        logger.error(f"Error syncing photo for faculty {faculty_id}: {str(e)}")

                success_count += 1

            except Exception as e:
                logger.error(f"Error syncing faculty {faculty_id}: {str(e)}")
                error_count += 1

        # Log the action
        FacultyLog.objects.create(
            faculty=None,
            action='Bulk Cloudinary Sync',
            details=f'Synced {success_count} faculty to Cloudinary ({error_count} errors)',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        if success_count > 0:
            messages.success(request, f"Successfully synced {success_count} faculty to Cloudinary.")
        if error_count > 0:
            messages.warning(request, f"Failed to sync {error_count} faculty.")

    return redirect('dashboard:faculty_list')


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

                    # CORRECTED: Record the upload - removed format, bytes, raw_response
                    CloudinaryUpload.objects.create(
                        faculty=faculty,
                        upload_type='certificate',
                        cloudinary_url=cloudinary_response['secure_url'],
                        public_id=cloudinary_response['public_id'],
                        resource_type=cloudinary_response['resource_type'],
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

            return redirect('dashboard:view_certificates', faculty_id=faculty_id)
    else:
        form = CertificateForm()

    return render(request, 'certificates/upload.html', {
        'title': f'Upload Certificate - {faculty.staff_name}',
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
        failed_count = 0

        for cert_file in files:
            try:
                # Extract certificate type from filename
                filename = os.path.splitext(cert_file.name)[0]
                cert_type = filename.replace('_', ' ').replace('-', ' ').title()

                # If certificate type is too generic, use a default
                if len(cert_type) < 3:
                    cert_type = "Certificate"

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
                failed_count += 1

        # Log the action
        FacultyLog.objects.create(
            faculty=faculty,
            action='Bulk Certificates Uploaded',
            details=f'{uploaded_count} certificates uploaded in bulk ({failed_count} failed)',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        if uploaded_count > 0:
            messages.success(request, f'{uploaded_count} certificates uploaded successfully!')
        if failed_count > 0:
            messages.warning(request, f'{failed_count} certificates failed to upload.')

        return redirect('dashboard:view_certificates', faculty_id=faculty.id)

    return render(request, 'certificates/bulk_upload.html', {
        'title': 'Bulk Upload Certificates'
    })


@login_required
def view_certificates(request, faculty_id):
    """View all certificates for a faculty"""
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certificates = Certificate.objects.filter(faculty=faculty).order_by('-issue_date')

    # Get certificate statistics
    cert_stats = {
        'total': certificates.count(),
        'by_type': certificates.values('certificate_type').annotate(count=Count('id')).order_by('-count'),
        'has_cloudinary': certificates.exclude(cloudinary_url__isnull=True).exclude(cloudinary_url='').count(),
    }

    return render(request, 'certificates/list.html', {
        'title': f'Certificates - {faculty.staff_name}',
        'faculty': faculty,
        'certificates': certificates,
        'cert_stats': cert_stats
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
                # Extract public_id from URL
                parts = certificate.cloudinary_url.split('/')
                public_id = parts[-1].split('.')[0]
                cloudinary.uploader.destroy(public_id, resource_type="raw")
            except Exception as e:
                logger.error(f"Error deleting from Cloudinary: {str(e)}")

        certificate_type = certificate.certificate_type
        certificate.delete()

        messages.success(request, 'Certificate deleted successfully!')

        # Log the action
        FacultyLog.objects.create(
            faculty=certificate.faculty,
            action='Certificate Deleted',
            details=f'Certificate deleted: {certificate_type}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return redirect('dashboard:view_certificates', faculty_id=faculty_id)

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
            old_type = certificate.certificate_type
            form.save()

            # Log the action
            FacultyLog.objects.create(
                faculty=certificate.faculty,
                action='Certificate Edited',
                details=f'Certificate edited: {old_type} -> {certificate.certificate_type}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, 'Certificate updated successfully!')
            return redirect('dashboard:view_certificates', faculty_id=certificate.faculty.id)
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
        return redirect('dashboard:view_certificates', faculty_id=faculty_id)

    try:
        merger = PdfMerger()

        # Add faculty PDF if exists
        if faculty.cloudinary_pdf_url:
            # Download from Cloudinary
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
                if os.path.exists(certificate.certificate_file.path):
                    merger.append(certificate.certificate_file.path)
            elif certificate.cloudinary_url:
                # Cloudinary URL
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

            # CORRECTED: Record the upload - removed format, bytes, raw_response
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='merged_certificates',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                uploaded_by=request.user.username
            )

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

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'merged_url': merged_url,
                'message': f'{certificates.count()} certificates merged successfully'
            })

        messages.success(request, f'{certificates.count()} certificates merged successfully!')
        return redirect(merged_url)

    except Exception as e:
        logger.error(f"Error merging certificates: {str(e)}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

        messages.error(request, f'Error merging certificates: {str(e)}')
        return redirect('dashboard:view_certificates', faculty_id=faculty_id)


@login_required
def merge_certificates_with_pdf(request, faculty_id):
    """Merge certificates with faculty PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        # Generate faculty PDF bytes
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate faculty PDF'
            })

        # Get certificates
        certificates = Certificate.objects.filter(faculty=faculty)

        # Merge certificates with PDF bytes
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

            # CORRECTED: Record the upload - removed format, bytes, raw_response
            CloudinaryUpload.objects.create(
                faculty=faculty,
                upload_type='merged_faculty_certs',
                cloudinary_url=cloudinary_response['secure_url'],
                public_id=cloudinary_response['public_id'],
                resource_type=cloudinary_response['resource_type'],
                uploaded_by=request.user.username
            )

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Certificates Merged with PDF',
                details=f'Certificates merged with faculty PDF: {certificates.count()} certificates',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'merged_url': cloudinary_response['secure_url'],
                    'message': f'PDF merged with {certificates.count()} certificates'
                })

            return redirect(cloudinary_response['secure_url'])
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


def generate_faculty_pdf_bytes(faculty):
    """Generate PDF bytes for a faculty member"""
    try:
        # Calculate experience
        experience = calculate_experience(faculty.joining_date) if faculty.joining_date else "N/A"

        # Prepare context
        context = {
            'faculty': faculty,
            'experience': experience,
            'current_date': date.today(),
            'pdf_mode': True,
        }

        # Render HTML template
        html_string = render_to_string('dashboard/faculty.html', context)

        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
            'enable-local-file-access': '',
        }

        # Generate PDF
        config = pdfkit.configuration()
        if hasattr(settings, 'WKHTMLTOPDF_PATH'):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

        pdf_bytes = pdfkit.from_string(html_string, False, options=options, configuration=config)
        return pdf_bytes

    except Exception as e:
        logger.error(f"Error generating PDF bytes: {str(e)}")
        return None


def merge_certificates_with_pdf_bytes(pdf_bytes, faculty):
    """Merge certificates with faculty PDF bytes"""
    try:
        merger = PdfMerger()

        # Add faculty PDF
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_faculty:
                tmp_faculty.write(pdf_bytes)
                tmp_faculty_path = tmp_faculty.name

            merger.append(tmp_faculty_path)

        # Add certificates
        certificates = Certificate.objects.filter(faculty=faculty)
        for certificate in certificates:
            if certificate.certificate_file and os.path.exists(certificate.certificate_file.path):
                # Local file
                merger.append(certificate.certificate_file.path)
            elif certificate.cloudinary_url:
                # Download from Cloudinary
                response = requests.get(certificate.cloudinary_url)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_cert:
                        tmp_cert.write(response.content)
                        tmp_cert_path = tmp_cert.name

                    merger.append(tmp_cert_path)
                    os.unlink(tmp_cert_path)

        # Create merged PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as merged_file:
            merger.write(merged_file.name)

            # Read merged PDF
            with open(merged_file.name, 'rb') as f:
                merged_bytes = f.read()

            # Clean up
            os.unlink(merged_file.name)

        # Clean up faculty temp file
        if pdf_bytes and 'tmp_faculty_path' in locals():
            os.unlink(tmp_faculty_path)

        merger.close()

        return merged_bytes

    except Exception as e:
        logger.error(f"Error merging certificates with PDF: {str(e)}")
        return None


@login_required
def preview_merged_pdf(request, faculty_id):
    """Preview merged PDF"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Check for existing merged PDF
    recent_upload = CloudinaryUpload.objects.filter(
        faculty=faculty,
        upload_type__in=['merged', 'merged_certificates', 'merged_faculty_certs'],
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


# ==================== FACULTY STATISTICS & APIS ====================

@login_required
def faculty_statistics_api(request, faculty_id):
    """
    API endpoint for faculty statistics (AJAX)
    """
    faculty = get_object_or_404(Faculty, id=faculty_id)

    # Calculate statistics
    total_subjects = faculty.subjects.count()
    total_students = 0  # You would need to calculate this based on your models
    avg_rating = 4.5  # You would calculate this from feedback

    # Mock data for demonstration
    statistics = {
        'total_subjects': total_subjects,
        'total_students': total_students,
        'avg_rating': avg_rating,
        'teaching_load': 75,
        'research_output': 60,
        'attendance_rate': 95,
        'publications': 12,
        'conferences': 5,
        'projects': 3,
        'awards': 2,
    }

    return JsonResponse(statistics)


@login_required
def bulk_faculty_actions(request):
    """Handle bulk actions for faculty"""
    if request.method == 'POST':
        action = request.POST.get('bulk_action')
        faculty_ids = request.POST.getlist('faculty_ids')

        if not faculty_ids:
            messages.error(request, 'No faculty members selected.')
            return redirect('dashboard:faculty_list')

        if action == 'delete':
            # Delete selected faculty
            deleted_count = 0
            for faculty_id in faculty_ids:
                try:
                    faculty = Faculty.objects.get(id=faculty_id)
                    faculty.delete()
                    deleted_count += 1
                except Faculty.DoesNotExist:
                    continue

            # Log the action
            FacultyLog.objects.create(
                faculty=None,
                action='Bulk Faculty Delete',
                details=f'{deleted_count} faculty members deleted in bulk',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f'Successfully deleted {deleted_count} faculty member(s).')

        elif action == 'activate':
            # Activate selected faculty
            updated_count = Faculty.objects.filter(id__in=faculty_ids).update(is_active=True)

            # Log the action
            FacultyLog.objects.create(
                faculty=None,
                action='Bulk Faculty Activate',
                details=f'{updated_count} faculty members activated',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f'Successfully activated {updated_count} faculty member(s).')

        elif action == 'deactivate':
            # Deactivate selected faculty
            updated_count = Faculty.objects.filter(id__in=faculty_ids).update(is_active=False)

            # Log the action
            FacultyLog.objects.create(
                faculty=None,
                action='Bulk Faculty Deactivate',
                details=f'{updated_count} faculty members deactivated',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f'Successfully deactivated {updated_count} faculty member(s).')

        elif action == 'export_csv':
            # Export selected faculty to CSV
            return export_faculty_csv(request, faculty_ids)

        elif action == 'generate_pdfs':
            # Generate PDFs for selected faculty
            return bulk_generate_faculty_pdfs(request)

        elif action == 'sync_cloudinary':
            # Sync selected faculty to Cloudinary
            return bulk_sync_to_cloudinary(request)

        else:
            messages.error(request, 'Invalid bulk action selected.')

    return redirect('dashboard:faculty_list')


@login_required
def export_faculty_csv(request, faculty_ids=None):
    """Export faculty data to CSV"""
    # If no specific IDs provided, export all
    if faculty_ids:
        faculties = Faculty.objects.filter(id__in=faculty_ids)
    else:
        faculties = Faculty.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="faculty_export_{date.today().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)

    # Write header
    writer.writerow([
        'Employee Code', 'Staff Name', 'Department', 'Designation',
        'Email', 'Phone', 'Date of Birth', 'Joining Date',
        'UG Degree', 'UG Year', 'PG Degree', 'PG Year',
        'PhD Status', 'Total Experience', 'Current Status',
        'Cloudinary PDF URL', 'Cloudinary Photo URL'
    ])

    # Write data
    for faculty in faculties:
        writer.writerow([
            faculty.employee_code,
            faculty.staff_name,
            faculty.department,
            faculty.designation,
            faculty.email,
            faculty.phone,
            faculty.dob.strftime('%Y-%m-%d') if faculty.dob else '',
            faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else '',
            faculty.ug_degree,
            faculty.ug_year,
            faculty.pg_degree,
            faculty.pg_year,
            faculty.phd_degree,
            calculate_experience(faculty.joining_date) if faculty.joining_date else 'N/A',
            'Active' if faculty.is_active else 'Inactive',
            faculty.cloudinary_pdf_url or '',
            faculty.cloudinary_photo_url or ''
        ])

    # Log the action
    FacultyLog.objects.create(
        faculty=None,
        action='Faculty CSV Export',
        details=f'Exported {faculties.count()} faculty to CSV',
        performed_by=request.user.username,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return response


# ==================== BULK UPLOAD ====================

@login_required
def bulk_upload(request):
    """Handle bulk upload of faculty data via Excel/CSV"""
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Read the uploaded file
                uploaded_file = request.FILES['file']

                # Check file extension
                file_name = uploaded_file.name.lower()

                if file_name.endswith('.csv'):
                    # Process CSV
                    if pd is None:
                        messages.error(request,
                                       'Pandas library is not installed. Please install pandas for CSV processing.')
                        return redirect('dashboard:bulk_upload')

                    df = pd.read_csv(uploaded_file)
                    success_count, error_count = process_csv_faculty_data(df, request.user)

                elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                    # Process Excel
                    if pd is None:
                        messages.error(request,
                                       'Pandas library is not installed. Please install pandas for Excel processing.')
                        return redirect('dashboard:bulk_upload')

                    df = pd.read_excel(uploaded_file)
                    success_count, error_count = process_csv_faculty_data(df, request.user)

                else:
                    messages.error(request, 'Unsupported file format. Please upload CSV or Excel files.')
                    return redirect('dashboard:bulk_upload')

                # Show results
                if success_count > 0:
                    messages.success(request, f'Successfully imported {success_count} faculty records.')
                if error_count > 0:
                    messages.warning(request, f'{error_count} records had errors and were not imported.')

                # Log the action
                FacultyLog.objects.create(
                    faculty=None,
                    action='Bulk Faculty Upload',
                    details=f'Bulk upload: {success_count} successful, {error_count} failed',
                    performed_by=request.user.username,
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                return redirect('dashboard:faculty_list')

            except Exception as e:
                logger.error(f"Error in bulk upload: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
                return redirect('dashboard:bulk_upload')
    else:
        form = BulkUploadForm()

    return render(request, 'dashboard/bulk_upload.html', {
        'form': form,
        'title': 'Bulk Faculty Upload',
        'has_pandas': pd is not None
    })


def process_csv_faculty_data(df, user):
    """Process faculty data from DataFrame"""
    success_count = 0
    error_count = 0

    # Required columns
    required_columns = ['employee_code', 'staff_name', 'department', 'designation']

    # Check if required columns exist
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in file.")

    for index, row in df.iterrows():
        try:
            # Check if faculty already exists
            employee_code = str(row['employee_code']).strip()
            faculty = Faculty.objects.filter(employee_code=employee_code).first()

            if faculty:
                # Update existing faculty
                for field in df.columns:
                    if hasattr(faculty, field) and not pd.isna(row[field]):
                        # Handle date fields
                        if field in ['dob', 'joining_date']:
                            try:
                                date_val = pd.to_datetime(row[field]).date()
                                setattr(faculty, field, date_val)
                            except:
                                pass
                        else:
                            setattr(faculty, field, row[field])
                faculty.save()
                action = 'updated'
            else:
                # Create new faculty
                faculty_data = {}
                for field in df.columns:
                    if hasattr(Faculty, field) and not pd.isna(row[field]):
                        # Handle date fields
                        if field in ['dob', 'joining_date']:
                            try:
                                faculty_data[field] = pd.to_datetime(row[field]).date()
                            except:
                                faculty_data[field] = None
                        else:
                            faculty_data[field] = row[field]

                faculty = Faculty.objects.create(**faculty_data)
                action = 'created'

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action=f'Bulk Upload - {action}',
                details=f'Faculty {action} via bulk upload: {faculty.employee_code}',
                performed_by=user.username if user else 'System',
                ip_address='127.0.0.1'  # Bulk upload doesn't have request context
            )

            success_count += 1

        except Exception as e:
            logger.error(f"Error processing row {index}: {str(e)}")
            error_count += 1
            continue

    return success_count, error_count


# ==================== SYSTEM UTILITIES ====================

@login_required
def system_status(request):
    """Display system status and statistics"""
    # Get system statistics
    stats = {
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'cloudinary_uploads': CloudinaryUpload.objects.count(),
        'total_logs': FacultyLog.objects.count(),
        'recent_logs': FacultyLog.objects.order_by('-created_at')[:10],
    }

    # Get system info if psutil is available
    system_info = {}
    if psutil:
        try:
            system_info = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'python_version': os.sys.version,
                'django_version': django.get_version(),
            }
        except:
            system_info = {'error': 'Unable to retrieve system information'}

    # Get database statistics
    db_stats = {
        'faculty_table': Faculty.objects.count(),
        'student_table': Student.objects.count(),
        'certificate_table': Certificate.objects.count(),
        'log_table': FacultyLog.objects.count(),
        'cloudinary_table': CloudinaryUpload.objects.count(),
    }

    # Check Cloudinary connection
    cloudinary_status = {'connected': False, 'error': ''}
    try:
        result = cloudinary.api.ping()
        cloudinary_status['connected'] = result.get('status') == 'ok'
    except Exception as e:
        cloudinary_status['error'] = str(e)

    return render(request, 'dashboard/system_status.html', {
        'title': 'System Status',
        'stats': stats,
        'system_info': system_info,
        'db_stats': db_stats,
        'cloudinary_status': cloudinary_status,
        'has_psutil': psutil is not None,
        'has_pandas': pd is not None,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })


@login_required
def clear_logs(request):
    """Clear system logs (with confirmation)"""
    if request.method == 'POST':
        try:
            days_old = int(request.POST.get('days', 30))
            cutoff_date = timezone.now() - timedelta(days=days_old)

            deleted_count, _ = FacultyLog.objects.filter(created_at__lt=cutoff_date).delete()

            # Log the action
            FacultyLog.objects.create(
                faculty=None,
                action='Logs Cleared',
                details=f'Cleared {deleted_count} logs older than {days_old} days',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f'Successfully deleted {deleted_count} logs older than {days_old} days.')
            return redirect('dashboard:system_status')
        except Exception as e:
            messages.error(request, f'Error clearing logs: {str(e)}')
            return redirect('dashboard:system_status')

    return render(request, 'dashboard/clear_logs.html', {
        'title': 'Clear System Logs'
    })


@login_required
def backup_database(request):
    """Create database backup"""
    try:
        import subprocess
        from django.conf import settings

        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.json')

        # Use Django's dumpdata command
        from django.core.management import call_command

        with open(backup_file, 'w') as f:
            call_command('dumpdata', stdout=f)

        # Log the action
        FacultyLog.objects.create(
            faculty=None,
            action='Database Backup',
            details=f'Database backup created: {backup_file}',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'Database backup created successfully: {os.path.basename(backup_file)}')

    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        messages.error(request, f'Error creating backup: {str(e)}')

    return redirect('dashboard:system_status')


# ==================== API ENDPOINTS ====================

@login_required
@require_GET
def api_faculty_list(request):
    """API endpoint for faculty list (JSON)"""
    faculties = Faculty.objects.all().values(
        'id', 'employee_code', 'staff_name', 'department',
        'designation', 'email', 'phone', 'is_active',
        'cloudinary_pdf_url', 'cloudinary_photo_url'
    )
    return JsonResponse(list(faculties), safe=False)


@login_required
@require_GET
def api_faculty_detail(request, faculty_id):
    """API endpoint for faculty details"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    data = {
        'id': faculty.id,
        'employee_code': faculty.employee_code,
        'staff_name': faculty.staff_name,
        'department': faculty.department,
        'designation': faculty.designation,
        'email': faculty.email,
        'phone': faculty.phone,
        'dob': faculty.dob.strftime('%Y-%m-%d') if faculty.dob else None,
        'joining_date': faculty.joining_date.strftime('%Y-%m-%d') if faculty.joining_date else None,
        'ug_degree': faculty.ug_degree,
        'ug_year': faculty.ug_year,
        'pg_degree': faculty.pg_degree,
        'pg_year': faculty.pg_year,
        'phd_degree': faculty.phd_degree,
        'is_active': faculty.is_active,
        'experience': calculate_experience(faculty.joining_date) if faculty.joining_date else "N/A",
        'cloudinary_pdf_url': faculty.cloudinary_pdf_url,
        'cloudinary_photo_url': faculty.cloudinary_photo_url,
        'created_at': faculty.created_at.strftime('%Y-%m-%d %H:%M:%S') if faculty.created_at else None,
        'updated_at': faculty.updated_at.strftime('%Y-%m-%d %H:%M:%S') if faculty.updated_at else None,
    }

    return JsonResponse(data)


@login_required
@require_POST
def api_update_faculty_status(request, faculty_id):
    """API endpoint to update faculty status"""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    try:
        data = json.loads(request.body)
        new_status = data.get('is_active')

        if new_status is not None:
            old_status = faculty.is_active
            faculty.is_active = bool(new_status)
            faculty.save()

            # Log the action
            FacultyLog.objects.create(
                faculty=faculty,
                action='Status Updated via API',
                details=f'Status changed from {"Active" if old_status else "Inactive"} to {"Active" if faculty.is_active else "Inactive"}',
                performed_by=request.user.username,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return JsonResponse({
                'success': True,
                'message': f'Status updated successfully',
                'is_active': faculty.is_active
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Missing is_active parameter'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_student_list(request):
    """API endpoint for student list (JSON)"""
    # Check authentication
    if not (request.user.is_authenticated or request.session.get('student_logged_in')):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    students = Student.objects.all().values(
        'id', 'ht_no', 'student_name', 'father_name', 'mother_name',
        'gender', 'dob', 'age', 'category', 'year', 'sem', 'branch', 'roll_number',
        'email', 'student_phone', 'parent_phone',
        'ssc_marks', 'inter_marks', 'cgpa',
        'photo_url', 'pdf_url', 'pdf_generated', 'created_at'
    )

    return JsonResponse(list(students), safe=False)


@require_GET
def api_student_detail(request, student_id):
    """API endpoint for student details"""
    # Check authentication
    if not (request.user.is_authenticated or request.session.get('student_logged_in')):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    student = get_object_or_404(Student, id=student_id)

    data = {
        'id': student.id,
        'ht_no': student.ht_no,
        'student_name': student.student_name,
        'father_name': student.father_name,
        'mother_name': student.mother_name,
        'gender': student.gender,
        'dob': student.dob.strftime('%Y-%m-%d') if student.dob else None,
        'age': student.age,
        'category': student.category,
        'religion': student.religion,
        'blood_group': student.blood_group,
        'aadhar': student.aadhar,
        'apaar_id': student.apaar_id,
        'address': student.address,
        'parent_phone': student.parent_phone,
        'student_phone': student.student_phone,
        'email': student.email,
        'year': student.year,
        'sem': student.sem,
        'branch': student.branch,
        'roll_number': student.roll_number,
        'ssc_marks': student.ssc_marks,
        'inter_marks': student.inter_marks,
        'cgpa': student.cgpa,
        'photo_url': student.photo_url,
        'pdf_url': student.pdf_url,
        'pdf_generated': student.pdf_generated,
        'pdf_generation_time': student.pdf_generation_time.strftime(
            '%Y-%m-%d %H:%M:%S') if student.pdf_generation_time else None,
        'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None,
        'updated_at': student.updated_at.strftime('%Y-%m-%d %H:%M:%S') if student.updated_at else None,
    }

    return JsonResponse(data)


# ==================== CHART & ANALYTICS ====================

@login_required
def faculty_charts(request):
    """Generate charts for faculty analytics"""
    if plt is None:
        messages.error(request, 'Matplotlib not installed. Charts unavailable.')
        return redirect('dashboard:dashboard')

    try:
        # Create charts directory
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # 1. Department Distribution Chart
        dept_data = Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:10]
        departments = [item['department'] for item in dept_data]
        counts = [item['count'] for item in dept_data]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(departments, counts, color=plt.cm.Set3(range(len(departments))))
        plt.title('Faculty Distribution by Department')
        plt.xlabel('Department')
        plt.ylabel('Number of Faculty')
        plt.xticks(rotation=45, ha='right')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                     f'{int(height)}', ha='center', va='bottom')

        plt.tight_layout()
        dept_chart_path = os.path.join(charts_dir, 'dept_distribution.png')
        plt.savefig(dept_chart_path, dpi=100)
        plt.close()

        # 2. Qualification Chart
        qual_data = {
            'PhD Completed': Faculty.objects.filter(phd_degree='Completed').count(),
            'PhD Pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
            'PG Only': Faculty.objects.filter(pg_year__isnull=False,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
            'UG Only': Faculty.objects.filter(ug_year__isnull=False, pg_year__isnull=True).count(),
        }

        plt.figure(figsize=(8, 8))
        labels = list(qual_data.keys())
        sizes = list(qual_data.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Faculty Qualification Distribution')

        qual_chart_path = os.path.join(charts_dir, 'qualification_distribution.png')
        plt.savefig(qual_chart_path, dpi=100)
        plt.close()

        # 3. Experience Chart
        today = date.today()
        exp_ranges = ['0-5 years', '5-10 years', '10-15 years', '15+ years']
        exp_counts = [0, 0, 0, 0]

        for faculty in Faculty.objects.all():
            if faculty.joining_date:
                exp_years = (today - faculty.joining_date).days / 365.25
                if exp_years <= 5:
                    exp_counts[0] += 1
                elif exp_years <= 10:
                    exp_counts[1] += 1
                elif exp_years <= 15:
                    exp_counts[2] += 1
                else:
                    exp_counts[3] += 1

        plt.figure(figsize=(10, 6))
        x = range(len(exp_ranges))
        bars = plt.bar(x, exp_counts, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        plt.title('Faculty Experience Distribution')
        plt.xlabel('Experience Range')
        plt.ylabel('Number of Faculty')
        plt.xticks(x, exp_ranges)

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, exp_counts)):
            plt.text(bar.get_x() + bar.get_width() / 2., count + 0.1,
                     f'{count}', ha='center', va='bottom')

        plt.tight_layout()
        exp_chart_path = os.path.join(charts_dir, 'experience_distribution.png')
        plt.savefig(exp_chart_path, dpi=100)
        plt.close()

        # Generate chart URLs
        chart_urls = {
            'dept_chart': os.path.join(settings.MEDIA_URL, 'charts', 'dept_distribution.png'),
            'qual_chart': os.path.join(settings.MEDIA_URL, 'charts', 'qualification_distribution.png'),
            'exp_chart': os.path.join(settings.MEDIA_URL, 'charts', 'experience_distribution.png'),
        }

        return render(request, 'dashboard/charts.html', {
            'title': 'Faculty Analytics Charts',
            'chart_urls': chart_urls,
            'dept_data': list(zip(departments, counts)),
            'qual_data': qual_data,
            'exp_data': list(zip(exp_ranges, exp_counts)),
        })

    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")
        messages.error(request, f'Error generating charts: {str(e)}')
        return redirect('dashboard:dashboard')


@login_required
def student_charts(request):
    """Generate charts for student analytics"""
    if plt is None:
        messages.error(request, 'Matplotlib not installed. Charts unavailable.')
        return redirect('dashboard:students_data')

    try:
        # Create charts directory
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        # 1. Gender Distribution
        gender_data = Student.objects.values('gender').annotate(count=Count('id')).order_by('-count')
        genders = [item['gender'] for item in gender_data]
        gender_counts = [item['count'] for item in gender_data]

        plt.figure(figsize=(8, 8))
        colors = ['#66b3ff', '#ff9999', '#99ff99']
        plt.pie(gender_counts, labels=genders, colors=colors[:len(genders)], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Student Gender Distribution')

        gender_chart_path = os.path.join(charts_dir, 'student_gender_distribution.png')
        plt.savefig(gender_chart_path, dpi=100)
        plt.close()

        # 2. Year-wise Distribution
        year_data = Student.objects.values('year').annotate(count=Count('id')).order_by('year')
        years = [item['year'] for item in year_data]
        year_counts = [item['count'] for item in year_data]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(years, year_counts, color=plt.cm.Paired(range(len(years))))
        plt.title('Student Distribution by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Students')

        # Add value labels
        for bar, count in zip(bars, year_counts):
            plt.text(bar.get_x() + bar.get_width() / 2., count + 0.1,
                     f'{count}', ha='center', va='bottom')

        plt.tight_layout()
        year_chart_path = os.path.join(charts_dir, 'student_year_distribution.png')
        plt.savefig(year_chart_path, dpi=100)
        plt.close()

        # 3. Category Distribution
        category_data = Student.objects.values('category').annotate(count=Count('id')).order_by('-count')[:10]
        categories = [item['category'] for item in category_data]
        category_counts = [item['count'] for item in category_data]

        plt.figure(figsize=(10, 6))
        x = range(len(categories))
        bars = plt.bar(x, category_counts, color=plt.cm.Set3(range(len(categories))))
        plt.title('Student Category Distribution (Top 10)')
        plt.xlabel('Category')
        plt.ylabel('Number of Students')
        plt.xticks(x, categories, rotation=45, ha='right')

        # Add value labels
        for bar, count in zip(bars, category_counts):
            plt.text(bar.get_x() + bar.get_width() / 2., count + 0.1,
                     f'{count}', ha='center', va='bottom')

        plt.tight_layout()
        category_chart_path = os.path.join(charts_dir, 'student_category_distribution.png')
        plt.savefig(category_chart_path, dpi=100)
        plt.close()

        # Generate chart URLs
        chart_urls = {
            'gender_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_gender_distribution.png'),
            'year_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_year_distribution.png'),
            'category_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_category_distribution.png'),
        }

        return render(request, 'dashboard/student_charts.html', {
            'title': 'Student Analytics Charts',
            'chart_urls': chart_urls,
            'gender_data': list(zip(genders, gender_counts)),
            'year_data': list(zip(years, year_counts)),
            'category_data': list(zip(categories, category_counts)),
        })

    except Exception as e:
        logger.error(f"Error generating student charts: {str(e)}")
        messages.error(request, f'Error generating charts: {str(e)}')
        return redirect('dashboard:students_data')


# ==================== MISCELLANEOUS FUNCTIONS ====================

@login_required
def recent_activity(request):
    """Show recent system activities"""
    activities = FacultyLog.objects.select_related('faculty', 'student').order_by('-created_at')[:50]

    return render(request, 'dashboard/recent_activity.html', {
        'title': 'Recent Activities',
        'activities': activities,
        'total_activities': FacultyLog.objects.count(),
    })


@login_required
def search_faculty(request):
    """Search faculty members"""
    query = request.GET.get('q', '')

    if query:
        faculties = Faculty.objects.filter(
            Q(staff_name__icontains=query) |
            Q(employee_code__icontains=query) |
            Q(department__icontains=query) |
            Q(designation__icontains=query) |
            Q(email__icontains=query)
        ).order_by('staff_name')[:20]
    else:
        faculties = Faculty.objects.none()

    results = []
    for faculty in faculties:
        results.append({
            'id': faculty.id,
            'name': faculty.staff_name,
            'employee_code': faculty.employee_code,
            'department': faculty.department,
            'designation': faculty.designation,
            'photo_url': faculty.cloudinary_photo_url or faculty.photo.url if faculty.photo else None,
            'detail_url': reverse('dashboard:faculty_dashboard') + f'?id={faculty.id}',
        })

    return JsonResponse({'results': results, 'count': len(results)})


@login_required
def search_students(request):
    """Search students"""
    query = request.GET.get('q', '')

    if query:
        students = Student.objects.filter(
            Q(student_name__icontains=query) |
            Q(ht_no__icontains=query) |
            Q(father_name__icontains=query) |
            Q(email__icontains=query)
        ).order_by('student_name')[:20]
    else:
        students = Student.objects.none()

    results = []
    for student in students:
        results.append({
            'id': student.id,
            'name': student.student_name,
            'ht_no': student.ht_no,
            'year': student.year,
            'sem': student.sem,
            'branch': student.branch,
            'roll_number': student.roll_number,
            'photo_url': student.photo_url,
            'detail_url': reverse('dashboard:students_data'),
        })

    return JsonResponse({'results': results, 'count': len(results)})


@login_required
def quick_stats(request):
    """Get quick statistics for dashboard widgets"""
    stats = {
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'recent_uploads': Faculty.objects.order_by('-created_at').count(),
        'cloudinary_uploads': CloudinaryUpload.objects.count(),
    }

    return JsonResponse(stats)


# ==================== ERROR HANDLERS ====================

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'dashboard/404.html', {
        'title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.'
    }, status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'dashboard/500.html', {
        'title': 'Server Error',
        'error_message': 'An internal server error occurred. Please try again later.'
    }, status=500)


def handler403(request, exception):
    """Custom 403 error handler"""
    return render(request, 'dashboard/403.html', {
        'title': 'Access Denied',
        'error_message': 'You do not have permission to access this page.'
    }, status=403)


def handler400(request, exception):
    """Custom 400 error handler"""
    return render(request, 'dashboard/400.html', {
        'title': 'Bad Request',
        'error_message': 'Invalid request. Please check your input.'
    }, status=400)


# ==================== MAIN APPLICATION VIEWS ====================

@login_required
def application_home(request):
    """Main application home page"""
    return render(request, 'dashboard/application_home.html', {
        'title': 'Faculty Management System',
        'user': request.user,
    })


@login_required
def profile_settings(request):
    """User profile settings"""
    user = request.user

    if request.method == 'POST':
        # Update user profile
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email

        # Update password if provided
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            messages.success(request, 'Password updated successfully.')
            # Re-login user with new password
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)

        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard:profile_settings')

    return render(request, 'dashboard/profile_settings.html', {
        'title': 'Profile Settings',
        'user': user,
    })


@login_required
def about_system(request):
    """About system page"""
    return render(request, 'dashboard/about.html', {
        'title': 'About Faculty Management System',
        'version': '2.0.0',
        'developed_by': 'ANURAG ENGINEERING COLLEGE',
        'contact_email': 'admin@anurag.edu.in',
        'features': [
            'Faculty Management with PDF generation',
            'Student Registration and Management',
            'Cloudinary Integration for file storage',
            'Certificate Management',
            'Analytics and Reporting',
            'Bulk Operations',
            'System Monitoring',
        ]
    })


@login_required
def help_documentation(request):
    """Help documentation page"""
    return render(request, 'dashboard/help.html', {
        'title': 'Help & Documentation',
        'sections': [
            {
                'title': 'Faculty Management',
                'content': 'Add, edit, delete faculty members. Generate PDF profiles and upload to Cloudinary.'
            },
            {
                'title': 'Student Management',
                'content': 'Register students, manage their data, generate student PDFs.'
            },
            {
                'title': 'Certificate Management',
                'content': 'Upload, view, and manage certificates for faculty members.'
            },
            {
                'title': 'Cloudinary Integration',
                'content': 'Sync faculty PDFs and photos to Cloudinary for secure cloud storage.'
            },
            {
                'title': 'Analytics',
                'content': 'View charts and statistics about faculty and students.'
            },
            {
                'title': 'System Tools',
                'content': 'Backup database, clear logs, check system status.'
            },
        ]
    })


@login_required
def contact_support(request):
    """Contact support page"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            # In a real application, you would send an email here
            # For now, we'll just log it and show a success message
            logger.info(f"Support request from {name} ({email}): {subject}")
            logger.info(f"Message: {message}")

            messages.success(request, 'Your message has been sent to support. We will get back to you soon.')
            return redirect('dashboard:contact_support')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'dashboard/contact.html', {
        'title': 'Contact Support',
        'support_email': 'support@anurag.edu.in',
        'phone': '+91 1234567890',
        'address': 'ANURAG ENGINEERING COLLEGE, Hyderabad, Telangana'
    })


# ==================== SESSION MANAGEMENT ====================

@login_required
def session_info(request):
    """Display session information"""
    session_info = {
        'session_key': request.session.session_key,
        'session_expiry_age': request.session.get_expiry_age(),
        'session_expiry_date': request.session.get_expiry_date(),
        'session_data': dict(request.session.items()),
        'user_authenticated': request.user.is_authenticated,
        'user_username': request.user.username,
        'user_email': request.user.email,
        'user_is_staff': request.user.is_staff,
        'user_is_superuser': request.user.is_superuser,
    }

    return render(request, 'dashboard/session_info.html', {
        'title': 'Session Information',
        'session_info': session_info,
    })


@login_required
def clear_session(request):
    """Clear session data (except authentication)"""
    # Save authentication data
    auth_data = {
        '_auth_user_id': request.session.get('_auth_user_id'),
        '_auth_user_backend': request.session.get('_auth_user_backend'),
        '_auth_user_hash': request.session.get('_auth_user_hash'),
    }

    # Clear all session data
    request.session.clear()

    # Restore authentication data
    for key, value in auth_data.items():
        if value:
            request.session[key] = value

    messages.success(request, 'Session data cleared successfully.')
    return redirect('dashboard:session_info')