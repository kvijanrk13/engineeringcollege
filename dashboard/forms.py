from django import forms
from .models import Faculty, Certificate


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = "__all__"


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = "__all__"


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class BulkUploadForm(forms.Form):
    file = forms.FileField()
