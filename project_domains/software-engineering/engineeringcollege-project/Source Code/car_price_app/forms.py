from __future__ import annotations

from django import forms
from django.core.validators import validate_email

from .models import StudentRegistration


class StudentRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label="Gmail Address",
        widget=forms.EmailInput(attrs={"placeholder": "yourname@gmail.com"}),
        help_text="Only Gmail addresses are accepted for this registration.",
    )

    class Meta:
        model = StudentRegistration
        fields = ["full_name", "roll_number", "email", "department", "college"]
        labels = {
            "full_name": "Customer Name",
            "roll_number": "Contact Number / Reference ID",
            "email": "Gmail Address",
            "department": "Car Model",
            "college": "Budget or Notes",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Customer full name"}),
            "roll_number": forms.TextInput(attrs={"placeholder": "Phone number or customer ID"}),
            "email": forms.EmailInput(attrs={"placeholder": "yourname@gmail.com"}),
            "department": forms.TextInput(attrs={"placeholder": "Example: Swift, City, Creta"}),
            "college": forms.TextInput(attrs={"placeholder": "Budget range or purchase notes"}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        validate_email(email)
        if not email.endswith("@gmail.com"):
            raise forms.ValidationError("Only Gmail addresses (ending with @gmail.com) are allowed.")
        return email


class CarEstimateForm(forms.Form):
    brand = forms.CharField(
        label="Car Brand",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Maruti, Honda, Hyundai"}),
    )
    model = forms.CharField(
        label="Car Name / Model",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Swift, City, Creta"}),
    )
    model_year = forms.IntegerField(
        label="Model Year",
        min_value=1990,
        max_value=2026,
        widget=forms.NumberInput(attrs={"placeholder": "2020"}),
    )
    engine_capacity = forms.FloatField(
        label="Engine CC",
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "1200"}),
    )
    kilometers = forms.IntegerField(
        label="Kilometers Driven",
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "75000"}),
    )
    accident = forms.ChoiceField(
        label="Accident History",
        choices=[("no", "No"), ("yes", "Yes")],
    )
    repairs = forms.ChoiceField(
        label="Previous Repairs",
        choices=[("no", "No"), ("yes", "Yes")],
    )
    owners = forms.ChoiceField(
        label="Number of Owners",
        choices=[
            ("First", "First Owner"),
            ("Second", "Second Owner"),
            ("Third", "Third Owner"),
            ("More", "More than Third Owner"),
        ],
    )
    color = forms.CharField(
        label="Car Color",
        max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "White, Black, Grey"}),
        required=False,
    )
    tyres_modified = forms.ChoiceField(
        label="Tyres Modified",
        choices=[("no", "No"), ("yes", "Yes")],
    )
