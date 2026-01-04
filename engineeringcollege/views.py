"""
Project level views for engineeringcollege.
"""

from django.shortcuts import render
from django.http import JsonResponse

def college_info(request):
    """College information page"""
    context = {
        'college_name': 'ANURAG Engineering College',
        'established': '2001',
        'affiliation': 'JNTUH',
        'location': 'Hyderabad, Telangana',
        'departments': [
            'Information Technology',
            'Computer Science Engineering',
            'Electronics and Communication Engineering',
            'Mechanical Engineering',
            'Civil Engineering',
            'Electrical and Electronics Engineering',
        ]
    }
    return render(request, 'college_info.html', context)

def contact(request):
    """Contact information page"""
    context = {
        'address': 'ANURAG Engineering College, Hyderabad, Telangana - 500001',
        'phone': '+91-40-12345678',
        'email': 'info@anurag.edu.in',
        'website': 'www.anurag.edu.in',
    }
    return render(request, 'contact.html', context)

def api_college_stats(request):
    """API endpoint for college statistics"""
    stats = {
        'students_total': 2500,
        'faculty_total': 150,
        'departments': 6,
        'courses': 25,
        'placements': 85,  # percentage
    }
    return JsonResponse({'status': 'success', 'data': stats})


# ================= CUSTOM ERROR HANDLERS (ADDED) =================

def handler404(request, exception):
    return render(request, "dashboard/404.html", status=404)


def handler500(request):
    return render(request, "dashboard/500.html", status=500)
