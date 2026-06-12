from django.contrib import admin
from .models import UserKey


@admin.register(UserKey)
class UserKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "key_source", "created_at", "updated_at")
    list_filter = ("key_source", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
