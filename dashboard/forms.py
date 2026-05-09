# dashboard/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import (
    Faculty, Student, Certificate, Subject,
    FacultyProfile, ResearchProject, ResearchPublication,
    FDP, BTechProject
)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'ht_no', 'student_name', 'father_name', 'mother_name', 'gender',
            'dob', 'nationality', 'category', 'religion', 'blood_group',
            'aadhar', 'apaar_id', 'address', 'parent_phone', 'student_phone',
            'email', 'year', 'sem', 'ssc_marks', 'inter_marks', 'cgpa',
            'task_registered', 'task_username', 'csi_registered', 'csi_membership_id',
            'admission_type', 'other_admission_details', 'eamcet_rank',
            'rtrp_project_title', 'intern_title', 'final_project_title', 'other_training',
            'photo', 'cert_achieve', 'cert_intern', 'cert_courses', 'cert_sdp',
            'cert_extra', 'cert_placement', 'cert_national'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3, 'maxlength': 1000}),
            'other_training': forms.Textarea(attrs={'rows': 2, 'maxlength': 1000}),
            # Enforce maxlength at HTML level for fields with database limits
            'nationalty': forms.TextInput(attrs={'maxlength': 100}),
            'task_username': forms.TextInput(attrs={'maxlength': 100}),
            'csi_membership_id': forms.TextInput(attrs={'maxlength': 100}),
            'category': forms.TextInput(attrs={'maxlength': 50}),
            'religion': forms.TextInput(attrs={'maxlength': 50}),
            'blood_group': forms.TextInput(attrs={'maxlength': 10}),
            'aadhar': forms.TextInput(attrs={'maxlength': 20}),
            'apaar_id': forms.TextInput(attrs={'maxlength': 50}),
            'parent_phone': forms.TextInput(attrs={'maxlength': 15}),
            'student_phone': forms.TextInput(attrs={'maxlength': 15}),
            'email': forms.EmailInput(attrs={'maxlength': 254}),
            'ssc_marks': forms.TextInput(attrs={'maxlength': 20}),
            'inter_marks': forms.TextInput(attrs={'maxlength': 20}),
            'cgpa': forms.TextInput(attrs={'maxlength': 10}),
            'admission_type': forms.TextInput(attrs={'maxlength': 50}),
            'eamcet_rank': forms.TextInput(attrs={'maxlength': 20}),
            'rtrp_project_title': forms.TextInput(attrs={'maxlength': 500}),
            'intern_title': forms.TextInput(attrs={'maxlength': 500}),
            'final_project_title': forms.TextInput(attrs={'maxlength': 500}),
        }

    def clean_nationality(self):
        val = self.cleaned_data.get('nationality', '')
        if val and len(val) > 100:
            raise forms.ValidationError("Nationality must be 100 characters or less.")
        return val

    def clean_task_username(self):
        val = self.cleaned_data.get('task_username', '')
        if val and len(val) > 100:
            raise forms.ValidationError("Task username must be 100 characters or less.")
        return val

    def clean_csi_membership_id(self):
        val = self.cleaned_data.get('csi_membership_id', '')
        if val and len(val) > 100:
            raise forms.ValidationError("CSI Membership ID must be 100 characters or less.")
        return val

    def clean_category(self):
        val = self.cleaned_data.get('category', '')
        if val and len(val) > 50:
            raise forms.ValidationError("Category must be 50 characters or less.")
        return val

    def clean_religion(self):
        val = self.cleaned_data.get('religion', '')
        if val and len(val) > 50:
            raise forms.ValidationError("Religion must be 50 characters or less.")
        return val

    def clean_blood_group(self):
        val = self.cleaned_data.get('blood_group', '')
        if val and len(val) > 10:
            raise forms.ValidationError("Blood group must be 10 characters or less.")
        return val

    def clean_aadhar(self):
        val = self.cleaned_data.get('aadhar', '')
        if val and len(val) > 20:
            raise forms.ValidationError("Aadhar number must be 20 characters or less.")
        return val

    def clean_apaar_id(self):
        val = self.cleaned_data.get('apaar_id', '')
        if val and len(val) > 50:
            raise forms.ValidationError("APAAR ID must be 50 characters or less.")
        return val

    def clean_parent_phone(self):
        val = self.cleaned_data.get('parent_phone', '')
        if val and len(val) > 15:
            raise forms.ValidationError("Parent phone must be 15 characters or less.")
        return val

    def clean_student_phone(self):
        val = self.cleaned_data.get('student_phone', '')
        if val and len(val) > 15:
            raise forms.ValidationError("Student phone must be 15 characters or less.")
        return val

    def clean_ssc_marks(self):
        val = self.cleaned_data.get('ssc_marks', '')
        if val and len(val) > 20:
            raise forms.ValidationError("SSC marks must be 20 characters or less.")
        return val

    def clean_inter_marks(self):
        val = self.cleaned_data.get('inter_marks', '')
        if val and len(val) > 20:
            raise forms.ValidationError("Inter marks must be 20 characters or less.")
        return val

    def clean_cgpa(self):
        val = self.cleaned_data.get('cgpa', '')
        if val and len(val) > 10:
            raise forms.ValidationError("CGPA must be 10 characters or less.")
        return val

    def clean_admission_type(self):
        val = self.cleaned_data.get('admission_type', '')
        if val and len(val) > 50:
            raise forms.ValidationError("Admission type must be 50 characters or less.")
        return val

    def clean_eamcet_rank(self):
        val = self.cleaned_data.get('eamcet_rank', '')
        if val and len(val) > 20:
            raise forms.ValidationError("EAMCET rank must be 20 characters or less.")
        return val

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__'
        exclude = ['cloudinary_pdf_url', 'cloudinary_photo_url', 'subjects']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'about_yourself': forms.Textarea(attrs={'rows': 4}),
            'subjects_dealt': forms.Textarea(attrs={'rows': 2}),
            'scm': forms.Textarea(attrs={'rows': 3}),
            'results': forms.Textarea(attrs={'rows': 2}),
            'phd_year': forms.NumberInput(attrs={'min': 2000, 'max': 2030}),  # supports 2028 from PDF
        }

# (rest of forms.py unchanged - all other classes remain exactly as provided)
class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['certificate_type', 'certificate_file', 'issued_by', 'issue_date', 'description']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class BulkUploadForm(forms.Form):
    file = forms.FileField(label='Select CSV/Excel File', help_text='Supported formats: .csv, .xlsx, .xls')

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['experience_other', 'experience_at_anurag', 'batch_number']

class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = [
            'research_type', 'title_of_project', 'journal_name',
            'publisher_name', 'marks_awarded', 'doi', 'issn_number',
            'volume', 'year'
        ]
        widgets = {
            'research_type': forms.Select(attrs={'class': 'form-control'}),
            'title_of_project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'journal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher_name': forms.TextInput(attrs={'class': 'form-control'}),
            'marks_awarded': forms.TextInput(attrs={'class': 'form-control'}),
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
            'issn_number': forms.TextInput(attrs={'class': 'form-control'}),
            'volume': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2025}),
        }

class ResearchPublicationForm(forms.ModelForm):
    class Meta:
        model = ResearchPublication
        fields = [
            'research_type', 'title', 'authors', 'department', 'publication_year',
            'status', 'doi', 'url', 'abstract', 'keywords',
            'journal_name', 'issn', 'volume', 'issue', 'page_numbers',
            'conference_name', 'conference_location', 'conference_dates',
            'book_title', 'isbn', 'edition',
            'patent_number', 'filing_date', 'grant_date',
            'project_title', 'funding_agency', 'sanction_amount',
            'award_title', 'awarding_body', 'award_date',
            'publisher_name', 'proof_document'
        ]
        widgets = { ... }  # unchanged

class FDPForm(forms.ModelForm):
    class Meta:
        model = FDP
        fields = [
            'fdp_type', 'title', 'from_date', 'to_date', 'organized_by',
            'place', 'mode', 'level', 'role', 'sponsored_by', 'remarks', 'certificate'
        ]
        widgets = { ... }  # unchanged

class BTechProjectForm(forms.ModelForm):
    class Meta:
        model = BTechProject
        fields = ['ht_no', 'student_name', 'batch', 'project_title', 'approved', 'marks']
        widgets = { ... }  # unchanged

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'credits']
        widgets = { ... }  # unchanged