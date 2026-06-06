from __future__ import annotations

from django import forms

from .models import StudentRegistration


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = StudentRegistration
        fields = ["full_name", "roll_number", "email", "department", "college"]
        labels = {
            "full_name": "Customer Name",
            "roll_number": "Contact Number / Reference ID",
            "email": "Email Address",
            "department": "Car Model",
            "college": "Budget or Notes",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Customer full name"}),
            "roll_number": forms.TextInput(attrs={"placeholder": "Phone number or customer ID"}),
            "email": forms.EmailInput(attrs={"placeholder": "customer@example.com"}),
            "department": forms.TextInput(attrs={"placeholder": "Example: Swift, City, Creta"}),
            "college": forms.TextInput(attrs={"placeholder": "Budget range or purchase notes"}),
        }
