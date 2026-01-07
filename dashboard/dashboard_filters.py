# dashboard/templatetags/dashboard_filters.py
from django import template

register = template.Library()

@register.filter
def filter_by_gender(queryset, gender):
    """Filter queryset by gender"""
    try:
        if hasattr(queryset, 'filter'):
            return queryset.filter(gender=gender)
        return []
    except:
        return []