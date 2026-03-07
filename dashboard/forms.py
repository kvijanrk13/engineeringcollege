# dashboard/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Faculty, Student, Certificate, FacultyProfile, ResearchProject, Subject


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = [
            'staff_name', 'employee_code', 'department', 'designation',
            'email', 'mobile', 'phone', 'dob', 'joining_date', 'gender',
            'address', 'father_name', 'mother_name', 'state',
            'aadhar', 'pan', 'apaar_id', 'scm',
            'ug_degree', 'ug_year', 'ug_college', 'ug_spec', 'ug_percentage',
            'pg_degree', 'pg_year', 'pg_college', 'pg_spec', 'pg_percentage',
            'phd_degree', 'phd_year', 'phd_university', 'phd_spec',
            'subjects_dealt', 'about_yourself', 'results',
            'ssc_year', 'ssc_percent', 'ssc_school',
            'inter_year', 'inter_percent', 'inter_college',
            'jntuh_id', 'aicte_id', 'orcid_id',
            'photo', 'pdf_document', 'aadhar_file', 'pan_file', 'apaar_file', 'scm_file',
            'ssc_certificate', 'inter_certificate', 'ug_certificate', 'pg_certificate', 'phd_certificate',
            'is_active'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'about_yourself': forms.Textarea(attrs={'rows': 4}),
            'results': forms.Textarea(attrs={'rows': 3}),
            'subjects_dealt': forms.Textarea(attrs={'rows': 3}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'ht_no', 'student_name', 'father_name', 'mother_name',
            'gender', 'dob', 'age', 'nationality', 'category',
            'religion', 'blood_group', 'aadhar', 'apaar_id',
            'address', 'parent_phone', 'student_phone', 'email',
            'task_registered', 'task_username', 'csi_registered', 'csi_membership_id',
            'admission_type', 'other_admission_details', 'eamcet_rank',
            'year', 'sem', 'branch', 'roll_number',
            'ssc_marks', 'inter_marks', 'cgpa',
            'rtrp_project_title', 'intern_title', 'final_project_title', 'other_training',
            'photo', 'cert_achieve', 'cert_intern', 'cert_courses',
            'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'other_admission_details': forms.Textarea(attrs={'rows': 2}),
            'other_training': forms.Textarea(attrs={'rows': 2}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['certificate_type', 'certificate_file', 'issued_by', 'issue_date', 'description']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = [
            'batch_number', 'joining_date', 'experience_other',
            'aadhar_document', 'apaar_document', 'pan_document', 'scm_document'
        ]
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = [
            'research_type', 'title_of_project',
            'marks_awarded', 'doi', 'volume', 'issn_number',
            'journal_name', 'publisher_name', 'upload_pdf'
        ]
        widgets = {
            'title_of_project': forms.TextInput(attrs={'class': 'form-control'}),
            'journal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BulkUploadForm(forms.Form):
    file = forms.FileField(
        label='Select Excel/CSV file',
        help_text='Allowed formats: .csv, .xlsx, .xls'
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()
        if ext not in ['csv', 'xlsx', 'xls']:
            raise forms.ValidationError('Please upload a CSV or Excel file.')
        return file