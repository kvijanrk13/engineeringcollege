# faculty/dashboard/context_processors.py
from .models import Faculty

def faculty_stats(request):
    """Context processor to add faculty stats to all templates"""
    try:
        stats = {
            'total_faculty': Faculty.objects.count(),
            'active_faculty': Faculty.objects.filter(is_active=True).count(),
            'faculty_with_pdf': Faculty.objects.exclude(cloudinary_pdf_url__isnull=True).exclude(cloudinary_pdf_url='').count(),
            'departments': Faculty.objects.values_list('department', flat=True).distinct().count(),
        }
        return {'faculty_stats': stats}
    except:
        return {'faculty_stats': {}}


def college_info(request):
    """Add college information to all templates"""
    return {
        'college_name': 'ANURAG ENGINEERING COLLEGE',
        'college_address': 'Anurag Nagar, Hyderabad, Telangana',
        'college_email': 'info@anurag.ac.in',
        'college_phone': '+91 9553122276',
    }


def user_permissions(request):
    """Add user permissions to templates"""
    if request.user.is_authenticated:
        return {
            'is_exam_branch': request.user.groups.filter(name='Exam Branch').exists(),
            'is_admin': request.user.is_superuser,
            'is_staff': request.user.is_staff,
        }
    return {'is_exam_branch': False, 'is_admin': False, 'is_staff': False}