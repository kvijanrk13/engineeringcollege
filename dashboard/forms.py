# dashboard/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import (
    Faculty, Certificate, Student, Subject,
    FacultyProfile, ResearchProject, CloudinaryUpload,
    ResearchPublication, FDP, BTechProject
)
import datetime


# ==================== LOGIN FORM ====================

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


# ==================== FACULTY FORM ====================

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__'
        exclude = ['cloudinary_photo_url', 'cloudinary_pdf_url', 'created_at', 'updated_at']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ssc_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'ssc_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inter_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'inter_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ug_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'ug_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pg_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'pg_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'phd_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'subjects_dealt': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'scm': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'about_yourself': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'results': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ==================== FACULTY PROFILE FORM ====================

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['experience_other', 'experience_at_anurag', 'batch_number']
        widgets = {
            'experience_other': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_at_anurag': forms.TextInput(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ==================== CERTIFICATE FORM ====================

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['certificate_type', 'certificate_file', 'issued_by', 'issue_date', 'description']
        widgets = {
            'certificate_type': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


# ==================== RESEARCH PROJECT FORM ====================

class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = ['research_type', 'title_of_project', 'marks_awarded', 'journal_name',
                  'issn_number', 'volume', 'doi', 'publisher_name', 'upload_pdf']
        widgets = {
            'research_type': forms.Select(attrs={'class': 'form-control'}),
            'title_of_project': forms.TextInput(attrs={'class': 'form-control'}),
            'marks_awarded': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'journal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'issn_number': forms.TextInput(attrs={'class': 'form-control'}),
            'volume': forms.TextInput(attrs={'class': 'form-control'}),
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher_name': forms.TextInput(attrs={'class': 'form-control'}),
            'upload_pdf': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ==================== RESEARCH PUBLICATION FORM ====================

class ResearchPublicationForm(forms.ModelForm):
    class Meta:
        model = ResearchPublication
        fields = '__all__'
        exclude = ['faculty', 'created_at', 'updated_at']
        widgets = {
            'research_type': forms.Select(attrs={'class': 'form-control', 'onchange': 'showResearchFields()'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'publisher_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'proof_document': forms.FileInput(attrs={'class': 'form-control'}),

            # Journal fields
            'journal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'issn': forms.TextInput(attrs={'class': 'form-control'}),
            'e_issn': forms.TextInput(attrs={'class': 'form-control'}),
            'volume': forms.TextInput(attrs={'class': 'form-control'}),
            'issue': forms.TextInput(attrs={'class': 'form-control'}),
            'page_numbers': forms.TextInput(attrs={'class': 'form-control'}),
            'impact_factor': forms.TextInput(attrs={'class': 'form-control'}),
            'quartile': forms.Select(attrs={'class': 'form-control'}),
            'indexed_in': forms.TextInput(attrs={'class': 'form-control'}),

            # Conference fields
            'conference_name': forms.TextInput(attrs={'class': 'form-control'}),
            'conference_type': forms.Select(attrs={'class': 'form-control'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control'}),
            'conference_location': forms.TextInput(attrs={'class': 'form-control'}),
            'conference_dates': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10-12 Jan 2024'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'proceedings_title': forms.TextInput(attrs={'class': 'form-control'}),
            'presentation_type': forms.Select(attrs={'class': 'form-control'}),

            # Book fields
            'book_title': forms.TextInput(attrs={'class': 'form-control'}),
            'edition': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_place': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'book_type': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),

            # Book Chapter fields
            'chapter_title': forms.TextInput(attrs={'class': 'form-control'}),
            'chapter_number': forms.TextInput(attrs={'class': 'form-control'}),
            'editors': forms.TextInput(attrs={'class': 'form-control'}),

            # Patent fields
            'patent_title': forms.TextInput(attrs={'class': 'form-control'}),
            'inventors': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'applicant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patent_number': forms.TextInput(attrs={'class': 'form-control'}),
            'application_number': forms.TextInput(attrs={'class': 'form-control'}),
            'filing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'grant_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'patent_status': forms.Select(attrs={'class': 'form-control'}),
            'patent_office': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'patent_type': forms.Select(attrs={'class': 'form-control'}),
            'license_details': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),

            # Project fields
            'project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'principal_investigator': forms.TextInput(attrs={'class': 'form-control'}),
            'co_investigators': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'funding_agency': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'sanction_number': forms.TextInput(attrs={'class': 'form-control'}),
            'sanction_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fund_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_status': forms.Select(attrs={'class': 'form-control'}),
            'outcomes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),

            # Copyright fields
            'copyright_registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'copyright_registration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'copyright_office': forms.TextInput(attrs={'class': 'form-control'}),
            'copyright_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),

            # Award fields
            'award_title': forms.TextInput(attrs={'class': 'form-control'}),
            'awarding_body': forms.TextInput(attrs={'class': 'form-control'}),
            'award_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'award_level': forms.Select(attrs={'class': 'form-control'}),
            'award_description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ==================== FDP FORM ====================

class FDPForm(forms.ModelForm):
    class Meta:
        model = FDP
        fields = '__all__'
        exclude = ['faculty', 'created_at', 'updated_at']
        widgets = {
            'fdp_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'from_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'to_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'organized_by': forms.TextInput(attrs={'class': 'form-control'}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'mode': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'sponsored_by': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_upload': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ==================== B.TECH PROJECT FORM ====================

class BTechProjectForm(forms.ModelForm):
    class Meta:
        model = BTechProject
        fields = '__all__'
        exclude = ['faculty', 'created_at', 'updated_at']
        widgets = {
            'ht_no': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'batch': forms.TextInput(attrs={'class': 'form-control'}),
            'project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'approved': forms.Select(choices=[(True, 'Yes'), (False, 'No')], attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


# ==================== STUDENT FORM ====================

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['photo_url', 'pdf_url', 'pdf_generated', 'pdf_generation_time', 'created_at', 'updated_at']
        widgets = {
            'ht_no': forms.TextInput(attrs={'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhar': forms.TextInput(attrs={'class': 'form-control'}),
            'apaar_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'student_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.Select(attrs={'class': 'form-control'}),
            'sem': forms.Select(attrs={'class': 'form-control'}),
            'admission_type': forms.TextInput(attrs={'class': 'form-control'}),
            'other_admission_details': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'eamcet_rank': forms.TextInput(attrs={'class': 'form-control'}),
            'task_registered': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'form-control'}),
            'task_username': forms.TextInput(attrs={'class': 'form-control'}),
            'csi_registered': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'form-control'}),
            'csi_membership_id': forms.TextInput(attrs={'class': 'form-control'}),
            'ssc_marks': forms.TextInput(attrs={'class': 'form-control'}),
            'inter_marks': forms.TextInput(attrs={'class': 'form-control'}),
            'cgpa': forms.TextInput(attrs={'class': 'form-control'}),
            'rtrp_project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'intern_title': forms.TextInput(attrs={'class': 'form-control'}),
            'final_project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'other_training': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_achieve': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_intern': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_courses': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_sdp': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_extra': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_placement': forms.FileInput(attrs={'class': 'form-control'}),
            'cert_national': forms.FileInput(attrs={'class': 'form-control'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ==================== BULK UPLOAD FORM ====================

class BulkUploadForm(forms.Form):
    file = forms.FileField(
        label='Select CSV or Excel file',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'})
    )