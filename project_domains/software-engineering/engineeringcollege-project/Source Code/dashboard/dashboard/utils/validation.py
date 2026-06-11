# dashboard/utils/validation.py
import re


def validate_faculty_data(data):
    """Validate faculty data"""
    errors = []
    warnings = []

    # Required fields
    required_fields = ['employee_code', 'staff_name', 'email', 'department']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} is required")

    # Email validation
    email = data.get('email', '')
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append("Invalid email format")

    # Phone validation
    mobile = data.get('mobile', '')
    if mobile and not re.match(r'^[0-9]{10}$', mobile):
        warnings.append("Mobile number should be 10 digits")

    # Date validations
    dob = data.get('dob')
    joining_date = data.get('joining_date')
    if dob and joining_date and dob > joining_date:
        warnings.append("Date of birth cannot be after joining date")

    return len(errors) == 0, errors, warnings


def validate_student_data(data):
    """Validate student data"""
    errors = []
    warnings = []

    # Required fields
    required_fields = ['ht_no', 'student_name']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} is required")

    # Email validation
    email = data.get('email', '')
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append("Invalid email format")

    # Phone validation
    student_phone = data.get('student_phone', '')
    if student_phone and not re.match(r'^[0-9]{10}$', student_phone):
        warnings.append("Student phone number should be 10 digits")

    # Roll number format
    ht_no = data.get('ht_no', '')
    if ht_no and not re.match(r'^[0-9A-Za-z]+$', ht_no):
        warnings.append("Hall ticket number should be alphanumeric")

    return len(errors) == 0, errors, warnings