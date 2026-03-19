# dashboard/views.py - COMPLETE MERGED VERSION
# ============================================================================

import os
import json
import csv
import tempfile
import logging
import uuid
import zipfile
from datetime import datetime, date, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Any

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import (HttpResponse, JsonResponse, HttpResponseRedirect,
                         FileResponse, HttpResponseBadRequest)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.urls import reverse
from django.utils import timezone
import django

# PDF Generation imports
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, HRFlowable, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from pypdf import PdfWriter, PdfReader
from PyPDF2 import PdfMerger
from PIL import Image as PILImage

# Cloudinary imports
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Local imports
from .models import (
    Faculty, Certificate, FacultyLog, CloudinaryUpload,
    Subject, FacultyProfile, ResearchProject, Student
)
from .forms import (
    LoginForm, StudentForm, FacultyForm, CertificateForm,
    BulkUploadForm, FacultyProfileForm, ResearchProjectForm
)
from .utils import (
    calculate_experience, generate_pdf_from_html, merge_pdfs,
    extract_text_from_pdf, validate_faculty_data, calculate_age,
    format_date, get_academic_year, send_email_notification,
    generate_qr_code, export_to_excel, validate_student_data
)

logger = logging.getLogger(__name__)

# ==================== OPTIONAL LIBRARIES ====================
try:
    import pandas as pd
except ImportError:
    pd = None
    logger.warning("Pandas not installed. Bulk upload features limited.")

try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil not installed. System monitoring limited.")

try:
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    plt = None
    np = None
    logger.warning("Matplotlib not installed. Chart features limited.")

try:
    import pdfkit
except ImportError:
    pdfkit = None
    logger.warning("pdfkit not installed. PDF generation features limited.")


# ==================== HELPERS ====================

def is_cloudinary_configured():
    return getattr(settings, 'CLOUDINARY_CONFIGURED', False)


if is_cloudinary_configured():
    try:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        logger.info("Cloudinary initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Cloudinary: {e}")
else:
    logger.warning("Cloudinary credentials not found.")


# ==================== DEBUG / TEST VIEWS ====================

def test_template(request):
    return render(request, 'test.html', {
        'title': 'Template Test',
        'message': 'If you can see this, templates are working correctly!'
    })


def test_session(request):
    return JsonResponse({
        'student_logged_in': request.session.get('student_logged_in', False),
        'student_username': request.session.get('student_username', None),
        'session_keys': list(request.session.keys()),
        'path': request.path,
        'method': request.method,
    })


def debug_cloudinary(request):
    config = {
        'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', None),
        'api_key': getattr(settings, 'CLOUDINARY_API_KEY', None),
        'api_secret': ('***' + getattr(settings, 'CLOUDINARY_API_SECRET', '')[-4:]
                       if getattr(settings, 'CLOUDINARY_API_SECRET', None) else None),
        'configured': is_cloudinary_configured(),
    }
    connection_test = False
    error_msg = None
    if config['configured']:
        try:
            cloudinary.api.ping()
            connection_test = True
        except Exception as e:
            error_msg = str(e)
    return JsonResponse({
        'config': config,
        'connection_test': connection_test,
        'error': error_msg,
        'env_vars': {
            'CLOUDINARY_CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
            'CLOUDINARY_API_KEY': (
                os.environ.get('CLOUDINARY_API_KEY')[:4] + '...'
                if os.environ.get('CLOUDINARY_API_KEY') else None
            ),
            'CLOUDINARY_API_SECRET': (
                '***' + os.environ.get('CLOUDINARY_API_SECRET', '')[-4:]
                if os.environ.get('CLOUDINARY_API_SECRET') else None
            ),
        }
    })


def debug_login(request):
    return HttpResponse(f"""
    <html><body style="background:black;color:lime;font-family:monospace;padding:20px;">
    <h1>Login Debug Info</h1><pre>
student_logged_in: {request.session.get('student_logged_in', False)}
student_username: {request.session.get('student_username', 'None')}
session keys: {list(request.session.keys())}
user authenticated: {request.user.is_authenticated}
user: {request.user}
    </pre>
    <p><a href="/student-login/">Go to Student Login</a></p>
    <p><a href="/students-data/">Go to Students Data</a></p>
    <p><a href="/add-student/">Go to Add Student</a></p>
    </body></html>
    """)


@login_required
def debug_faculty_data(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    data = {}
    for field in Faculty._meta.fields:
        fn = field.name
        fv = getattr(faculty, fn)
        if fn == 'photo' and fv:
            try:
                data[fn] = {'url': fv.url if hasattr(fv, 'url') else str(fv), 'exists': True}
            except Exception:
                data[fn] = str(fv)
        elif fv and hasattr(fv, 'strftime'):
            data[fn] = fv.strftime('%Y-%m-%d')
        else:
            data[fn] = str(fv) if fv else None
    certificates = Certificate.objects.filter(faculty=faculty)
    data['certificates'] = [
        {
            'id': c.id,
            'certificate_type': c.certificate_type,
            'certificate_file': str(c.certificate_file) if c.certificate_file else None,
            'cloudinary_url': c.cloudinary_url,
            'issue_date': c.issue_date.strftime('%Y-%m-%d') if c.issue_date else None
        }
        for c in certificates
    ]
    data['subjects'] = [s.name for s in faculty.subjects.all()]
    return JsonResponse(data, safe=False, json_dumps_params={'indent': 2})


# ==================== FACULTY PROFILE VIEW ====================

@login_required
def edit_faculty_complete(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == "POST":
        for attr in ['staff_name', 'employee_code', 'department', 'designation', 'email', 'mobile',
                     'gender', 'address', 'father_name', 'mother_name', 'aadhar', 'pan', 'state',
                     'caste', 'sub_caste', 'nationality', 'jntuh_id', 'aicte_id', 'orcid_id', 'apaar_id',
                     'ug_degree', 'ug_college', 'ug_spec', 'pg_degree', 'pg_college', 'pg_spec',
                     'phd_degree', 'phd_university', 'phd_spec', 'about_yourself']:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)
        for date_attr in ['joining_date', 'dob', 'ug_year', 'pg_year', 'phd_year']:
            val = request.POST.get(date_attr)
            if val:
                setattr(faculty, date_attr, val)
        for pct_attr in ['ug_percentage', 'pg_percentage', 'ssc_percent', 'inter_percent']:
            val = request.POST.get(pct_attr)
            if val:
                setattr(faculty, pct_attr, val)
        for text_attr in ['ssc_year', 'ssc_school', 'inter_year', 'inter_college']:
            val = request.POST.get(text_attr)
            if val:
                setattr(faculty, text_attr, val)
        if request.FILES.get("photo"):
            faculty.photo = request.FILES["photo"]
        faculty.save()
        messages.success(request, f'Faculty {faculty.staff_name} updated successfully!')
        return HttpResponseRedirect(reverse('dashboard:faculty_dashboard') + f'?id={faculty.id}')
    return render(request, 'dashboard/edit_faculty_complete.html', {
        'faculty': faculty,
        'title': f'Edit Faculty - {faculty.staff_name}',
    })


@login_required
def faculty_profile_view(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    profile, _ = FacultyProfile.objects.get_or_create(faculty=faculty)
    research_projects = ResearchProject.objects.filter(faculty=faculty)

    if request.method == "POST":
        profile_form = FacultyProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save()
            research_types = request.POST.getlist('research_type[]')
            titles = request.POST.getlist('title_of_project[]')
            marks = request.POST.getlist('marks_awarded[]')
            dois = request.POST.getlist('doi[]')
            volumes = request.POST.getlist('volume[]')
            issns = request.POST.getlist('issn_number[]')
            journals = request.POST.getlist('journal_name[]')
            publishers = request.POST.getlist('publisher_name[]')
            project_ids = request.POST.getlist('project_id[]')

            for i in range(len(titles)):
                if not titles[i]:
                    continue
                pid = project_ids[i] if i < len(project_ids) else None
                if pid and pid.isdigit():
                    proj = get_object_or_404(ResearchProject, id=int(pid), faculty=faculty)
                    proj.research_type = research_types[i] if i < len(research_types) else ''
                    proj.title_of_project = titles[i]
                    proj.marks_awarded = marks[i] if i < len(marks) and marks[i] else None
                    proj.doi = dois[i] if i < len(dois) else ''
                    proj.volume = volumes[i] if i < len(volumes) else ''
                    proj.issn_number = issns[i] if i < len(issns) else ''
                    proj.journal_name = journals[i] if i < len(journals) else ''
                    proj.publisher_name = publishers[i] if i < len(publishers) else ''
                    if request.FILES.get(f'upload_pdf_{i}'):
                        proj.upload_pdf = request.FILES[f'upload_pdf_{i}']
                    proj.save()
                else:
                    ResearchProject.objects.create(
                        faculty=faculty,
                        faculty_profile=profile,
                        research_type=research_types[i] if i < len(research_types) else '',
                        title_of_project=titles[i],
                        marks_awarded=marks[i] if i < len(marks) and marks[i] else None,
                        doi=dois[i] if i < len(dois) else '',
                        volume=volumes[i] if i < len(volumes) else '',
                        issn_number=issns[i] if i < len(issns) else '',
                        journal_name=journals[i] if i < len(journals) else '',
                        publisher_name=publishers[i] if i < len(publishers) else '',
                        upload_pdf=request.FILES.get(f'upload_pdf_{i}') or None,
                    )
            messages.success(request, 'Faculty profile updated successfully!')
            return redirect('dashboard:faculty_profile_view', faculty_id=faculty.id)
    else:
        profile_form = FacultyProfileForm(instance=profile)

    return render(request, 'dashboard/faculty_profile.html', {
        'faculty': faculty, 'profile': profile,
        'profile_form': profile_form, 'research_projects': research_projects,
        'title': f'Profile - {faculty.staff_name}',
    })


@login_required
@require_POST
def delete_research_project(request, project_id):
    project = get_object_or_404(ResearchProject, id=project_id)
    project.delete()
    messages.success(request, 'Research project deleted successfully.')
    return JsonResponse({'success': True})


def laboratory(request):
    return render(request, 'dashboard/laboratory.html', {'title': 'Laboratory'})


def gallery(request):
    return render(request, 'dashboard/gallery.html', {'title': 'Gallery'})


def student_detail(request, student_id):
    if not request.session.get('student_logged_in') and not request.user.is_authenticated:
        return redirect('dashboard:student_login')
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'dashboard/student_detail.html', {
        'student': student,
        'title': f'{student.student_name} - Details',
    })


# ==================== CLOUDINARY SYNC ====================

@login_required
def sync_to_cloudinary(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if not is_cloudinary_configured():
        messages.error(request, "Cloudinary is not configured properly.")
        return redirect("dashboard:faculty_dashboard")

    if faculty.pdf_document and not faculty.cloudinary_pdf_url:
        try:
            with faculty.pdf_document.open("rb") as f:
                resp = cloudinary.uploader.upload(
                    f, folder="faculty_pdfs", resource_type="raw",
                    public_id=f"faculty_{faculty.employee_code}_profile", overwrite=True,
                )
            faculty.cloudinary_pdf_url = resp["secure_url"]
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type="pdf",
                cloudinary_url=resp["secure_url"], public_id=resp["public_id"],
                resource_type=resp["resource_type"], uploaded_by=request.user.username,
            )
        except Exception as e:
            messages.error(request, f"Error uploading PDF: {e}")
            return redirect("dashboard:faculty_dashboard")

    if faculty.photo and not faculty.cloudinary_photo_url:
        try:
            with faculty.photo.open("rb") as f:
                resp = cloudinary.uploader.upload(
                    f, folder="faculty_photos",
                    public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                    transformation=[{'width': 300, 'height': 300, 'crop': 'fill'},
                                    {'quality': 'auto:good'}]
                )
            faculty.cloudinary_photo_url = resp["secure_url"]
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type="photo",
                cloudinary_url=resp["secure_url"], public_id=resp["public_id"],
                resource_type=resp["resource_type"], uploaded_by=request.user.username,
            )
        except Exception as e:
            messages.error(request, f"Error uploading photo: {e}")
            return redirect("dashboard:faculty_dashboard")

    FacultyLog.objects.create(
        faculty=faculty, action="Cloudinary Sync",
        details=f"Faculty synced to Cloudinary: {faculty.employee_code}",
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    messages.success(request, f"Faculty {faculty.employee_code} synced to Cloudinary.")
    return redirect("dashboard:faculty_dashboard")


@login_required
def upload_to_cloudinary(request, faculty_id):
    return sync_to_cloudinary(request, faculty_id)


# ==================== AUTHENTICATION ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    if request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    return render(request, 'dashboard/login.html', {
        'title': 'Login - ANURAG ENGINEERING COLLEGE',
        'student_login': False, 'admin_login': False,
    })


@csrf_protect
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Admin login successful!')
            return redirect('dashboard:dashboard')
        else:
            error = 'Invalid admin credentials'
            messages.error(request, error)
    return render(request, 'dashboard/login.html', {
        'title': 'Admin Login - ANURAG ENGINEERING COLLEGE',
        'admin_login': True, 'error': error,
    })


def student_login(request):
    if request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "anrkitstudent" and password == "anrkitstudent":
            request.session["student_logged_in"] = True
            request.session["student_username"] = username
            messages.success(request, "Student login successful!")
            return redirect("dashboard:students_data")
        error = "Invalid student credentials"
        messages.error(request, error)
    return render(request, 'dashboard/login.html', {
        'student_login': True, 'error': error,
        'title': 'Student Login - ANURAG ENGINEERING COLLEGE'
    })


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
    else:
        messages.success(request, 'Logged out successfully.')
    for key in ('student_logged_in', 'student_username', 'student_role'):
        request.session.pop(key, None)
    return redirect('dashboard:login')


def student_logout(request):
    request.session.flush()
    messages.success(request, "Student logged out successfully.")
    return redirect('dashboard:student_login')


def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
    return redirect('dashboard:admin_login')


# ==================== HOME & DASHBOARD ====================

def home(request):
    if request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard')
    if request.user.is_authenticated:
        return redirect('dashboard:admin_dashboard' if request.user.is_superuser else 'dashboard:dashboard')
    return render(request, 'dashboard/home.html', {
        'title': 'Faculty Management System - Home',
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:5],
        'recent_activities': FacultyLog.objects.order_by('-created_at')[:5],
        'show_hero': True,
    })


@login_required
def dashboard(request):
    total_faculty = Faculty.objects.count()
    with_phd = Faculty.objects.exclude(phd_degree__isnull=True).exclude(phd_degree__exact='').count()
    today = date.today()
    exp_distribution = {'0-5': 0, '5-10': 0, '10-15': 0, '15+': 0}
    for f in Faculty.objects.all():
        if f.joining_date:
            yrs = (today - f.joining_date).days / 365.25
            if yrs <= 5:
                exp_distribution['0-5'] += 1
            elif yrs <= 10:
                exp_distribution['5-10'] += 1
            elif yrs <= 15:
                exp_distribution['10-15'] += 1
            else:
                exp_distribution['15+'] += 1
    return render(request, "dashboard/dashboard.html", {
        'title': 'Dashboard',
        'total_faculty': total_faculty,
        'with_phd': with_phd,
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_certificates': Certificate.objects.count(),
        'departments': Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count'),
        'recent_uploads': Faculty.objects.order_by('-created_at')[:5],
        'recent_logs': FacultyLog.objects.order_by('-created_at')[:5],
        'exp_distribution': exp_distribution,
        'today': today, 'user': request.user,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard')
    total_faculty = Faculty.objects.count()
    departments = list(Faculty.objects.values('department')
                       .annotate(count=Count('id'), active=Count('id', filter=Q(is_active=True)))
                       .order_by('-count'))
    for d in departments:
        d['percentage'] = (d['count'] / total_faculty * 100) if total_faculty > 0 else 0
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
            system_stats = {'error': str(e)}
    return render(request, "dashboard/admin_dashboard.html", {
        'title': 'Admin Dashboard',
        'total_faculty': total_faculty,
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'cloudinary_uploads': CloudinaryUpload.objects.count(),
        'with_phd': Faculty.objects.filter(phd_degree='Completed').count(),
        'departments': departments,
        'recent_logs': FacultyLog.objects.order_by('-created_at')[:10],
        'system_stats': system_stats,
        'user_activity': {
            'total_users': User.objects.count(),
            'active_today': FacultyLog.objects.filter(
                created_at__date=date.today()).values('performed_by').distinct().count(),
        },
        'has_psutil': psutil is not None,
        'recent_uploads': Faculty.objects.order_by('-created_at')[:5],
    })


def student_dashboard(request):
    if not request.session.get('student_logged_in'):
        messages.error(request, 'Please login to access student dashboard')
        return redirect('dashboard:student_login')
    student_username = request.session.get('student_username', 'anrkitstudent')
    student = None
    try:
        student = Student.objects.filter(ht_no=student_username).first()
    except Exception as e:
        logger.error(f"Error getting student data: {e}")
    if not student:
        student = {
            'ht_no': student_username, 'student_name': 'Student User',
            'year': 'II', 'sem': 'II', 'branch': 'Computer Science',
            'email': 'student@anurag.edu.in', 'student_phone': 'Not Available',
            'cgpa': None, 'photo': None, 'photo_url': None,
        }
    certificates = []
    if student and hasattr(student, 'id'):
        for fn, dn in [('cert_achieve', 'Achievement'), ('cert_intern', 'Internship'),
                       ('cert_courses', 'Courses'), ('cert_sdp', 'SDP'),
                       ('cert_extra', 'Extra Curricular'), ('cert_placement', 'Placement'),
                       ('cert_national', 'National Exam')]:
            if hasattr(student, fn) and getattr(student, fn):
                certificates.append({'type': dn, 'field': fn, 'has_file': True})
    return render(request, "dashboard/student_dashboard.html", {
        'student': student, 'title': 'Student Dashboard',
        'total_students': Student.objects.count(),
        'recent_students': Student.objects.order_by('-created_at')[:5],
        'certificates': certificates, 'is_student': True,
    })


def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect('dashboard:admin_dashboard' if request.user.is_superuser else 'dashboard:dashboard')
    elif request.session.get('student_logged_in'):
        return redirect('dashboard:student_dashboard')
    return redirect('dashboard:login')


@login_required
def syllabus_view(request):
    return render(request, 'dashboard/students.html', {
        'title': 'Syllabus & Common Subjects - ANURAG Engineering College',
    })


# ==================== FACULTY DASHBOARD ====================

@login_required
def faculty_dashboard(request):
    pdf_mode = request.GET.get("print") == "1"
    if pdf_mode:
        fid = request.GET.get("id")
        if not fid:
            return HttpResponseBadRequest("Faculty ID required for PDF mode")
        f = get_object_or_404(Faculty, id=fid)
        exp = calculate_experience(f.joining_date) if f.joining_date else "N/A"
        return render(request, "dashboard/faculty_pdf.html", {
            "faculty": f, "pdf_mode": True, "current_date": timezone.now(),
            "experience": exp, "cloudinary_status": {"has_pdf": bool(f.cloudinary_pdf_url)},
        })

    faculties = Faculty.objects.all().order_by('staff_name')
    fid = request.GET.get('id')
    faculty = certificates = None

    if fid:
        faculty = get_object_or_404(Faculty, id=fid)
    elif faculties.exists():
        faculty = faculties.first()

    if faculty:
        certificates = Certificate.objects.filter(faculty=faculty)

    if request.GET.get('analytics') == 'true' or (not faculty and faculties.exists()):
        return faculty_analytics(request)

    experience = calculate_experience(faculty.joining_date) if faculty and faculty.joining_date else "N/A"
    departments = Faculty.objects.values_list('department', flat=True).distinct().order_by('department')

    return render(request, 'dashboard/faculty.html', {
        'faculties': faculties, 'faculty': faculty, 'certificates': certificates or [],
        'experience': experience,
        'cloudinary_status': {
            'has_pdf': bool(faculty.cloudinary_pdf_url) if faculty else False,
            'has_photo': bool(faculty.cloudinary_photo_url) if faculty else False,
        },
        'current_date': timezone.now(), 'is_analytics': False, 'pdf_mode': False,
        'departments': departments,
        'title': f'Faculty Profile - {faculty.staff_name}' if faculty else 'Faculty Dashboard',
    })


@login_required
def faculty_analytics(request):
    total = Faculty.objects.count()
    departments = list(Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count'))
    for d in departments:
        d['percentage'] = (d['count'] / total * 100) if total > 0 else 0
    today = date.today()
    exp_stats = {'0_5': 0, '5_10': 0, '10_plus': 0}
    for f in Faculty.objects.all():
        if f.joining_date:
            yrs = today.year - f.joining_date.year
            if yrs <= 5:
                exp_stats['0_5'] += 1
            elif yrs <= 10:
                exp_stats['5_10'] += 1
            else:
                exp_stats['10_plus'] += 1
    return render(request, 'dashboard/faculty.html', {
        'is_analytics': True, 'total_faculty': total,
        'qualification_stats': {
            'phd_completed': Faculty.objects.filter(phd_degree='Completed').count(),
            'phd_pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
            'pg_only': Faculty.objects.filter(pg_year__isnull=False,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
            'ug_only': Faculty.objects.filter(ug_year__isnull=False, pg_year__isnull=True,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
        },
        'departments': departments, 'experience_stats': exp_stats,
        'faculties': Faculty.objects.all()[:10], 'title': 'Faculty Analytics',
    })


# ==================== FACULTY LIST ====================

@login_required
def faculty_list(request):
    qs = Faculty.objects.all().order_by('staff_name')
    sq = request.GET.get('search', '')
    if sq:
        qs = qs.filter(Q(staff_name__icontains=sq) | Q(employee_code__icontains=sq) |
                       Q(email__icontains=sq) | Q(department__icontains=sq) | Q(designation__icontains=sq))
    df = request.GET.get('department', '')
    if df: qs = qs.filter(department__icontains=df)
    sf = request.GET.get('status', '')
    if sf == 'active':
        qs = qs.filter(is_active=True)
    elif sf == 'inactive':
        qs = qs.filter(is_active=False)
    qf = request.GET.get('qualification', '')
    if qf == 'phd':
        qs = qs.filter(phd_degree='Completed')
    elif qf == 'pg':
        qs = qs.filter(pg_year__isnull=False, phd_degree__in=['', 'Not Started', 'None'])
    paginator = Paginator(qs, 20)
    try:
        faculties = paginator.page(request.GET.get('page', 1))
    except (PageNotAnInteger, EmptyPage) as e:
        faculties = paginator.page(1 if isinstance(e, PageNotAnInteger) else paginator.num_pages)
    return render(request, 'dashboard/faculty_list.html', {
        'faculties': faculties,
        'departments': Faculty.objects.values_list('department', flat=True).distinct().order_by('department'),
        'search_query': sq, 'department_filter': df, 'status_filter': sf, 'qualification_filter': qf,
        'total_faculty': qs.count(), 'page_title': 'Faculty Directory', 'active_page': 'faculty_list',
    })


# ==================== ADD FACULTY ====================

@login_required
# ==================== ADD FACULTY ====================

@login_required
def add_faculty(request):
    if request.method == "POST":
        try:
            # Handle empty numeric fields by converting empty strings to None
            def get_int_or_none(value):
                return int(value) if value and value.strip() else None

            def get_float_or_none(value):
                return float(value) if value and value.strip() else None

            faculty = Faculty.objects.create(
                staff_name=request.POST.get("staff_name"),
                employee_code=request.POST.get("employee_code"),
                father_name=request.POST.get("father_name"),
                mother_name=request.POST.get("mother_name"),
                dob=request.POST.get("dob") or None,
                gender=request.POST.get("gender"),
                state=request.POST.get("state"),
                caste=request.POST.get("caste"),
                sub_caste=request.POST.get("sub_caste"),
                nationality=request.POST.get("nationality", "Indian"),
                address=request.POST.get("address"),
                mobile=request.POST.get("mobile"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email"),
                department=request.POST.get("department"),
                designation=request.POST.get("designation"),
                joining_date=request.POST.get("joining_date") or None,
                jntuh_id=request.POST.get("jntuh_id"),
                aicte_id=request.POST.get("aicte_id"),
                pan=request.POST.get("pan"),
                aadhar=request.POST.get("aadhar"),
                apaar_id=request.POST.get("apaar_id"),
                orcid_id=request.POST.get("orcid_id"),
                ssc_year=get_int_or_none(request.POST.get("ssc_year")),
                ssc_percent=get_float_or_none(request.POST.get("ssc_percent")),
                ssc_school=request.POST.get("ssc_school"),
                inter_year=get_int_or_none(request.POST.get("inter_year")),
                inter_percent=get_float_or_none(request.POST.get("inter_percent")),
                inter_college=request.POST.get("inter_college"),
                ug_degree=request.POST.get("ug_degree"),
                ug_year=get_int_or_none(request.POST.get("ug_year")),
                ug_percentage=get_float_or_none(request.POST.get("ug_percentage")),
                ug_college=request.POST.get("ug_college"),
                ug_spec=request.POST.get("ug_spec"),
                pg_degree=request.POST.get("pg_degree"),
                pg_year=get_int_or_none(request.POST.get("pg_year")),
                pg_percentage=get_float_or_none(request.POST.get("pg_percentage")),
                pg_college=request.POST.get("pg_college"),
                pg_spec=request.POST.get("pg_spec"),
                phd_degree=request.POST.get("phd_degree"),
                phd_year=get_int_or_none(request.POST.get("phd_year")),
                phd_university=request.POST.get("phd_university"),
                phd_spec=request.POST.get("phd_spec"),
                subjects_dealt=request.POST.get("subjects_dealt"),
                scm=request.POST.get("scm"),
                about_yourself=request.POST.get("about_yourself"),
                results=request.POST.get("results"),
                photo=request.FILES.get("photo"),
            )
            FacultyProfile.objects.create(faculty=faculty)

            # Save photo to Cloudinary if configured
            if request.FILES.get("photo") and is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES["photo"], folder="faculty_photos",
                        public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                        transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                    )
                    faculty.cloudinary_photo_url = cr["secure_url"]
                    faculty.save()
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type="photo",
                        cloudinary_url=cr["secure_url"], public_id=cr["public_id"],
                        resource_type=cr["resource_type"],
                        uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                    )
                except Exception as e:
                    logger.error(f"Cloudinary upload error: {e}")
                    messages.warning(request, "Faculty added but Cloudinary photo upload failed.")

            # Save ALL document & certificate fields uploaded via the form
            doc_fields = [
                'aadhar_file', 'pan_file', 'apaar_file', 'scm_file',
                'ssc_certificate', 'inter_certificate',
                'ug_certificate', 'pg_certificate', 'phd_certificate',
            ]
            needs_save = False
            for ffile in doc_fields:
                if request.FILES.get(ffile):
                    setattr(faculty, ffile, request.FILES[ffile])
                    needs_save = True
            if needs_save:
                faculty.save()

            messages.success(request, "Faculty added successfully.")
            return redirect("dashboard:faculty_dashboard")
        except Exception as e:
            logger.error(f"Error adding faculty: {e}")
            messages.error(request, f"Error adding faculty: {e}")
            return redirect("dashboard:add_faculty")
    return render(request, "dashboard/faculty.html", {"add_mode": True, "faculty": None, "title": "Add Faculty"})


# ==================== EDIT FACULTY ====================

@login_required
def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == "POST":
        # ── SIMPLE & ROBUST: setattr all form fields, then call save()
        # Django's save() internally uses _meta.concrete_fields to build
        # the SQL UPDATE, so any extra Python attributes that don't map
        # to DB columns are simply ignored — no errors, no data loss.
        # This is SAFER than filtering with _meta.get_fields() which can
        # miss fields or produce false negatives.

        # All text/char/number fields the edit form submits
        text_fields = [
            # Personal
            'staff_name', 'employee_code', 'father_name', 'mother_name',
            'gender', 'state', 'caste', 'sub_caste', 'nationality', 'address',
            # Contact
            'email', 'mobile', 'phone', 'department', 'designation',
            # Professional IDs
            'jntuh_id', 'aicte_id', 'pan', 'aadhar', 'apaar_id', 'orcid_id',
            # Education — SSC
            'ssc_year', 'ssc_percent', 'ssc_school',
            # Education — Intermediate
            'inter_year', 'inter_percent', 'inter_college',
            # Education — UG
            'ug_degree', 'ug_year', 'ug_percentage', 'ug_college', 'ug_spec',
            # Education — PG
            'pg_degree', 'pg_year', 'pg_percentage', 'pg_college', 'pg_spec',
            # Education — PhD
            'phd_degree', 'phd_year', 'phd_university', 'phd_spec',
            # Additional info
            'subjects_dealt', 'scm', 'about_yourself', 'results',
        ]

        for attr in text_fields:
            val = request.POST.get(attr)
            if val is not None:
                setattr(faculty, attr, val)

        # Date fields: empty string → None to avoid DB errors
        for date_attr in ['dob', 'joining_date']:
            val = request.POST.get(date_attr)
            setattr(faculty, date_attr, val if val else None)

        # ── FacultyProfile (separate model) ────────────────────────────
        try:
            profile, _ = FacultyProfile.objects.get_or_create(faculty=faculty)
            for fp_attr in ['experience_other', 'experience_at_anurag', 'batch_number']:
                form_key = {
                    'experience_other': 'exp_other',
                    'experience_at_anurag': 'exp_anurag',
                    'batch_number': 'batch_number',
                }.get(fp_attr, fp_attr)
                val = request.POST.get(form_key)
                if val is not None and hasattr(profile, fp_attr):
                    setattr(profile, fp_attr, val)
            profile.save()
        except Exception as e:
            logger.error(f"FacultyProfile save error: {e}")

        if request.FILES.get("photo"):
            faculty.photo = request.FILES["photo"]
            if is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES["photo"], folder="faculty_photos",
                        public_id=f"faculty_{faculty.employee_code}_photo", overwrite=True,
                        transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
                    )
                    faculty.cloudinary_photo_url = cr["secure_url"]
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type="photo",
                        cloudinary_url=cr["secure_url"], public_id=cr["public_id"],
                        resource_type=cr["resource_type"], uploaded_by=request.user.username
                    )
                except Exception as e:
                    logger.error(f"Cloudinary upload error during edit: {e}")
                    messages.warning(request, "Photo saved but Cloudinary upload failed.")

        # Save ALL document fields — identity docs + education certificates
        all_doc_fields = [
            'aadhar_file', 'pan_file', 'apaar_file', 'scm_file',
            'ssc_certificate', 'inter_certificate',
            'ug_certificate', 'pg_certificate', 'phd_certificate',
        ]
        for ffile in all_doc_fields:
            if request.FILES.get(ffile):
                setattr(faculty, ffile, request.FILES[ffile])
        faculty.save()
        messages.success(request, f'Faculty {faculty.staff_name} updated successfully!')
        return redirect("dashboard:faculty_dashboard")
    return render(request, "dashboard/faculty.html", {"add_mode": True, "faculty": faculty, "title": "Edit Faculty"})


@login_required
def delete_faculty(request, faculty_id):
    """Delete faculty member — supports both AJAX and normal form POST."""
    faculty = get_object_or_404(Faculty, id=faculty_id)

    if request.method == 'POST':
        faculty_name = faculty.staff_name
        employee_code = faculty.employee_code

        # Log before deletion
        FacultyLog.objects.create(
            faculty=None,
            action='Faculty Deleted',
            details=f'Faculty deleted: {faculty_name} ({employee_code})',
            performed_by=request.user.username,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        faculty.delete()

        # Detect AJAX — check both X-Requested-With and Accept header
        is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '')
        )
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Faculty {faculty_name} deleted successfully.'
            })

        messages.success(request, f'Faculty {faculty_name} deleted successfully.')
        return redirect('dashboard:faculty_list')

    # GET → confirmation page
    return render(request, 'dashboard/confirm_delete.html', {
        'faculty': faculty,
        'page_title': f'Delete {faculty.staff_name}',
    })


@login_required
def assign_subjects(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        subject_ids = request.POST.getlist('subjects')
        old_subjects = set(faculty.subjects.values_list('id', flat=True))
        new_subjects = set(map(int, subject_ids))
        faculty.subjects.set(Subject.objects.filter(id__in=subject_ids))
        changes = []
        added = new_subjects - old_subjects
        removed = old_subjects - new_subjects
        if added:
            changes.append(f"Added: {', '.join(Subject.objects.filter(id__in=added).values_list('name', flat=True))}")
        if removed:
            changes.append(
                f"Removed: {', '.join(Subject.objects.filter(id__in=removed).values_list('name', flat=True))}")
        FacultyLog.objects.create(
            faculty=faculty, action='Subjects Assigned',
            details=f"Subjects updated. {'; '.join(changes) if changes else 'No changes'}",
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f'Subjects assigned to {faculty.staff_name} successfully!')
        return HttpResponseRedirect(reverse('dashboard:faculty_dashboard') + f'?id={faculty.id}')
    return render(request, 'dashboard/assign_subjects.html', {
        'faculty': faculty,
        'available_subjects': Subject.objects.all(),
        'assigned_subjects': faculty.subjects.all(),
        'page_title': f'Assign Subjects to {faculty.staff_name}',
        'active_page': 'assign_subjects',
    })


# ==================== STUDENT MANAGEMENT ====================

def students(request):
    return redirect('dashboard:add_student')


def students_data(request):
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:student_login')
    qs = Student.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "dashboard/students_data.html", {
        "title": "Students Data", "students": page_obj,
        "total_students": qs.count(),
        "year_1_count": qs.filter(year=1).count(), "year_2_count": qs.filter(year=2).count(),
        "year_3_count": qs.filter(year=3).count(), "year_4_count": qs.filter(year=4).count(),
        "years": Student.objects.values_list("year", flat=True).distinct(),
        "sems": Student.objects.values_list("sem", flat=True).distinct(),
        "is_paginated": page_obj.has_other_pages(), "page_obj": page_obj,
    })


def add_student(request):
    if request.method == 'POST':
        try:
            ca = is_cloudinary_configured()

            def _upload(file, folder):
                if not file or not ca:
                    return None
                try:
                    res = cloudinary.uploader.upload(
                        file, resource_type="auto",
                        folder=f"student_documents/{folder}",
                        public_id=f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=True
                    )
                    return res['secure_url']
                except Exception as e:
                    logger.error(f"Cloudinary upload error ({folder}): {e}")
                    if hasattr(file, 'seek'): file.seek(0)
                    return None

            student = Student(
                ht_no=request.POST.get('ht_no'),
                student_name=request.POST.get('student_name'),
                father_name=request.POST.get('father_name'),
                mother_name=request.POST.get('mother_name'),
                gender=request.POST.get('gender'),
                dob=request.POST.get('dob'),
                age=request.POST.get('age'),
                nationality=request.POST.get('nationality', 'Indian'),
                category=request.POST.get('category'),
                religion=request.POST.get('religion'),
                blood_group=request.POST.get('blood_group'),
                aadhar=request.POST.get('aadhar'),
                apaar_id=request.POST.get('apaar_id'),
                address=request.POST.get('address'),
                parent_phone=request.POST.get('parent_phone'),
                student_phone=request.POST.get('student_phone'),
                email=request.POST.get('email'),
                task_registered=request.POST.get('task_registered'),
                task_username=request.POST.get('task_username'),
                csi_registered=request.POST.get('csi_registered'),
                csi_membership_id=request.POST.get('csi_membership_id'),
                admission_type=request.POST.get('admission_type'),
                other_admission_details=request.POST.get('other_admission_details'),
                eamcet_rank=request.POST.get('eamcet_rank') or None,
                year=request.POST.get('year'),
                sem=request.POST.get('sem'),
                ssc_marks=request.POST.get('ssc_marks'),
                inter_marks=request.POST.get('inter_marks'),
                cgpa=request.POST.get('cgpa'),
                rtrp_project_title=request.POST.get('rtrp_project_title'),
                intern_title=request.POST.get('intern_title'),
                final_project_title=request.POST.get('final_project_title'),
                other_training=request.POST.get('other_training'),
                photo=None, cert_achieve=None, cert_intern=None, cert_courses=None,
                cert_sdp=None, cert_extra=None, cert_placement=None, cert_national=None,
            )
            student.save()

            files_up, files_lo = [], []

            # Photo
            if request.FILES.get('photo'):
                pf = request.FILES['photo']
                url = _upload(pf, 'photos')
                if url:
                    student.photo_url = url
                    student.photo = None
                    files_up.append('photo')
                else:
                    student.photo = pf
                    files_lo.append('photo')

            # Certificates
            for fn, folder in [('cert_achieve', 'achievement'), ('cert_intern', 'internship'),
                               ('cert_courses', 'courses'), ('cert_sdp', 'sdp'),
                               ('cert_extra', 'extra'), ('cert_placement', 'placement'),
                               ('cert_national', 'national')]:
                if request.FILES.get(fn):
                    cf = request.FILES[fn]
                    url = _upload(cf, folder)
                    if url:
                        setattr(student, fn, url)
                        files_up.append(fn)
                    else:
                        setattr(student, fn, cf)
                        files_lo.append(fn)

            student.save()

            if files_up:
                messages.success(request, f'Student {student.student_name} added! Cloudinary: {", ".join(files_up)}')
            if files_lo:
                messages.warning(request, f'Some files saved locally: {", ".join(files_lo)}')
            if not files_up and not files_lo:
                messages.success(request, f'Student {student.student_name} added successfully!')

            return redirect('dashboard:students_data')
        except Exception as e:
            import traceback;
            traceback.print_exc()
            messages.error(request, f'Error adding student: {e}')
            return redirect('dashboard:add_student')
    return render(request, 'dashboard/add_student.html')


@require_POST
def delete_student(request, student_id):
    if not request.session.get('student_logged_in'):
        return redirect('dashboard:students_data')
    student = get_object_or_404(Student, id=student_id)
    name, ht = student.student_name, student.ht_no
    student.delete()
    messages.success(request, f"Student {name} ({ht}) deleted successfully.")
    return redirect('dashboard:students_data')


def edit_student(request, student_id):
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
    return render(request, 'dashboard/add_student.html', {'form': form, 'title': 'Edit Student'})


# ==================== PDF MERGE UTILITY ====================

def merge_files(file_list):
    from pypdf import PdfMerger
    from PIL import Image
    import tempfile
    import os
    import requests

    merger = PdfMerger()
    temp_files = []

    print("\n========== PDF MERGE START ==========")

    for idx, file in enumerate(file_list):
        if not file:
            print(f"[{idx}] Skipped (empty)")
            continue

        try:
            # Get URL or path
            file_url = file.url if hasattr(file, "url") else str(file)

            print(f"[{idx}] Processing: {file_url}")

            # Step 1: Download if URL
            if file_url.startswith("http"):
                response = requests.get(file_url, timeout=20)
                if response.status_code != 200:
                    print("  ❌ Download failed")
                    continue

                suffix = ".pdf" if file_url.lower().endswith(".pdf") else ".img"
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp.write(response.content)
                temp.close()
                file_path = temp.name
                temp_files.append(file_path)

            else:
                file_path = file.path

            # Step 2: Detect type
            with open(file_path, "rb") as f:
                header = f.read(4)

            is_pdf = header.startswith(b"%PDF")

            # Step 3: Process PDF
            if is_pdf:
                print("  ✔ PDF detected")
                merger.append(file_path)

            else:
                print("  ✔ Image detected → converting to PDF")

                img = Image.open(file_path)

                # Fix transparency
                if img.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        bg.paste(img, mask=img.split()[3])
                    else:
                        bg.paste(img)
                    img = bg
                else:
                    img = img.convert("RGB")

                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                img.save(temp_pdf.name, "PDF")
                temp_pdf.close()

                merger.append(temp_pdf.name)
                temp_files.append(temp_pdf.name)

        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Step 4: Final PDF
    final_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(final_pdf.name)
    merger.close()

    print(f"✅ Final PDF: {final_pdf.name}")

    # Step 5: Cleanup
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass

    print("========== PDF MERGE END ==========\n")

    return final_pdf.name


# ==================== GENERATE STUDENT PDF ====================

def generate_student_pdf(student):
    """
    Generate a merged PDF for a student by combining:
    - Student photo
    - All certificate files (achievement, internship, courses, sdp, extra, placement, national)
    - Existing student PDF file
    """
    print(f"\n=== GENERATING STUDENT PDF for {student.student_name} (ID: {student.id}) ===")

    files = [
        student.photo,
        student.cert_achieve,
        student.cert_intern,
        student.cert_courses,
        student.cert_sdp,
        student.cert_extra,
        student.cert_placement,
        student.cert_national,
        student.pdf_file  # existing PDF
    ]

    # Debug: Show which files exist
    file_names = [
        'photo', 'cert_achieve', 'cert_intern', 'cert_courses',
        'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national', 'pdf_file'
    ]

    for name, file in zip(file_names, files):
        if file:
            if hasattr(file, 'url'):
                print(f"  - {name}: URL = {file.url}")
            else:
                print(f"  - {name}: {file}")
        else:
            print(f"  - {name}: None")

    final_pdf_path = merge_files(files)

    # Save final PDF path
    student.pdf_url = final_pdf_path
    student.pdf_generated = True
    student.save()

    print(f"PDF saved to student record: {final_pdf_path}")
    print("=== PDF GENERATION COMPLETE ===\n")

    return final_pdf_path


def generate_student_pdf_file(request, student_id):
    import io, shutil
    student = get_object_or_404(Student, id=student_id)
    styles = getSampleStyleSheet()
    temp_files = []

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    main_pdf_path = tmp.name;
    tmp.close()
    temp_files.append(main_pdf_path)

    doc = SimpleDocTemplate(main_pdf_path, pagesize=A4)
    elems = []
    elems.append(Paragraph("""<para alignment='center'>
        <font name='Helvetica-Bold' size='16' color='darkblue'>ANURAG ENGINEERING COLLEGE</font><br/>
        <font name='Helvetica' size='12' color='navy'>DEPARTMENT OF INFORMATION TECHNOLOGY</font><br/><br/>
        <font name='Helvetica-Bold' size='14'>STUDENT PROFILE</font></para>""", styles['Normal']))
    elems.append(Spacer(1, 0.2 * inch))
    elems.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    elems.append(Spacer(1, 0.2 * inch))

    photo_img = None
    photo_url = getattr(student, 'photo_url', None) or (student.photo.url if student.photo else None)
    if photo_url:
        try:
            r = requests.get(photo_url, timeout=10)
            if r.status_code == 200:
                ext = '.png' if 'png' in r.headers.get('content-type', '') else '.jpg'
                tp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                tp.write(r.content);
                tp.close();
                temp_files.append(tp.name)
                photo_img = Image(tp.name, width=1.5 * inch, height=1.8 * inch)
        except Exception:
            pass

    if photo_img:
        ht = Table([[Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']), photo_img]],
                   colWidths=[4.5 * inch, 1.5 * inch])
        ht.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        elems.append(ht)
    else:
        elems.append(Paragraph("<b>STUDENT INFORMATION</b>", styles['Normal']))
    elems.append(Spacer(1, 0.2 * inch))

    fields = [
        ("Hall Ticket No", student.ht_no), ("Name", student.student_name),
        ("Father Name", student.father_name), ("Mother Name", student.mother_name),
        ("Gender", student.gender), ("Date of Birth", student.dob), ("Age", student.age),
        ("Nationality", student.nationality or "Indian"), ("Category", student.category or "N/S"),
        ("Religion", student.religion or "N/S"), ("Blood Group", student.blood_group or "N/S"),
        ("Aadhar Number", student.aadhar), ("APAAR ID", student.apaar_id or "N/S"),
        ("Address", student.address), ("Parent Phone", student.parent_phone),
        ("Student Phone", student.student_phone), ("Email", student.email),
        ("TASK Registered", student.task_registered or "No"),
        ("TASK Username", student.task_username or "N/A"),
        ("CSI Registered", student.csi_registered or "No"),
        ("CSI Membership ID", student.csi_membership_id or "N/A"),
        ("Admission Type", student.admission_type),
        ("Other Admission Details", student.other_admission_details or "N/A"),
        ("EAMCET Rank", student.eamcet_rank or "N/A"),
        ("Year", student.year), ("Semester", student.sem),
        ("SSC Marks (%)", student.ssc_marks or "N/A"),
        ("Intermediate Marks (%)", student.inter_marks or "N/A"),
        ("CGPA", student.cgpa or "N/A"),
        ("RTRP Project Title", student.rtrp_project_title or "N/A"),
        ("Internship Title", student.intern_title or "N/A"),
        ("Final Project Title", student.final_project_title or "N/A"),
        ("Other Training", student.other_training or "N/A"),
    ]
    tbl = Table([[Paragraph(f"<b>{l}</b>", styles['Normal']),
                  Paragraph(str(v) if v else "N/A", styles['Normal'])] for l, v in fields],
                colWidths=[2.2 * inch, 4.3 * inch])
    tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'), ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elems.append(tbl)
    elems.append(Spacer(1, 0.2 * inch))
    elems.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    doc.build(elems)

    writer = PdfWriter()
    try:
        for pg in PdfReader(main_pdf_path).pages: writer.add_page(pg)
    except Exception as e:
        logger.error(f"Error adding main PDF: {e}")

    cert_fields = [
        ('cert_achieve', 'Achievement'), ('cert_intern', 'Internship'),
        ('cert_courses', 'Courses'), ('cert_sdp', 'SDP'),
        ('cert_extra', 'Extracurricular'), ('cert_placement', 'Placement'),
        ('cert_national', 'National Exam'),
    ]
    merged_count = 0
    for fn, fl in cert_fields:
        cf = getattr(student, fn, None)
        if not cf: continue
        try:
            curl = cf.url if hasattr(cf, 'url') else str(cf)
            r = requests.get(curl, timeout=30)
            if r.status_code == 200:
                content = r.content
                if content.startswith(b'%PDF'):
                    tp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    tp.write(content);
                    tp.close();
                    temp_files.append(tp.name)
                    for pg in PdfReader(tp.name).pages: writer.add_page(pg)
                    merged_count += 1
                else:
                    try:
                        img = PILImage.open(io.BytesIO(content))
                        if img.mode != 'RGB': img = img.convert('RGB')
                        tp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        img.save(tp.name, 'PDF', resolution=100.0);
                        tp.close();
                        temp_files.append(tp.name)
                        for pg in PdfReader(tp.name).pages: writer.add_page(pg)
                        merged_count += 1
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error processing {fl}: {e}")

    fp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    final_path = fp.name;
    fp.close();
    temp_files.append(final_path)
    try:
        with open(final_path, "wb") as out:
            writer.write(out)
    except Exception:
        shutil.copy(main_pdf_path, final_path)

    if is_cloudinary_configured():
        try:
            ur = cloudinary.uploader.upload(
                final_path, resource_type="raw", folder="student_generated_pdfs",
                public_id=f"student_{student.ht_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", overwrite=True
            )
            student.pdf_url = ur["secure_url"]
            student.pdf_file = ur["secure_url"]
            student.pdf_generated = True
            student.pdf_generation_time = timezone.now()
            student.save()
            CloudinaryUpload.objects.create(
                student=student, upload_type='pdf',
                cloudinary_url=ur['secure_url'], public_id=ur['public_id'],
                resource_type=ur['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Student'
            )
        except Exception as e:
            logger.error(f"Error uploading student PDF to Cloudinary: {e}")

    try:
        with open(final_path, 'rb') as pf:
            response = HttpResponse(pf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="student_{student.ht_no}.pdf"'
        for t in temp_files:
            try:
                if os.path.exists(t): os.remove(t)
            except Exception:
                pass
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {e}", status=500)


def view_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    url = getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None)
    if url: return redirect(url)
    messages.error(request, "PDF not generated yet.")
    return redirect('dashboard:students_data')


def download_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    url = getattr(student, 'pdf_url', None) or getattr(student, 'pdf_file', None)
    if url: return redirect(url)
    return generate_student_pdf_file(request, student_id)


@login_required
def export_students_csv(request):
    qs = Student.objects.all().order_by('ht_no')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="students_export_{date.today().strftime("%Y%m%d")}.csv"'
    )
    w = csv.writer(response)
    w.writerow(['HT No', 'Student Name', 'Father Name', 'Mother Name', 'Gender', 'Date of Birth', 'Age',
                'Category', 'Religion', 'Blood Group', 'Aadhar', 'APAAR ID', 'Address',
                'Parent Phone', 'Student Phone', 'Email', 'Year', 'Semester', 'Branch', 'Roll Number',
                'SSC Marks', 'Inter Marks', 'CGPA', 'Admission Type', 'EAMCET Rank',
                'RTRP Project Title', 'Internship Title', 'Final Project Title', 'Created Date'])
    for s in qs:
        w.writerow([
            s.ht_no, s.student_name, s.father_name, s.mother_name, s.gender,
            s.dob.strftime('%d-%m-%Y') if s.dob else '',
            s.age, s.category, s.religion or '', s.blood_group or '',
                               s.aadhar or '', s.apaar_id or '', s.address,
            s.parent_phone, s.student_phone, s.email,
            s.year, s.sem,
                               getattr(s, 'branch', '') or '', getattr(s, 'roll_number', '') or '',
            s.ssc_marks, s.inter_marks, s.cgpa,
                               s.admission_type or '', s.eamcet_rank or '',
                               s.rtrp_project_title or '', s.intern_title or '', s.final_project_title or '',
            s.created_at.strftime('%d-%m-%Y %H:%M:%S') if s.created_at else '',
        ])
    FacultyLog.objects.create(
        faculty=None, action='Students CSV Export',
        details=f'Exported {qs.count()} students to CSV',
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    return response


# ==================== GENERATE FACULTY PDF ====================

@login_required
def generate_faculty_pdf(request, faculty_id):
    """Generate PDF for a faculty member with ALL documents merged (identity + education certificates)."""
    import io
    import shutil

    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        print(f"\n{'=' * 60}")
        print(f"GENERATING FACULTY PDF FOR: {faculty.staff_name}")
        print(f"Employee Code: {faculty.employee_code}")
        print(f"{'=' * 60}")

        # Debug print to verify all fields have data
        print("\n--- FACULTY DATA CHECK ---")
        print(f"Caste: {faculty.caste}")
        print(f"Sub-Caste: {faculty.sub_caste}")
        print(f"Nationality: {faculty.nationality}")
        print(f"JNTUH ID: {faculty.jntuh_id}")
        print(f"AICTE ID: {faculty.aicte_id}")
        print(f"PAN: {faculty.pan}")
        print(f"Aadhar: {faculty.aadhar}")
        print(f"APAAR ID: {faculty.apaar_id}")
        print(f"ORCID ID: {faculty.orcid_id}")
        print(f"SSC Year: {faculty.ssc_year}")
        print(f"SSC Percent: {faculty.ssc_percent}")
        print(f"SSC School: {faculty.ssc_school}")
        print(f"Inter Year: {faculty.inter_year}")
        print(f"Inter Percent: {faculty.inter_percent}")
        print(f"Inter College: {faculty.inter_college}")
        print(f"UG Degree: {faculty.ug_degree}")
        print(f"UG Year: {faculty.ug_year}")
        print(f"UG Percentage: {faculty.ug_percentage}")
        print(f"UG College: {faculty.ug_college}")
        print(f"UG Spec: {faculty.ug_spec}")
        print(f"PG Degree: {faculty.pg_degree}")
        print(f"PG Year: {faculty.pg_year}")
        print(f"PG Percentage: {faculty.pg_percentage}")
        print(f"PG College: {faculty.pg_college}")
        print(f"PG Spec: {faculty.pg_spec}")
        print(f"PhD Status: {faculty.phd_degree}")
        print(f"PhD Year: {faculty.phd_year}")
        print(f"PhD University: {faculty.phd_university}")
        print(f"PhD Spec: {faculty.phd_spec}")
        print(f"Subjects Dealt: {faculty.subjects_dealt}")
        print(f"SCM: {faculty.scm}")
        print(f"About: {faculty.about_yourself}")
        print(f"Results: {faculty.results}")
        print(f"Has Aadhar File: {bool(faculty.aadhar_file)}")
        print(f"Has PAN File: {bool(faculty.pan_file)}")
        print(f"Has APAAR File: {bool(faculty.apaar_file)}")
        print(f"Has SCM File: {bool(faculty.scm_file)}")
        print(f"Has SSC Certificate: {bool(faculty.ssc_certificate)}")
        print(f"Has Inter Certificate: {bool(faculty.inter_certificate)}")
        print(f"Has UG Certificate: {bool(faculty.ug_certificate)}")
        print(f"Has PG Certificate: {bool(faculty.pg_certificate)}")
        print(f"Has PhD Certificate: {bool(faculty.phd_certificate)}")
        print("---------------------------\n")

        merger = PdfMerger()
        temp_files = []

        # ---- 1. CALCULATE EXPERIENCE ----
        experience = "N/A"
        if faculty.joining_date:
            today = date.today()
            j = faculty.joining_date
            yrs = today.year - j.year
            mths = today.month - j.month
            dys = today.day - j.day

            if dys < 0:
                mths -= 1
                pm = today.month - 1 or 12
                py = today.year - (1 if today.month == 1 else 0)
                dim = (30 if pm in [4, 6, 9, 11]
                       else 29 if pm == 2 and ((py % 4 == 0 and py % 100 != 0) or py % 400 == 0)
                else 28 if pm == 2
                else 31)
                dys += dim
            if mths < 0:
                yrs -= 1
                mths += 12
            experience = f"{yrs} Years {mths} Months {dys} Days"
            print(f"Experience: {experience}")

        # ---- 2. DOWNLOAD PHOTO ----
        temp_photo_path = None
        photo_url = None
        try:
            photo_url = faculty.photo.url if faculty.photo else None
        except Exception:
            photo_url = None
        if not photo_url:
            photo_url = getattr(faculty, 'cloudinary_photo_url', None)

        if photo_url:
            try:
                r = requests.get(photo_url, timeout=15)
                if r.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tp:
                        tp.write(r.content)
                        temp_photo_path = tp.name
                    temp_files.append(temp_photo_path)
                    print(f"Photo downloaded: {temp_photo_path}")
            except Exception as e:
                print(f"Photo download error: {e}")

        # ---- 3. GET RELATED DATA ----
        certificates = Certificate.objects.filter(faculty=faculty)
        research_projects = ResearchProject.objects.filter(faculty=faculty)
        try:
            profile = FacultyProfile.objects.get(faculty=faculty)
        except FacultyProfile.DoesNotExist:
            profile = None

        subjects_list = []
        sd = getattr(faculty, 'subjects_dealt', None)
        if sd:
            subjects_list = [s.strip() for s in sd.split(',') if s.strip()]

        # ---- 4. BUILD CONTEXT ----
        context = {
            'faculty': faculty,
            'profile': profile,
            'research_projects': research_projects,
            'certificates': certificates,
            'subjects_list': subjects_list,
            'experience': experience,
            'current_date': datetime.now(),
            'local_photo_path': temp_photo_path,
            # Personal Information
            'staff_name': faculty.staff_name,
            'employee_code': faculty.employee_code,
            'father_name': faculty.father_name,
            'mother_name': faculty.mother_name,
            'dob': faculty.dob,
            'gender': faculty.gender,
            'state': faculty.state,
            'caste': faculty.caste,
            'sub_caste': faculty.sub_caste,
            'nationality': faculty.nationality,
            'address': faculty.address,
            # Professional Information
            'department': faculty.department,
            'designation': faculty.designation,
            'joining_date': faculty.joining_date,
            'email': faculty.email,
            'mobile': faculty.mobile,
            'phone': faculty.phone,
            # Professional IDs
            'jntuh_id': faculty.jntuh_id,
            'aicte_id': faculty.aicte_id,
            'pan': faculty.pan,
            'aadhar': faculty.aadhar,
            'apaar_id': faculty.apaar_id,
            'orcid_id': faculty.orcid_id,
            # Educational Qualifications
            'ssc_year': faculty.ssc_year,
            'ssc_percent': faculty.ssc_percent,
            'ssc_school': faculty.ssc_school,
            'inter_year': faculty.inter_year,
            'inter_percent': faculty.inter_percent,
            'inter_college': faculty.inter_college,
            'ug_degree': faculty.ug_degree,
            'ug_year': faculty.ug_year,
            'ug_percentage': faculty.ug_percentage,
            'ug_college': faculty.ug_college,
            'ug_spec': faculty.ug_spec,
            'pg_degree': faculty.pg_degree,
            'pg_year': faculty.pg_year,
            'pg_percentage': faculty.pg_percentage,
            'pg_college': faculty.pg_college,
            'pg_spec': faculty.pg_spec,
            'phd_degree': faculty.phd_degree,
            'phd_year': faculty.phd_year,
            'phd_university': faculty.phd_university,
            'phd_spec': faculty.phd_spec,
            # Additional Information
            'subjects_dealt': faculty.subjects_dealt,
            'about_yourself': faculty.about_yourself,
            'results': faculty.results,
            'scm': faculty.scm,
            # Document flags
            'has_aadhar': bool(faculty.aadhar_file),
            'has_pan': bool(faculty.pan_file),
            'has_apaar': bool(faculty.apaar_file),
            'has_scm': bool(faculty.scm_file),
            'has_ssc_cert': bool(faculty.ssc_certificate),
            'has_inter_cert': bool(faculty.inter_certificate),
            'has_ug_cert': bool(faculty.ug_certificate),
            'has_pg_cert': bool(faculty.pg_certificate),
            'has_phd_cert': bool(faculty.phd_certificate),
        }

        # ---- 5. GENERATE MAIN PROFILE PDF ----
        print("Generating main profile PDF...")
        html_string = render_to_string('dashboard/faculty_pdf.html', context)
        main_pdf_path = None

        # Try pdfkit first (works on Windows with wkhtmltopdf)
        if pdfkit is not None:
            try:
                opts = {
                    'page-size': 'A4',
                    'margin-top': '15mm', 'margin-right': '15mm',
                    'margin-bottom': '15mm', 'margin-left': '15mm',
                    'encoding': 'UTF-8', 'enable-local-file-access': '', 'quiet': ''
                }
                wk = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
                cfg = pdfkit.configuration(wkhtmltopdf=wk) if os.path.exists(wk) else pdfkit.configuration()
                pdf_bytes = pdfkit.from_string(html_string, False, options=opts, configuration=cfg)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tm:
                    tm.write(pdf_bytes)
                    main_pdf_path = tm.name
                temp_files.append(main_pdf_path)
                print(f"Main PDF (pdfkit): {main_pdf_path}")
            except Exception as e:
                print(f"pdfkit failed ({e}), using ReportLab fallback.")
                main_pdf_path = None

        # ReportLab fallback (works on Render/Linux)
        if main_pdf_path is None:
            tm = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            main_pdf_path = tm.name
            tm.close()
            temp_files.append(main_pdf_path)

            s = getSampleStyleSheet()
            hs = ParagraphStyle('h', fontSize=16, fontName='Helvetica-Bold',
                                textColor=colors.darkblue, alignment=1)
            ts = ParagraphStyle('t', fontSize=14, alignment=1)
            docrl = SimpleDocTemplate(
                main_pdf_path, pagesize=A4,
                topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                leftMargin=0.75 * inch, rightMargin=0.75 * inch
            )
            el = []
            el.append(Paragraph("ANURAG ENGINEERING COLLEGE", hs))
            el.append(Spacer(1, 0.1 * inch))
            el.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
            el.append(Spacer(1, 0.1 * inch))
            el.append(Paragraph("FACULTY PROFILE", ts))
            el.append(Spacer(1, 0.2 * inch))

            # Photo in header if available
            if temp_photo_path:
                try:
                    photo_rl = Image(temp_photo_path, width=1.2 * inch, height=1.4 * inch)
                    hdr = Table(
                        [[Paragraph(
                            f"<b>{faculty.staff_name}</b><br/>{faculty.designation}<br/>{faculty.department}",
                            s['Normal']), photo_rl]],
                        colWidths=[5 * inch, 1.5 * inch]
                    )
                    hdr.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ]))
                    el.append(hdr)
                except Exception:
                    el.append(Paragraph(f"<b>{faculty.staff_name}</b>", s['Normal']))
            else:
                el.append(Paragraph(f"<b>{faculty.staff_name}</b>", s['Normal']))
            el.append(Spacer(1, 0.2 * inch))

            # Info table rows
            rows = [
                ("Employee Code", faculty.employee_code),
                ("Department", faculty.department),
                ("Designation", faculty.designation),
                ("Email", faculty.email),
                ("Mobile", faculty.mobile),
                ("Gender", faculty.gender),
                ("Date of Birth", faculty.dob.strftime('%d-%m-%Y') if faculty.dob else "N/A"),
                ("Father's Name", faculty.father_name or "N/A"),
                ("Mother's Name", faculty.mother_name or "N/A"),
                ("State", faculty.state or "N/A"),
                ("Caste", faculty.caste or "N/A"),
                ("Sub-Caste", faculty.sub_caste or "N/A"),
                ("Nationality", faculty.nationality or "N/A"),
                ("Address", faculty.address or "N/A"),
                ("Joining Date", faculty.joining_date.strftime('%d-%m-%Y') if faculty.joining_date else "N/A"),
                ("Total Experience", experience),
                ("Status", "Active" if faculty.is_active else "Inactive"),
                ("JNTUH ID", faculty.jntuh_id or "N/A"),
                ("AICTE ID", faculty.aicte_id or "N/A"),
                ("PAN Number", faculty.pan or "N/A"),
                ("Aadhar Number", faculty.aadhar or "N/A"),
                ("APAAR ID", faculty.apaar_id or "N/A"),
                ("ORCID ID", faculty.orcid_id or "N/A"),
                ("SSC Year", str(faculty.ssc_year or "N/A")),
                ("SSC %", str(faculty.ssc_percent or "N/A")),
                ("SSC School", faculty.ssc_school or "N/A"),
                ("Inter Year", str(faculty.inter_year or "N/A")),
                ("Inter %", str(faculty.inter_percent or "N/A")),
                ("Inter College", faculty.inter_college or "N/A"),
                ("UG Degree", faculty.ug_degree or "N/A"),
                ("UG Year", str(faculty.ug_year or "N/A")),
                ("UG %", str(faculty.ug_percentage or "N/A")),
                ("UG College", faculty.ug_college or "N/A"),
                ("UG Specialization", faculty.ug_spec or "N/A"),
                ("PG Degree", faculty.pg_degree or "N/A"),
                ("PG Year", str(faculty.pg_year or "N/A")),
                ("PG %", str(faculty.pg_percentage or "N/A")),
                ("PG College", faculty.pg_college or "N/A"),
                ("PG Specialization", faculty.pg_spec or "N/A"),
                ("PhD Status", faculty.phd_degree or "N/A"),
                ("PhD Year", str(faculty.phd_year or "N/A")),
                ("PhD University", faculty.phd_university or "N/A"),
                ("PhD Specialization", faculty.phd_spec or "N/A"),
                ("Subjects Dealt", faculty.subjects_dealt or "N/A"),
                ("About / Research", faculty.about_yourself or "N/A"),
                ("Results", faculty.results or "N/A"),
                ("SCM Details", faculty.scm or "N/A"),
                ("Aadhar Document", "Uploaded" if bool(faculty.aadhar_file) else "Not Uploaded"),
                ("PAN Document", "Uploaded" if bool(faculty.pan_file) else "Not Uploaded"),
                ("APAAR Document", "Uploaded" if bool(faculty.apaar_file) else "Not Uploaded"),
                ("SCM Document", "Uploaded" if bool(faculty.scm_file) else "Not Uploaded"),
            ]

            td = [
                [Paragraph(f"<b>{l}</b>", s['Normal']),
                 Paragraph(str(v) if v else "N/A", s['Normal'])]
                for l, v in rows
            ]
            tbl = Table(td, colWidths=[2.2 * inch, 4.3 * inch])
            tbl.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            el.append(tbl)

            # Research projects table
            if research_projects:
                el.append(Spacer(1, 0.2 * inch))
                el.append(Paragraph("<b>RESEARCH PROJECTS</b>",
                                    ParagraphStyle('rh', fontSize=12, fontName='Helvetica-Bold')))
                el.append(Spacer(1, 0.1 * inch))
                rp_data = [['Type', 'Title', 'Journal/Publisher', 'DOI/ISSN']]
                for rp in research_projects:
                    rp_data.append([
                        rp.research_type or '',
                        rp.title_of_project or '',
                        (rp.journal_name or rp.publisher_name or ''),
                        (rp.doi or rp.issn_number or '')
                    ])
                rp_tbl = Table(rp_data, colWidths=[1.2 * inch, 2.5 * inch, 2 * inch, 1 * inch])
                rp_tbl.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('PADDING', (0, 0), (-1, -1), 4),
                ]))
                el.append(rp_tbl)

            el.append(Spacer(1, 0.2 * inch))
            el.append(Paragraph(
                f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                s['Normal']
            ))
            docrl.build(el)
            print(f"Main PDF (ReportLab): {main_pdf_path}")

        # Add main profile PDF to merger
        merger.append(main_pdf_path)
        print("Added main PDF to merger.")

        # ---- 6. MERGE ALL FACULTY DOCUMENTS ----
        # KEY FIX: Now includes aadhar_file, pan_file, apaar_file, scm_file
        # in addition to education certificates - same image/PDF handling as student PDF
        all_doc_fields = [
            # Identity / KYC Documents
            ('aadhar_file', 'Aadhar Card'),
            ('pan_file', 'PAN Card'),
            ('apaar_file', 'APAAR Document'),
            ('scm_file', 'SCM Document'),
            # Education Certificates
            ('ssc_certificate', 'SSC Certificate'),
            ('inter_certificate', 'Intermediate Certificate'),
            ('ug_certificate', 'UG Certificate'),
            ('pg_certificate', 'PG Certificate'),
            ('phd_certificate', 'PhD Certificate'),
        ]

        cert_count = 0
        for field_name, field_label in all_doc_fields:
            doc_field = getattr(faculty, field_name, None)

            if not doc_field:
                print(f"  [SKIP] {field_label}: not uploaded")
                continue

            try:
                doc_url = doc_field.url if hasattr(doc_field, 'url') else str(doc_field)
            except Exception as e:
                print(f"  [SKIP] {field_label}: cannot get URL ({e})")
                continue

            print(f"Processing {field_label}: {doc_url}")

            try:
                r = requests.get(doc_url, timeout=30)
                if r.status_code != 200:
                    print(f"  [ERROR] HTTP {r.status_code}")
                    continue

                content = r.content

                # Case 1: PDF file
                if content.startswith(b'%PDF'):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tc:
                        tc.write(content)
                        tc_path = tc.name
                    temp_files.append(tc_path)
                    merger.append(tc_path)
                    cert_count += 1
                    print(f"  [OK] Added PDF: {field_label}")

                # Case 2: Image file -> convert to PDF
                else:
                    try:
                        import io as _io
                        img = PILImage.open(_io.BytesIO(content))
                        print(f"  Image detected: {img.format} {img.size}")

                        # Handle transparency (RGBA/P/LA)
                        if img.mode in ('RGBA', 'P', 'LA'):
                            bg = PILImage.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                bg.paste(img, mask=img.split()[3])
                            else:
                                bg.paste(img)
                            img = bg
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as ti:
                            ti_path = ti.name
                        img.save(ti_path, 'PDF', resolution=150.0)
                        temp_files.append(ti_path)
                        merger.append(ti_path)
                        cert_count += 1
                        print(f"  [OK] Converted image to PDF: {field_label}")

                    except Exception as img_error:
                        print(f"  [ERROR] Cannot process as image: {img_error}")

            except Exception as e:
                print(f"  [ERROR] Processing {field_label}: {e}")

        # Also merge Certificate model records (from certificate management)
        for cert in certificates:
            cert_label = f"Certificate: {cert.certificate_type}"
            cert_url = None

            if cert.certificate_file:
                try:
                    cert_url = cert.certificate_file.url
                except Exception:
                    pass
            elif cert.cloudinary_url:
                cert_url = cert.cloudinary_url

            if not cert_url:
                continue

            try:
                r = requests.get(cert_url, timeout=30)
                if r.status_code != 200:
                    continue

                content = r.content
                if content.startswith(b'%PDF'):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tc:
                        tc.write(content)
                        tc_path = tc.name
                    temp_files.append(tc_path)
                    merger.append(tc_path)
                    cert_count += 1
                    print(f"  [OK] Added Certificate record PDF: {cert_label}")
                else:
                    try:
                        import io as _io
                        img = PILImage.open(_io.BytesIO(content))
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as ti:
                            ti_path = ti.name
                        img.save(ti_path, 'PDF', resolution=150.0)
                        temp_files.append(ti_path)
                        merger.append(ti_path)
                        cert_count += 1
                        print(f"  [OK] Converted Certificate record image: {cert_label}")
                    except Exception:
                        pass
            except Exception as e:
                print(f"  [ERROR] Certificate record {cert_label}: {e}")

        print(f"Total documents merged: {cert_count}")

        # ---- 7. SAVE FINAL MERGED PDF ----
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as ot:
            merger.write(ot.name)
            final_pdf_path = ot.name
        temp_files.append(final_pdf_path)
        merger.close()
        print(f"Final merged PDF: {final_pdf_path}")

        # ---- 8. UPLOAD TO CLOUDINARY ----
        if is_cloudinary_configured():
            try:
                ur = cloudinary.uploader.upload(
                    final_pdf_path,
                    resource_type="raw",
                    folder="faculty_generated_pdfs",
                    public_id=f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}",
                    overwrite=True
                )
                faculty.cloudinary_pdf_url = ur["secure_url"]
                faculty.save()
                print(f"Uploaded to Cloudinary: {ur['secure_url']}")
                CloudinaryUpload.objects.create(
                    faculty=faculty,
                    upload_type='pdf',
                    cloudinary_url=ur['secure_url'],
                    public_id=ur['public_id'],
                    resource_type=ur['resource_type'],
                    uploaded_by=request.user.username if request.user.is_authenticated else 'System'
                )
            except Exception as e:
                print(f"Cloudinary upload error: {e}")

        # ---- 9. RETURN PDF ----
        with open(final_pdf_path, 'rb') as pf:
            response = HttpResponse(pf.read(), content_type='application/pdf')
            fname = f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{fname}"'

        # ---- 10. CLEANUP ----
        for tmp in temp_files:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
                    print(f"Cleaned: {tmp}")
            except Exception:
                pass

        FacultyLog.objects.create(
            faculty=faculty,
            action='PDF Generated',
            details=f'PDF generated for {faculty.employee_code} with {cert_count} documents merged',
            performed_by=request.user.username if request.user.is_authenticated else 'Anonymous',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        print(f"{'=' * 60}\nPDF GENERATION COMPLETE - {cert_count} docs merged\n{'=' * 60}")
        return response

    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error generating faculty PDF: {e}')
        return redirect('dashboard:faculty_dashboard')


def generate_pdf_with_data(request):
    if request.method == 'POST':
        if pdfkit is None:
            return JsonResponse({'success': False, 'error': 'pdfkit not installed'})
        try:
            html_string = render_to_string('faculty/custom_pdf_template.html', {'data': request.POST.dict()})
            opts = {'page-size': 'A4', 'margin-top': '0.5in', 'margin-right': '0.5in',
                    'margin-bottom': '0.5in', 'margin-left': '0.5in', 'encoding': 'UTF-8'}
            wk = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            cfg = pdfkit.configuration(wkhtmltopdf=wk)
            pdf = pdfkit.from_string(html_string, False, options=opts, configuration=cfg)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_document.pdf"'
            return response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'faculty/generate_pdf_form.html')


@login_required
def preview_faculty_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if faculty.cloudinary_pdf_url:
        return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url, 'message': 'PDF on Cloudinary'})
    if faculty.pdf_document and faculty.pdf_document.url:
        return JsonResponse({'success': True, 'pdf_url': faculty.pdf_document.url, 'message': 'Local PDF available'})
    return JsonResponse({'success': False, 'error': 'No PDF available. Please generate one first.'})


def preview_pdf_template(request):
    return render(request, 'faculty/pdf_preview.html')


@login_required
def download_faculty_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if faculty.cloudinary_pdf_url:
        return redirect(faculty.cloudinary_pdf_url)
    if faculty.pdf_document and faculty.pdf_document.url:
        response = HttpResponse(faculty.pdf_document, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="faculty_{faculty.employee_code}.pdf"'
        return response
    return generate_faculty_pdf(request, faculty_id)


@login_required
def bulk_generate_faculty_pdfs(request):
    if request.method != 'POST':
        return redirect('dashboard:faculty_list')
    faculty_ids = request.POST.getlist('faculty_ids')
    if not faculty_ids:
        messages.error(request, "No faculty selected.")
        return redirect('dashboard:faculty_list')
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f'faculty_pdfs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for fid in faculty_ids:
                try:
                    fac = Faculty.objects.get(id=fid)
                    exp = calculate_experience(fac.joining_date) if fac.joining_date else "N/A"
                    ctx = {'faculty': fac, 'experience': exp, 'current_date': datetime.now(), 'pdf_mode': True}
                    html = render_to_string('dashboard/faculty_pdf.html', ctx)
                    if pdfkit is not None:
                        opts = {'page-size': 'A4', 'margin-top': '20mm', 'margin-right': '20mm',
                                'margin-bottom': '20mm', 'margin-left': '20mm', 'encoding': 'UTF-8'}
                        wk = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
                        cfg = pdfkit.configuration(wkhtmltopdf=wk)
                        pdf = pdfkit.from_string(html, False, options=opts, configuration=cfg)
                        pname = f"faculty_{fac.employee_code}.pdf"
                        pp = os.path.join(temp_dir, pname)
                        with open(pp, 'wb') as f: f.write(pdf)
                        zipf.write(pp, pname)
                        os.remove(pp)
                except Exception as e:
                    logger.error(f"Error generating PDF for faculty {fid}: {e}")
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        response = HttpResponse(zip_data, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="faculty_pdfs_{datetime.now().strftime("%Y%m%d")}.zip"'
        if os.path.exists(zip_path): os.remove(zip_path)
        try:
            os.rmdir(temp_dir)
        except Exception:
            pass
        FacultyLog.objects.create(
            faculty=None, action='Bulk Faculty PDFs Generated',
            details=f'PDFs generated for {len(faculty_ids)} faculty members',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        return response
    except Exception as e:
        logger.error(f"Bulk PDF error: {e}")
        messages.error(request, f"Error generating PDFs: {e}")
    return redirect('dashboard:faculty_list')


# ==================== CLOUDINARY MANAGEMENT ====================

@login_required
@csrf_exempt
def upload_faculty_to_cloudinary(request, faculty_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    try:
        faculty = get_object_or_404(Faculty, id=faculty_id)
        if not is_cloudinary_configured():
            return JsonResponse({'success': False, 'error': 'Cloudinary not configured.'})
        if faculty.cloudinary_pdf_url:
            return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url,
                                 'message': 'PDF already exists on Cloudinary'})
        pdf_resp = generate_faculty_pdf(request, faculty_id)
        if not isinstance(pdf_resp, HttpResponse):
            return JsonResponse({'success': False, 'error': 'Failed to generate PDF'})
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
            tf.write(pdf_resp.content);
            tfp = tf.name
        cr = cloudinary.uploader.upload(
            tfp, resource_type="raw", folder="faculty_pdfs",
            public_id=f"faculty_{faculty.employee_code}_{date.today().strftime('%Y%m%d')}",
            overwrite=True, tags=[f"faculty_{faculty.employee_code}", faculty.department, "pdf"]
        )
        faculty.cloudinary_pdf_url = cr['secure_url'];
        faculty.save()
        CloudinaryUpload.objects.create(
            faculty=faculty, upload_type='pdf', cloudinary_url=cr['secure_url'],
            public_id=cr['public_id'], resource_type=cr['resource_type'], uploaded_by=request.user.username
        )
        os.unlink(tfp)
        FacultyLog.objects.create(
            faculty=faculty, action='PDF Uploaded to Cloudinary',
            details=f'PDF uploaded: {faculty.employee_code}',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url,
                             'public_id': cr['public_id'], 'message': 'Uploaded successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def upload_faculty_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            faculty = get_object_or_404(Faculty, employee_code=request.POST.get('employee_code'))
            if not is_cloudinary_configured():
                return JsonResponse({'success': False, 'error': 'Cloudinary not configured.'})
            cr = cloudinary.uploader.upload(
                request.FILES['photo'], folder="faculty_photos",
                public_id=f"faculty_{faculty.employee_code}", overwrite=True,
                transformation=[{'width': 300, 'height': 300, 'crop': 'fill'}, {'quality': 'auto:good'}]
            )
            faculty.cloudinary_photo_url = cr['secure_url'];
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type='photo', cloudinary_url=cr['secure_url'],
                public_id=cr['public_id'], resource_type=cr['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )
            return JsonResponse({'success': True, 'photo_url': faculty.cloudinary_photo_url,
                                 'message': 'Photo uploaded successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'No photo file provided'})


@csrf_exempt
def upload_faculty_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        try:
            faculty = get_object_or_404(Faculty, employee_code=request.POST.get('employee_code'))
            if not is_cloudinary_configured():
                return JsonResponse({'success': False, 'error': 'Cloudinary not configured.'})
            cr = cloudinary.uploader.upload(
                request.FILES['pdf_file'], resource_type="raw", folder="faculty_pdfs",
                public_id=f"faculty_{faculty.employee_code}", overwrite=True
            )
            faculty.cloudinary_pdf_url = cr['secure_url'];
            faculty.save()
            CloudinaryUpload.objects.create(
                faculty=faculty, upload_type='pdf', cloudinary_url=cr['secure_url'],
                public_id=cr['public_id'], resource_type=cr['resource_type'],
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )
            return JsonResponse({'success': True, 'pdf_url': faculty.cloudinary_pdf_url,
                                 'message': 'PDF uploaded successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'No PDF file provided'})


@login_required
def cloudinary_status(request):
    try:
        if not is_cloudinary_configured():
            return render(request, 'cloudinary/status.html', {
                'title': 'Cloudinary Status', 'connected': False,
                'error': 'Cloudinary credentials not configured.',
                'cloudinary_config': {
                    'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                    'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                    'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
                }
            })
        result = cloudinary.api.ping()
        usage = cloudinary.api.usage()
        recent_uploads = CloudinaryUpload.objects.select_related('faculty', 'student').order_by('-upload_date')[:10]
        total_faculty = Faculty.objects.count()
        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status', 'connected': result.get('status') == 'ok',
            'usage': usage,
            'uploaded_count': CloudinaryUpload.objects.count(),
            'faculty_with_pdf': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(
                cloudinary_pdf_url='').count(),
            'faculty_with_photo': Faculty.objects.exclude(cloudinary_photo_url__isnull=True).exclude(
                cloudinary_photo_url='').count(),
            'total_faculty': total_faculty, 'recent_uploads': recent_uploads,
            'cloudinary_config': {
                'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
            }
        })
    except Exception as e:
        return render(request, 'cloudinary/status.html', {
            'title': 'Cloudinary Status', 'connected': False, 'error': str(e),
            'cloudinary_config': {
                'cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'Not configured'),
                'api_key_exists': bool(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                'api_secret_exists': bool(getattr(settings, 'CLOUDINARY_API_SECRET', None)),
            }
        })


@login_required
def get_cloudinary_url(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    return JsonResponse({
        'pdf_url': faculty.cloudinary_pdf_url,
        'photo_url': faculty.cloudinary_photo_url,
        'employee_code': faculty.employee_code,
        'has_pdf': bool(faculty.cloudinary_pdf_url),
        'has_photo': bool(faculty.cloudinary_photo_url),
    })


@login_required
def bulk_sync_to_cloudinary(request):
    if request.method != 'POST':
        return redirect('dashboard:faculty_list')
    faculty_ids = request.POST.getlist('faculty_ids')
    if not faculty_ids:
        messages.error(request, "No faculty selected.")
        return redirect('dashboard:faculty_list')
    if not is_cloudinary_configured():
        messages.error(request, "Cloudinary not configured.")
        return redirect('dashboard:faculty_list')
    ok = err = 0
    for fid in faculty_ids:
        try:
            fac = Faculty.objects.get(id=fid)
            if fac.photo and not fac.cloudinary_photo_url:
                try:
                    with fac.photo.open('rb') as pf:
                        cr = cloudinary.uploader.upload(pf, folder="faculty_photos",
                                                        public_id=f"faculty_{fac.employee_code}", overwrite=True)
                        fac.cloudinary_photo_url = cr['secure_url'];
                        fac.save()
                        CloudinaryUpload.objects.create(
                            faculty=fac, upload_type='photo', cloudinary_url=cr['secure_url'],
                            public_id=cr['public_id'], resource_type=cr['resource_type'],
                            uploaded_by=request.user.username
                        )
                except Exception as e:
                    logger.error(f"Photo sync error for {fid}: {e}")
            ok += 1
        except Exception as e:
            logger.error(f"Sync error for {fid}: {e}");
            err += 1
    FacultyLog.objects.create(
        faculty=None, action='Bulk Cloudinary Sync',
        details=f'Synced {ok} faculty ({err} errors)',
        performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
    )
    if ok:  messages.success(request, f"Synced {ok} faculty to Cloudinary.")
    if err: messages.warning(request, f"Failed to sync {err} faculty.")
    return redirect('dashboard:faculty_list')


# ==================== CERTIFICATE MANAGEMENT ====================

@login_required
def upload_certificate(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.faculty = faculty
            if 'certificate_file' in request.FILES and is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES['certificate_file'], resource_type="raw",
                        folder=f"certificates/{faculty.employee_code}",
                        public_id=f"cert_{cert.certificate_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=False
                    )
                    cert.cloudinary_url = cr['secure_url']
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type='certificate',
                        cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                        resource_type=cr['resource_type'], uploaded_by=request.user.username
                    )
                    messages.success(request, 'Certificate uploaded to Cloudinary!')
                except Exception as e:
                    logger.error(f"Certificate Cloudinary error: {e}")
                    messages.warning(request, 'Certificate saved locally but Cloudinary upload failed.')
            cert.save()
            FacultyLog.objects.create(
                faculty=faculty, action='Certificate Uploaded',
                details=f'Certificate uploaded: {cert.certificate_type}',
                performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Certificate uploaded successfully!')
            return redirect('dashboard:view_certificates', faculty_id=faculty_id)
    else:
        form = CertificateForm()
    return render(request, 'dashboard/certificate_upload.html', {
        'title': f'Upload Certificate - {faculty.staff_name}', 'form': form, 'faculty': faculty
    })


@login_required
def upload_certificates_bulk(request):
    if request.method == 'POST' and request.FILES.getlist('certificate_files'):
        faculty = get_object_or_404(Faculty, employee_code=request.POST.get('employee_code'))
        files = request.FILES.getlist('certificate_files')
        ok = err = 0
        for cf in files:
            try:
                ct = os.path.splitext(cf.name)[0].replace('_', ' ').replace('-', ' ').title() or "Certificate"
                curl = None
                if is_cloudinary_configured():
                    try:
                        cr = cloudinary.uploader.upload(
                            cf, resource_type="raw", folder=f"certificates/{faculty.employee_code}",
                            public_id=f"cert_{ct.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            overwrite=False
                        )
                        curl = cr['secure_url']
                    except Exception as e:
                        logger.error(f"Cloudinary upload error: {e}")
                Certificate.objects.create(
                    faculty=faculty, certificate_type=ct, certificate_file=cf,
                    cloudinary_url=curl, issued_by='Unknown', issue_date=date.today(),
                    description=f'Uploaded bulk on {date.today().strftime("%Y-%m-%d")}'
                )
                ok += 1
            except Exception as e:
                logger.error(f"Error uploading {cf.name}: {e}");
                err += 1
        FacultyLog.objects.create(
            faculty=faculty, action='Bulk Certificates Uploaded',
            details=f'{ok} certs uploaded ({err} failed)',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        if ok:  messages.success(request, f'{ok} certificates uploaded!')
        if err: messages.warning(request, f'{err} certificates failed.')
        return redirect('dashboard:view_certificates', faculty_id=faculty.id)
    return render(request, 'certificates/bulk_upload.html', {'title': 'Bulk Upload Certificates'})


@login_required
def view_certificates(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certs = Certificate.objects.filter(faculty=faculty).order_by('-issue_date')
    return render(request, 'dashboard/certificate_list.html', {
        'title': f'Certificates - {faculty.staff_name}',
        'faculty': faculty, 'certificates': certs,
        'cert_stats': {
            'total': certs.count(),
            'by_type': certs.values('certificate_type').annotate(count=Count('id')).order_by('-count'),
            'has_cloudinary': certs.exclude(cloudinary_url__isnull=True).exclude(cloudinary_url='').count(),
        }
    })


@login_required
def delete_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    fid = cert.faculty.id
    if request.method == 'POST':
        if cert.cloudinary_url and is_cloudinary_configured():
            try:
                pid = cert.cloudinary_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(pid, resource_type="raw")
            except Exception as e:
                logger.error(f"Cloudinary delete error: {e}")
        ct = cert.certificate_type
        cert.delete()
        messages.success(request, 'Certificate deleted successfully!')
        FacultyLog.objects.create(
            faculty=cert.faculty, action='Certificate Deleted',
            details=f'Certificate deleted: {ct}',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard:view_certificates', faculty_id=fid)
    return render(request, 'dashboard/certificate_confirm_delete.html', {
        'title': 'Delete Certificate', 'certificate': cert
    })


@login_required
def edit_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    fid = cert.faculty.id
    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=cert)
        if form.is_valid():
            old_type = cert.certificate_type
            if 'certificate_file' in request.FILES and is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        request.FILES['certificate_file'], resource_type="raw",
                        folder=f"certificates/{cert.faculty.employee_code}",
                        public_id=f"cert_{cert.certificate_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=True
                    )
                    cert.cloudinary_url = cr['secure_url']
                except Exception as e:
                    logger.error(f"Cloudinary error editing cert: {e}")
            form.save()
            FacultyLog.objects.create(
                faculty=cert.faculty, action='Certificate Edited',
                details=f'Certificate edited: {old_type} -> {cert.certificate_type}',
                performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Certificate updated successfully!')
            return redirect('dashboard:view_certificates', faculty_id=fid)
    else:
        form = CertificateForm(instance=cert)
    return render(request, 'dashboard/certificate_edit.html', {
        'title': 'Edit Certificate', 'form': form, 'certificate': cert
    })


@login_required
def merge_certificates(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    certs = Certificate.objects.filter(faculty=faculty)
    if not certs.exists():
        messages.error(request, 'No certificates found to merge.')
        return redirect('dashboard:view_certificates', faculty_id=faculty_id)
    try:
        writer = PdfWriter()
        if faculty.cloudinary_pdf_url:
            r = requests.get(faculty.cloudinary_pdf_url)
            if r.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                    tf.write(r.content);
                    tfp = tf.name
                for pg in PdfReader(tfp).pages: writer.add_page(pg)
                os.unlink(tfp)
        for cert in certs:
            if cert.certificate_file:
                try:
                    if os.path.exists(cert.certificate_file.path):
                        for pg in PdfReader(cert.certificate_file.path).pages: writer.add_page(pg)
                except Exception:
                    pass
            elif cert.cloudinary_url:
                r = requests.get(cert.cloudinary_url)
                if r.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                        tf.write(r.content);
                        tfp = tf.name
                    for pg in PdfReader(tfp).pages: writer.add_page(pg)
                    os.unlink(tfp)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as mf:
            writer.write(mf.name);
            merged_path = mf.name
        merged_url = None
        if is_cloudinary_configured():
            try:
                cr = cloudinary.uploader.upload(
                    merged_path, resource_type="raw", folder="merged_certificates",
                    public_id=f"merged_{faculty.employee_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=False
                )
                merged_url = cr['secure_url']
                CloudinaryUpload.objects.create(
                    faculty=faculty, upload_type='merged_certificates',
                    cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                    resource_type=cr['resource_type'], uploaded_by=request.user.username
                )
            except Exception as e:
                logger.error(f"Cloudinary merge upload error: {e}")
        FacultyLog.objects.create(
            faculty=faculty, action='Certificates Merged',
            details=f'{certs.count()} certificates merged',
            performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'merged_url': merged_url,
                                 'message': f'{certs.count()} certificates merged successfully'})
        if merged_url:
            messages.success(request, f'{certs.count()} certificates merged!')
            return redirect(merged_url)
        messages.warning(request, 'Merged locally but Cloudinary upload failed.')
    except Exception as e:
        logger.error(f"Merge error: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error merging: {e}')
    return redirect('dashboard:view_certificates', faculty_id=faculty_id)


@login_required
def merge_certificates_with_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    try:
        pdf_bytes = generate_faculty_pdf_bytes(faculty)
        if not pdf_bytes:
            return JsonResponse({'success': False, 'error': 'Failed to generate faculty PDF'})
        merged = merge_certificates_with_pdf_bytes(pdf_bytes, faculty)
        if merged:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                tf.write(merged);
                tfp = tf.name
            merged_url = None
            if is_cloudinary_configured():
                try:
                    cr = cloudinary.uploader.upload(
                        tfp, resource_type="raw", folder="merged_documents",
                        public_id=f"faculty_certs_{faculty.employee_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        overwrite=False
                    )
                    merged_url = cr['secure_url']
                    CloudinaryUpload.objects.create(
                        faculty=faculty, upload_type='merged_faculty_certs',
                        cloudinary_url=cr['secure_url'], public_id=cr['public_id'],
                        resource_type=cr['resource_type'], uploaded_by=request.user.username
                    )
                except Exception as e:
                    logger.error(f"Cloudinary error: {e}")
            os.unlink(tfp)
            FacultyLog.objects.create(
                faculty=faculty, action='Certificates Merged with PDF',
                details=f'Certs merged with PDF: {Certificate.objects.filter(faculty=faculty).count()} certs',
                performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR')
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'merged_url': merged_url})
            if merged_url: return redirect(merged_url)
            return JsonResponse({'success': False, 'error': 'Failed to upload to Cloudinary'})
        return JsonResponse({'success': False, 'error': 'Failed to merge certificates'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def generate_faculty_pdf_bytes(faculty):
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        factory = RequestFactory()
        fake_req = factory.get('/')
        fake_req.user = AnonymousUser()
        fake_req.META['REMOTE_ADDR'] = '127.0.0.1'
        r = generate_faculty_pdf(fake_req, faculty.id)
        return r.content if isinstance(r, HttpResponse) else None
    except Exception as e:
        logger.error(f"Error generating PDF bytes: {e}")
        return None


def merge_certificates_with_pdf_bytes(pdf_bytes, faculty):
    try:
        writer = PdfWriter()
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                tf.write(pdf_bytes);
                tfp = tf.name
            for pg in PdfReader(tfp).pages: writer.add_page(pg)
        for cert in Certificate.objects.filter(faculty=faculty):
            if cert.cloudinary_url:
                try:
                    r = requests.get(cert.cloudinary_url)
                    if r.status_code == 200 and r.content[:4] == b'%PDF':
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tc:
                            tc.write(r.content);
                            tcp = tc.name
                        for pg in PdfReader(tcp).pages: writer.add_page(pg)
                        try:
                            os.unlink(tcp)
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"Error merging cert: {e}")
            elif cert.certificate_file:
                try:
                    if os.path.exists(cert.certificate_file.path):
                        for pg in PdfReader(cert.certificate_file.path).pages: writer.add_page(pg)
                except Exception:
                    pass
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as mf:
            writer.write(mf.name)
            with open(mf.name, 'rb') as f: merged = f.read()
            os.unlink(mf.name)
        if pdf_bytes and 'tfp' in dir():
            try:
                os.unlink(tfp)
            except Exception:
                pass
        return merged
    except Exception as e:
        logger.error(f"Error in merge_certificates_with_pdf_bytes: {e}")
        return None


@login_required
def preview_merged_pdf(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    recent = CloudinaryUpload.objects.filter(
        faculty=faculty,
        upload_type__in=['merged', 'merged_certificates', 'merged_faculty_certs'],
        public_id__contains='merged'
    ).order_by('-upload_date').first()
    if recent and recent.cloudinary_url:
        return JsonResponse({'success': True, 'pdf_url': recent.cloudinary_url, 'message': 'Merged PDF available'})
    return JsonResponse({'success': False, 'error': 'No merged PDF found.'})


# ==================== FACULTY STATISTICS & APIs ====================

@login_required
def faculty_statistics_api(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    rc = ResearchProject.objects.filter(faculty=faculty).count()
    return JsonResponse({
        'total_subjects': faculty.subjects.count(),
        'total_students': 0,
        'avg_rating': 4.5,
        'teaching_load': 75,
        'research_output': 60,
        'attendance_rate': 95,
        'publications': rc,
        'conferences': rc,
        'projects': 3,
        'awards': 2,
    })


@login_required
def bulk_faculty_actions(request):
    if request.method != 'POST':
        return redirect('dashboard:faculty_list')
    action = request.POST.get('bulk_action')
    faculty_ids = request.POST.getlist('faculty_ids')
    if not faculty_ids:
        messages.error(request, 'No faculty members selected.')
        return redirect('dashboard:faculty_list')
    if action == 'delete':
        cnt = 0
        for fid in faculty_ids:
            try:
                Faculty.objects.get(id=fid).delete(); cnt += 1
            except Faculty.DoesNotExist:
                pass
        FacultyLog.objects.create(faculty=None, action='Bulk Faculty Delete',
                                  details=f'{cnt} faculty deleted in bulk', performed_by=request.user.username,
                                  ip_address=request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Deleted {cnt} faculty member(s).')
    elif action == 'activate':
        cnt = Faculty.objects.filter(id__in=faculty_ids).update(is_active=True)
        messages.success(request, f'Activated {cnt} faculty member(s).')
    elif action == 'deactivate':
        cnt = Faculty.objects.filter(id__in=faculty_ids).update(is_active=False)
        messages.success(request, f'Deactivated {cnt} faculty member(s).')
    elif action == 'export_csv':
        return export_faculty_csv(request, faculty_ids)
    elif action == 'generate_pdfs':
        return bulk_generate_faculty_pdfs(request)
    elif action == 'sync_cloudinary':
        return bulk_sync_to_cloudinary(request)
    else:
        messages.error(request, 'Invalid bulk action.')
    return redirect('dashboard:faculty_list')


@login_required
def export_faculty_csv(request, faculty_ids=None):
    qs = Faculty.objects.filter(id__in=faculty_ids) if faculty_ids else Faculty.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="faculty_export_{date.today().strftime("%Y%m%d")}.csv"'
    w = csv.writer(response)
    w.writerow(['Employee Code', 'Staff Name', 'Department', 'Designation', 'Email', 'Phone',
                'Date of Birth', 'Joining Date', 'UG Degree', 'UG Year', 'PG Degree', 'PG Year',
                'PhD Status', 'Total Experience', 'Current Status', 'Cloudinary PDF URL', 'Cloudinary Photo URL'])
    for f in qs:
        w.writerow([
            f.employee_code, f.staff_name, f.department, f.designation,
            f.email, f.mobile,
            f.dob.strftime('%Y-%m-%d') if f.dob else '',
            f.joining_date.strftime('%Y-%m-%d') if f.joining_date else '',
            getattr(f, 'ug_degree', ''), getattr(f, 'ug_year', ''),
            getattr(f, 'pg_degree', ''), getattr(f, 'pg_year', ''),
            getattr(f, 'phd_degree', ''),
            calculate_experience(f.joining_date) if f.joining_date else 'N/A',
            'Active' if f.is_active else 'Inactive',
            f.cloudinary_pdf_url or '', f.cloudinary_photo_url or '',
        ])
    FacultyLog.objects.create(faculty=None, action='Faculty CSV Export',
                              details=f'Exported {qs.count()} faculty to CSV',
                              performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
    return response


# ==================== BULK UPLOAD ====================

@login_required
def bulk_upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if pd is None:
                    messages.error(request, 'Pandas not installed. Cannot process file.')
                    return redirect('dashboard:bulk_upload')
                f = request.FILES['file']
                fn = f.name.lower()
                if fn.endswith('.csv'):
                    df = pd.read_csv(f)
                elif fn.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(f)
                else:
                    messages.error(request, 'Unsupported format. Use CSV or Excel.')
                    return redirect('dashboard:bulk_upload')
                ok, err = process_csv_faculty_data(df, request.user)
                if ok:  messages.success(request, f'Imported {ok} faculty records.')
                if err: messages.warning(request, f'{err} records had errors.')
                FacultyLog.objects.create(faculty=None, action='Bulk Faculty Upload',
                                          details=f'Bulk upload: {ok} ok, {err} failed',
                                          performed_by=request.user.username,
                                          ip_address=request.META.get('REMOTE_ADDR'))
                return redirect('dashboard:faculty_list')
            except Exception as e:
                logger.error(f"Bulk upload error: {e}")
                messages.error(request, f'Error processing file: {e}')
                return redirect('dashboard:bulk_upload')
    else:
        form = BulkUploadForm()
    return render(request, 'dashboard/bulk_upload.html', {
        'form': form, 'title': 'Bulk Faculty Upload', 'has_pandas': pd is not None
    })


def process_csv_faculty_data(df, user):
    ok = err = 0
    required = ['employee_code', 'staff_name', 'department', 'designation']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found.")
    for i, row in df.iterrows():
        try:
            ec = str(row['employee_code']).strip()
            fac = Faculty.objects.filter(employee_code=ec).first()
            if fac:
                for col in df.columns:
                    if hasattr(fac, col) and not pd.isna(row[col]):
                        if col in ['dob', 'joining_date']:
                            try:
                                setattr(fac, col, pd.to_datetime(row[col]).date())
                            except Exception:
                                pass
                        else:
                            setattr(fac, col, row[col])
                fac.save();
                act = 'updated'
            else:
                fd = {}
                for col in df.columns:
                    if hasattr(Faculty, col) and not pd.isna(row[col]):
                        if col in ['dob', 'joining_date']:
                            try:
                                fd[col] = pd.to_datetime(row[col]).date()
                            except Exception:
                                fd[col] = None
                        else:
                            fd[col] = row[col]
                fac = Faculty.objects.create(**fd)
                FacultyProfile.objects.create(faculty=fac)
                act = 'created'
            FacultyLog.objects.create(faculty=fac, action=f'Bulk Upload - {act}',
                                      details=f'Faculty {act} via bulk upload: {fac.employee_code}',
                                      performed_by=user.username if user else 'System', ip_address='127.0.0.1')
            ok += 1
        except Exception as e:
            logger.error(f"Error row {i}: {e}");
            err += 1
    return ok, err


# ==================== SYSTEM UTILITIES ====================

@login_required
def system_status(request):
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
        except Exception:
            system_info = {'error': 'Unable to retrieve system info'}
    cs = {'connected': False, 'error': ''}
    if is_cloudinary_configured():
        try:
            r = cloudinary.api.ping()
            cs['connected'] = r.get('status') == 'ok'
        except Exception as e:
            cs['error'] = str(e)
    else:
        cs['error'] = 'Cloudinary not configured'
    return render(request, 'dashboard/system_status.html', {
        'title': 'System Status',
        'stats': {
            'total_faculty': Faculty.objects.count(),
            'active_faculty': Faculty.objects.filter(is_active=True).count(),
            'total_students': Student.objects.count(),
            'total_certificates': Certificate.objects.count(),
            'cloudinary_uploads': CloudinaryUpload.objects.count(),
            'total_logs': FacultyLog.objects.count(),
            'recent_logs': FacultyLog.objects.order_by('-created_at')[:10],
        },
        'system_info': system_info,
        'db_stats': {
            'faculty_table': Faculty.objects.count(),
            'student_table': Student.objects.count(),
            'certificate_table': Certificate.objects.count(),
            'log_table': FacultyLog.objects.count(),
            'cloudinary_table': CloudinaryUpload.objects.count(),
        },
        'cloudinary_status': cs,
        'has_psutil': psutil is not None,
        'has_pandas': pd is not None,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })


@login_required
def clear_logs(request):
    if request.method == 'POST':
        try:
            days = int(request.POST.get('days', 30))
            cutoff = timezone.now() - timedelta(days=days)
            cnt, _ = FacultyLog.objects.filter(created_at__lt=cutoff).delete()
            FacultyLog.objects.create(faculty=None, action='Logs Cleared',
                                      details=f'Cleared {cnt} logs older than {days} days',
                                      performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Deleted {cnt} logs older than {days} days.')
            return redirect('dashboard:system_status')
        except Exception as e:
            messages.error(request, f'Error clearing logs: {e}')
            return redirect('dashboard:system_status')
    return render(request, 'dashboard/clear_logs.html', {'title': 'Clear System Logs'})


@login_required
def backup_database(request):
    try:
        from django.core.management import call_command
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bf = os.path.join(backup_dir, f'db_backup_{ts}.json')
        with open(bf, 'w') as f:
            call_command('dumpdata', stdout=f)
        FacultyLog.objects.create(faculty=None, action='Database Backup',
                                  details=f'Backup created: {bf}',
                                  performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Backup created: {os.path.basename(bf)}')
    except Exception as e:
        logger.error(f"Backup error: {e}");
        messages.error(request, f'Error creating backup: {e}')
    return redirect('dashboard:system_status')


# ==================== API ENDPOINTS ====================

@login_required
@require_GET
def api_faculty_list(request):
    data = list(Faculty.objects.all().values(
        'id', 'employee_code', 'staff_name', 'department', 'designation',
        'email', 'mobile', 'is_active', 'cloudinary_pdf_url', 'cloudinary_photo_url'
    ))
    return JsonResponse(data, safe=False)


@login_required
@require_GET
def api_faculty_detail(request, faculty_id):
    f = get_object_or_404(Faculty, id=faculty_id)
    return JsonResponse({
        'id': f.id, 'employee_code': f.employee_code, 'staff_name': f.staff_name,
        'department': f.department, 'designation': f.designation,
        'email': f.email, 'mobile': f.mobile,
        'dob': f.dob.strftime('%Y-%m-%d') if f.dob else None,
        'joining_date': f.joining_date.strftime('%Y-%m-%d') if f.joining_date else None,
        'ug_degree': getattr(f, 'ug_degree', None), 'ug_year': getattr(f, 'ug_year', None),
        'pg_degree': getattr(f, 'pg_degree', None), 'pg_year': getattr(f, 'pg_year', None),
        'phd_degree': getattr(f, 'phd_degree', None),
        'is_active': f.is_active,
        'experience': calculate_experience(f.joining_date) if f.joining_date else "N/A",
        'cloudinary_pdf_url': f.cloudinary_pdf_url,
        'cloudinary_photo_url': f.cloudinary_photo_url,
        'created_at': f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else None,
        'updated_at': f.updated_at.strftime('%Y-%m-%d %H:%M:%S') if f.updated_at else None,
    })


@login_required
@require_POST
def api_update_faculty_status(request, faculty_id):
    f = get_object_or_404(Faculty, id=faculty_id)
    try:
        data = json.loads(request.body)
        ns = data.get('is_active')
        if ns is None:
            return JsonResponse({'success': False, 'error': 'Missing is_active'}, status=400)
        old = f.is_active;
        f.is_active = bool(ns);
        f.save()
        FacultyLog.objects.create(faculty=f, action='Status Updated via API',
                                  details=f'Status: {"Active" if old else "Inactive"} -> {"Active" if f.is_active else "Inactive"}',
                                  performed_by=request.user.username, ip_address=request.META.get('REMOTE_ADDR'))
        return JsonResponse({'success': True, 'message': 'Status updated', 'is_active': f.is_active})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def api_student_list(request):
    if not (request.user.is_authenticated or request.session.get('student_logged_in')):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    data = list(Student.objects.all().values(
        'id', 'ht_no', 'student_name', 'father_name', 'mother_name', 'gender', 'dob', 'age',
        'category', 'year', 'sem', 'email', 'student_phone', 'parent_phone',
        'ssc_marks', 'inter_marks', 'cgpa', 'created_at'
    ))
    return JsonResponse(data, safe=False)


@require_GET
def api_student_detail(request, student_id):
    if not (request.user.is_authenticated or request.session.get('student_logged_in')):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    s = get_object_or_404(Student, id=student_id)
    return JsonResponse({
        'id': s.id, 'ht_no': s.ht_no, 'student_name': s.student_name,
        'father_name': s.father_name, 'mother_name': s.mother_name,
        'gender': s.gender, 'dob': s.dob.strftime('%Y-%m-%d') if s.dob else None,
        'age': s.age, 'category': s.category, 'religion': s.religion,
        'blood_group': s.blood_group, 'aadhar': s.aadhar,
        'apaar_id': s.apaar_id, 'address': s.address,
        'parent_phone': s.parent_phone, 'student_phone': s.student_phone,
        'email': s.email, 'year': s.year, 'sem': s.sem,
        'ssc_marks': s.ssc_marks, 'inter_marks': s.inter_marks, 'cgpa': s.cgpa,
        'photo_url': getattr(s, 'photo_url', None),
        'pdf_url': getattr(s, 'pdf_url', None),
        'pdf_generated': getattr(s, 'pdf_generated', None),
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else None,
    })


# ==================== CHARTS & ANALYTICS ====================

@login_required
def faculty_charts(request):
    if plt is None:
        messages.error(request, 'Matplotlib not installed.')
        return redirect('dashboard:dashboard')
    try:
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        dept_data = Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:10]
        depts = [d['department'] for d in dept_data]
        cnts = [d['count'] for d in dept_data]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(depts, cnts)
        plt.title('Faculty Distribution by Department')
        plt.xlabel('Department');
        plt.ylabel('Number of Faculty')
        plt.xticks(rotation=45, ha='right')
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., h + 0.1, f'{int(h)}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'dept_distribution.png'), dpi=100);
        plt.close()

        qual_data = {
            'PhD Completed': Faculty.objects.filter(phd_degree='Completed').count(),
            'PhD Pursuing': Faculty.objects.filter(phd_degree='Pursuing').count(),
            'PG Only': Faculty.objects.filter(pg_year__isnull=False,
                                              phd_degree__in=['', 'Not Started', 'None']).count(),
            'UG Only': Faculty.objects.filter(ug_year__isnull=False, pg_year__isnull=True).count(),
        }
        plt.figure(figsize=(8, 8))
        plt.pie(list(qual_data.values()), labels=list(qual_data.keys()),
                colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'], autopct='%1.1f%%', startangle=90)
        plt.axis('equal');
        plt.title('Faculty Qualification Distribution')
        plt.savefig(os.path.join(charts_dir, 'qualification_distribution.png'), dpi=100);
        plt.close()

        today = date.today()
        exp_ranges = ['0-5 years', '5-10 years', '10-15 years', '15+ years']
        exp_counts = [0, 0, 0, 0]
        for f in Faculty.objects.all():
            if f.joining_date:
                yrs = (today - f.joining_date).days / 365.25
                if yrs <= 5:
                    exp_counts[0] += 1
                elif yrs <= 10:
                    exp_counts[1] += 1
                elif yrs <= 15:
                    exp_counts[2] += 1
                else:
                    exp_counts[3] += 1
        plt.figure(figsize=(10, 6))
        bars = plt.bar(range(len(exp_ranges)), exp_counts,
                       color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        plt.title('Faculty Experience Distribution')
        plt.xlabel('Experience Range');
        plt.ylabel('Number of Faculty')
        plt.xticks(range(len(exp_ranges)), exp_ranges)
        for i, (bar, cnt) in enumerate(zip(bars, exp_counts)):
            plt.text(bar.get_x() + bar.get_width() / 2., cnt + 0.1, f'{cnt}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'experience_distribution.png'), dpi=100);
        plt.close()

        return render(request, 'dashboard/charts.html', {
            'title': 'Faculty Analytics Charts',
            'chart_urls': {
                'dept_chart': os.path.join(settings.MEDIA_URL, 'charts', 'dept_distribution.png'),
                'qual_chart': os.path.join(settings.MEDIA_URL, 'charts', 'qualification_distribution.png'),
                'exp_chart': os.path.join(settings.MEDIA_URL, 'charts', 'experience_distribution.png'),
            },
            'dept_data': list(zip(depts, cnts)),
            'qual_data': qual_data,
            'exp_data': list(zip(exp_ranges, exp_counts)),
        })
    except Exception as e:
        logger.error(f"Chart error: {e}")
        messages.error(request, f'Error generating charts: {e}')
        return redirect('dashboard:dashboard')


@login_required
def student_charts(request):
    if plt is None:
        messages.error(request, 'Matplotlib not installed.')
        return redirect('dashboard:students_data')
    try:
        charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(charts_dir, exist_ok=True)

        gd = Student.objects.values('gender').annotate(count=Count('id')).order_by('-count')
        gs = [d['gender'] for d in gd];
        gc = [d['count'] for d in gd]
        plt.figure(figsize=(8, 8))
        plt.pie(gc, labels=gs, colors=['#66b3ff', '#ff9999', '#99ff99'][:len(gs)],
                autopct='%1.1f%%', startangle=90)
        plt.axis('equal');
        plt.title('Student Gender Distribution')
        plt.savefig(os.path.join(charts_dir, 'student_gender_distribution.png'), dpi=100);
        plt.close()

        yd = Student.objects.values('year').annotate(count=Count('id')).order_by('year')
        ys = [d['year'] for d in yd];
        yc = [d['count'] for d in yd]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(ys, yc)
        plt.title('Student Distribution by Year')
        plt.xlabel('Year');
        plt.ylabel('Number of Students')
        for bar, cnt in zip(bars, yc):
            plt.text(bar.get_x() + bar.get_width() / 2., cnt + 0.1, f'{cnt}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'student_year_distribution.png'), dpi=100);
        plt.close()

        cd = Student.objects.values('category').annotate(count=Count('id')).order_by('-count')[:10]
        cs = [d['category'] for d in cd];
        cc = [d['count'] for d in cd]
        plt.figure(figsize=(10, 6))
        bars = plt.bar(range(len(cs)), cc)
        plt.title('Student Category Distribution (Top 10)')
        plt.xlabel('Category');
        plt.ylabel('Number of Students')
        plt.xticks(range(len(cs)), cs, rotation=45, ha='right')
        for bar, cnt in zip(bars, cc):
            plt.text(bar.get_x() + bar.get_width() / 2., cnt + 0.1, f'{cnt}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'student_category_distribution.png'), dpi=100);
        plt.close()

        return render(request, 'dashboard/student_charts.html', {
            'title': 'Student Analytics Charts',
            'chart_urls': {
                'gender_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_gender_distribution.png'),
                'year_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_year_distribution.png'),
                'category_chart': os.path.join(settings.MEDIA_URL, 'charts', 'student_category_distribution.png'),
            },
            'gender_data': list(zip(gs, gc)),
            'year_data': list(zip(ys, yc)),
            'category_data': list(zip(cs, cc)),
        })
    except Exception as e:
        logger.error(f"Student chart error: {e}")
        messages.error(request, f'Error generating charts: {e}')
        return redirect('dashboard:students_data')


# ==================== MISCELLANEOUS ====================

@login_required
def recent_activity(request):
    acts = FacultyLog.objects.select_related('faculty', 'student').order_by('-created_at')[:50]
    return render(request, 'dashboard/recent_activity.html', {
        'title': 'Recent Activities', 'activities': acts,
        'total_activities': FacultyLog.objects.count(),
    })


@login_required
def search_faculty(request):
    q = request.GET.get('q', '')
    qs = Faculty.objects.filter(
        Q(staff_name__icontains=q) | Q(employee_code__icontains=q) |
        Q(department__icontains=q) | Q(designation__icontains=q) | Q(email__icontains=q)
    ).order_by('staff_name')[:20] if q else Faculty.objects.none()
    results = []
    for f in qs:
        pu = None
        try:
            pu = f.cloudinary_photo_url or (f.photo.url if f.photo else None)
        except Exception:
            pass
        results.append({
            'id': f.id, 'name': f.staff_name, 'employee_code': f.employee_code,
            'department': f.department, 'designation': f.designation, 'photo_url': pu,
            'detail_url': reverse('dashboard:faculty_dashboard') + f'?id={f.id}',
        })
    return JsonResponse({'results': results, 'count': len(results)})


@login_required
def search_students(request):
    q = request.GET.get('q', '')
    qs = Student.objects.filter(
        Q(student_name__icontains=q) | Q(ht_no__icontains=q) |
        Q(father_name__icontains=q) | Q(email__icontains=q)
    ).order_by('student_name')[:20] if q else Student.objects.none()
    results = [
        {
            'id': s.id, 'name': s.student_name, 'ht_no': s.ht_no,
            'year': s.year, 'sem': s.sem,
            'branch': getattr(s, 'branch', ''),
            'roll_number': getattr(s, 'roll_number', ''),
            'photo_url': getattr(s, 'photo_url', None),
            'detail_url': reverse('dashboard:students_data'),
        }
        for s in qs
    ]
    return JsonResponse({'results': results, 'count': len(results)})


@login_required
def quick_stats(request):
    return JsonResponse({
        'total_faculty': Faculty.objects.count(),
        'active_faculty': Faculty.objects.filter(is_active=True).count(),
        'total_students': Student.objects.count(),
        'total_certificates': Certificate.objects.count(),
        'recent_uploads': Faculty.objects.order_by('-created_at').count(),
        'cloudinary_uploads': CloudinaryUpload.objects.count(),
    })


# ==================== ERROR HANDLERS ====================

def handler404(request, exception):
    return render(request, 'dashboard/404.html', {
        'title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.'
    }, status=404)


def handler500(request):
    return render(request, 'dashboard/500.html', {
        'title': 'Server Error',
        'error_message': 'An internal server error occurred.'
    }, status=500)


def handler403(request, exception):
    return render(request, 'dashboard/403.html', {
        'title': 'Access Denied',
        'error_message': 'You do not have permission to access this page.'
    }, status=403)


def handler400(request, exception):
    return render(request, 'dashboard/400.html', {
        'title': 'Bad Request',
        'error_message': 'Invalid request. Please check your input.'
    }, status=400)


# ==================== APPLICATION VIEWS ====================

@login_required
def application_home(request):
    return render(request, 'dashboard/application_home.html', {
        'title': 'Faculty Management System', 'user': request.user,
    })


@login_required
def profile_settings(request):
    user = request.user
    if request.method == 'POST':
        fn = request.POST.get('first_name', '').strip()
        ln = request.POST.get('last_name', '').strip()
        em = request.POST.get('email', '').strip().lower()
        if fn: user.first_name = fn
        if ln: user.last_name = ln
        if em: user.email = em
        np = request.POST.get('new_password', '').strip()
        cp = request.POST.get('confirm_password', '').strip()
        if np and np == cp:
            user.set_password(np)
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard:profile_settings')
    return render(request, 'dashboard/profile_settings.html', {
        'title': 'Profile Settings', 'user': user,
    })


@login_required
def about_system(request):
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
    return render(request, 'dashboard/help.html', {
        'title': 'Help & Documentation',
        'sections': [
            {'title': 'Faculty Management',
             'content': 'Add, edit, delete faculty. Generate PDF profiles and upload to Cloudinary.'},
            {'title': 'Student Management', 'content': 'Register students, manage data, generate student PDFs.'},
            {'title': 'Certificate Management', 'content': 'Upload, view, and manage certificates for faculty.'},
            {'title': 'Cloudinary Integration', 'content': 'Sync faculty PDFs and photos to Cloudinary.'},
            {'title': 'Analytics', 'content': 'View charts and statistics about faculty and students.'},
            {'title': 'System Tools', 'content': 'Backup database, clear logs, check system status.'},
        ]
    })


@login_required
def contact_support(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        msg = request.POST.get('message', '').strip()
        if name and email and subject and msg:
            logger.info(f"Support request from {name} ({email}): {subject}")
            messages.success(request, 'Message sent to support. We will get back to you soon.')
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
    return render(request, 'dashboard/session_info.html', {
        'title': 'Session Information',
        'session_info': {
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
    })


@login_required
def clear_session(request):
    auth = {k: request.session.get(k) for k in
            ('_auth_user_id', '_auth_user_backend', '_auth_user_hash')}
    request.session.clear()
    for k, v in auth.items():
        if v: request.session[k] = v
    messages.success(request, 'Session data cleared successfully.')
    return redirect('dashboard:session_info')


# ==================== FACULTY PDF HELPERS ====================

@login_required
def faculty_pdf(request, faculty_id):
    return redirect('dashboard:generate_faculty_pdf', faculty_id=faculty_id)


@login_required
def ajax_check_pdf_status(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    has_pdf = bool(faculty.cloudinary_pdf_url)
    return JsonResponse({
        'success': True,
        'status': {
            'has_cloudinary_pdf': has_pdf,
            'cloudinary_url': faculty.cloudinary_pdf_url if has_pdf else None,
        }
    })