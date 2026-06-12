from django.contrib import admin
from .models import PlainTextFile


@admin.register(PlainTextFile)
class PlainTextFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "owner", "file_size", "uploaded_at")
    search_fields = ("original_name", "owner__username")
    list_filter = ("uploaded_at",)
