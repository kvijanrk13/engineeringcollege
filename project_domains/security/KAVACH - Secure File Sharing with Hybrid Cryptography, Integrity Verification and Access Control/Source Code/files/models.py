from django.db import models
from django.contrib.auth.models import User


class PlainTextFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plain_text_files")
    original_name = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to="plain_text_files/")
    file_size = models.PositiveIntegerField(default=0)
    preview_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name
