# dashboard/forms.py

from django import forms
from .models import Faculty, Student, Certificate


# =====================================================
# LOGIN FORM
# =====================================================

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        })
    )


# =====================================================
# FACULTY FORM
# =====================================================

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = [
            'staff_name',
            'employee_code',
            'department',
            'designation',
            'email',
            'phone',
            'mobile',
            'dob',
            'joining_date',
            'gender',
            'address',
            'father_name',
            'state',
            'aadhar',
            'pan',
            'jntuh_id',
            'aicte_id',

            # Education
            'ug_degree',
            'ug_year',
            'ug_percentage',
            'ug_college',
            'ug_spec',

            'pg_degree',
            'pg_year',
            'pg_percentage',
            'pg_college',
            'pg_spec',

            'phd_degree',
            'phd_year',
            'phd_university',
            'phd_spec',

            'ssc_year',
            'ssc_percent',
            'ssc_school',

            'inter_year',
            'inter_percent',
            'inter_college',

            # Experience
            'total_experience',
            'exp_anurag',
            'exp_other',

            # Other
            'subjects_dealt',
            'about_yourself',

            # Files
            'photo',
            'pdf_document',

            # Status
            'is_active',
        ]

        widgets = {
            'staff_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'employee_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Code'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(
                choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                attrs={'class': 'form-control'}
            ),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aadhar Number'}),
            'pan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN Number'}),
            'jntuh_id': forms.TextInput(attrs={'class': 'form-control'}),
            'aicte_id': forms.TextInput(attrs={'class': 'form-control'}),

            'ug_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'ug_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'ug_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ug_college': forms.TextInput(attrs={'class': 'form-control'}),
            'ug_spec': forms.TextInput(attrs={'class': 'form-control'}),

            'pg_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'pg_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'pg_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pg_college': forms.TextInput(attrs={'class': 'form-control'}),
            'pg_spec': forms.TextInput(attrs={'class': 'form-control'}),

            'phd_degree': forms.Select(attrs={'class': 'form-control'}),
            'phd_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'phd_university': forms.TextInput(attrs={'class': 'form-control'}),
            'phd_spec': forms.TextInput(attrs={'class': 'form-control'}),

            'ssc_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'ssc_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ssc_school': forms.TextInput(attrs={'class': 'form-control'}),

            'inter_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'inter_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inter_college': forms.TextInput(attrs={'class': 'form-control'}),

            'total_experience': forms.TextInput(attrs={'class': 'form-control'}),
            'exp_anurag': forms.TextInput(attrs={'class': 'form-control'}),
            'exp_other': forms.TextInput(attrs={'class': 'form-control'}),

            'subjects_dealt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'about_yourself': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),

            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'pdf_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# =====================================================
# STUDENT FORM
# =====================================================

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'ht_no', 'student_name', 'father_name', 'mother_name',
            'gender', 'dob', 'age', 'nationality', 'category', 'religion',
            'blood_group', 'aadhar', 'apaar_id', 'address',
            'parent_phone', 'student_phone', 'email',
            'task_registered', 'task_username',
            'csi_registered', 'csi_membership_id',
            'admission_type', 'other_admission_details', 'eamcet_rank',
            'year', 'sem', 'ssc_marks', 'inter_marks', 'cgpa',
            'rtrp_project_title', 'intern_title', 'final_project_title',
            'other_training', 'photo',
        ]

        widgets = {
            'ht_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hall Ticket Number'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(
                choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                attrs={'class': 'form-control'}
            ),
            'dob': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DD-MM-YYYY'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhar': forms.TextInput(attrs={'class': 'form-control'}),
            'apaar_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'student_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'task_registered': forms.TextInput(attrs={'class': 'form-control'}),
            'task_username': forms.TextInput(attrs={'class': 'form-control'}),
            'csi_registered': forms.TextInput(attrs={'class': 'form-control'}),
            'csi_membership_id': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_type': forms.TextInput(attrs={'class': 'form-control'}),
            'other_admission_details': forms.TextInput(attrs={'class': 'form-control'}),
            'eamcet_rank': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'sem': forms.NumberInput(attrs={'class': 'form-control'}),
            'ssc_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'inter_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rtrp_project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'intern_title': forms.TextInput(attrs={'class': 'form-control'}),
            'final_project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'other_training': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
            'description',
        ]

        widgets = {
            'certificate_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. FDP, Workshop, Conference'
            }),
            'certificate_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issuing Organization'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# =====================================================
# BULK UPLOAD FORM
# =====================================================

class BulkUploadForm(forms.Form):
    file = forms.FileField(
        label='Upload CSV / Excel File',
        help_text='Supported formats: .csv, .xlsx, .xls',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'})
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            name = file.name.lower()
            if not (name.endswith('.csv') or name.endswith('.xlsx') or name.endswith('.xls')):
                raise forms.ValidationError('Only CSV and Excel files (.csv, .xlsx, .xls) are supported.')
        return file