"""
dashboard/forms.py - Updated to match models
"""

from django import forms
from .models import Faculty, Certificate, Student, Subject


# =====================================================
# FACULTY FORM
# =====================================================

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


# =====================================================
# CERTIFICATE FORM
# =====================================================

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'certificate_type',
            'certificate_file',
            'issued_by',
            'issue_date',
            'expiry_date',
            'is_verified',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


# =====================================================
# LOGIN FORM
# =====================================================

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


# =====================================================
# BULK UPLOAD FORM
# =====================================================

class BulkUploadForm(forms.Form):
    file = forms.FileField()
    file_type = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('excel', 'Excel')],
        required=True
    )


# =====================================================
# STUDENT FORM
# =====================================================

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


# =====================================================
# SUBJECT FORM  ✅ REQUIRED BY views.py
# =====================================================

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'
