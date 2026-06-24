from django.contrib import admin
from .models import PlainTextFile


@admin.register(PlainTextFile)
class PlainTextFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "owner", "receiver_email", "file_size", "encryption_algorithm", "sha256_hash", "uploaded_at")
    search_fields = ("original_name", "owner__username", "owner__email", "receiver_email", "sha256_hash")
    list_filter = ("encryption_algorithm", "uploaded_at")
