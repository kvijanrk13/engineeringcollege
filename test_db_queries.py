#!/usr/bin/env python
import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

from dashboard.models import Faculty, Certificate, FacultyLog

print("Testing database queries...")

try:
    # Test basic queries from dashboard view
    total_faculty = Faculty.objects.count()
    print(f"Total faculty: {total_faculty}")

    with_phd = Faculty.objects.exclude(phd_degree__isnull=True).exclude(phd_degree__exact='').count()
    print(f"With PhD: {with_phd}")

    today = date.today()
    print(f"Today: {today}")

    exp_distribution = {'0-5': 0, '5-10': 0, '10-15': 0, '15+': 0}
    for f in Faculty.objects.all():
        if f.joining_date:
            jd = f.joining_date
            if hasattr(jd, 'date'):
                jd = jd.date()
            try:
                yrs = (today - jd).days / 365.25
                if yrs <= 5:
                    exp_distribution['0-5'] += 1
                elif yrs <= 10:
                    exp_distribution['5-10'] += 1
                elif yrs <= 15:
                    exp_distribution['10-15'] += 1
                else:
                    exp_distribution['15+'] += 1
            except (TypeError, ValueError) as e:
                print(f"Error calculating experience for faculty {f.id}: {e}")
                continue

    print(f"Experience distribution: {exp_distribution}")

    total_certificates = Certificate.objects.count()
    print(f"Total certificates: {total_certificates}")

    from django.db.models import Count
    departments = Faculty.objects.values('department').annotate(count=Count('id')).order_by('-count')[:5]
    print(f"Departments: {list(departments)}")

    recent_uploads = Faculty.objects.order_by('-created_at')[:5]
    print(f"Recent uploads count: {len(recent_uploads)}")

    recent_logs = FacultyLog.objects.order_by('-created_at')[:5]
    print(f"Recent logs count: {len(recent_logs)}")

    print("All queries successful!")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()