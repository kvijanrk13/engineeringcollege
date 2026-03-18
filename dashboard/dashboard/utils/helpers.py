# dashboard/utils/helpers.py
from datetime import date


def calculate_experience(joining_date):
    """Calculate years of experience from joining date"""
    if not joining_date:
        return "N/A"
    today = date.today()
    years = today.year - joining_date.year
    months = today.month - joining_date.month
    days = today.day - joining_date.day

    if days < 0:
        months -= 1
        # Get days in previous month
        if today.month == 1:
            prev_month = 12
            year_for_days = today.year - 1
        else:
            prev_month = today.month - 1
            year_for_days = today.year

        if prev_month in [4, 6, 9, 11]:
            days_in_prev_month = 30
        elif prev_month == 2:
            # Check for leap year
            if (year_for_days % 4 == 0 and year_for_days % 100 != 0) or (year_for_days % 400 == 0):
                days_in_prev_month = 29
            else:
                days_in_prev_month = 28
        else:
            days_in_prev_month = 31

        days += days_in_prev_month

    if months < 0:
        years -= 1
        months += 12

    return f"{years} Years {months} Months {days} Days"


def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    today = date.today()
    age = today.year - dob.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age


def format_date(date_obj, format_str="%d-%m-%Y"):
    """Format date object to string"""
    if not date_obj:
        return ""
    return date_obj.strftime(format_str)


def get_academic_year(date_obj=None):
    """Get academic year for a given date"""
    if not date_obj:
        date_obj = date.today()
    year = date_obj.year
    month = date_obj.month
    if month >= 6:  # June is start of academic year
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"