from __future__ import annotations

from django import forms

from .models import StudentRegistration


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = StudentRegistration
        fields = ["full_name", "roll_number", "email", "department", "college"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Student full name"}),
            "roll_number": forms.TextInput(attrs={"placeholder": "Roll number / hall ticket number"}),
            "email": forms.EmailInput(attrs={"placeholder": "student@example.com"}),
            "department": forms.TextInput(attrs={"placeholder": "Information Technology"}),
            "college": forms.TextInput(attrs={"placeholder": "Engineering College"}),
        }
