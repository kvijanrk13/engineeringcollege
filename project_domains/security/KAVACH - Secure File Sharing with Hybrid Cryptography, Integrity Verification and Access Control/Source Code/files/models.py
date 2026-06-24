from django.db import models
from django.contrib.auth.models import User


class PlainTextFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plain_text_files")
    receiver_email = models.EmailField(blank=True, db_index=True)
    original_name = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to="encrypted_files/")
    file_size = models.PositiveIntegerField(default=0)
    preview_text = models.TextField(blank=True)
    sha256_hash = models.CharField(max_length=64, blank=True, db_index=True)
    aes_key = models.CharField(max_length=64, blank=True)
    aes_nonce = models.CharField(max_length=32, blank=True)
    encryption_algorithm = models.CharField(max_length=20, default="AES-GCM")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name
