from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'ht_no',
        'student_name',
        'gender',
        'year',
        'sem',
        'student_phone',
        'cgpa',
    )

    list_filter = (
        'gender',
        'year',
        'sem',
    )

    search_fields = (
        'ht_no',
        'student_name',
        'student_phone',
        'email',
    )

    ordering = ('ht_no',)
