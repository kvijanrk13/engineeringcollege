"""
Context processors for dashboard app.
"""

from django.conf import settings

def college_info(request):
    """Add college information to all templates"""
    return {
        'college_name': settings.COLLEGE_NAME,
        'department_name': settings.DEPARTMENT_NAME,
        'academic_year': settings.ACADEMIC_YEAR,
    }