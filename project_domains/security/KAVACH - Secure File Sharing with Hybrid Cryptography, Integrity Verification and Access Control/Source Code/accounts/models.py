from django.db import models
from django.contrib.auth.models import User


class UserKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="key_pair")
    public_key = models.TextField(help_text="Public key shared with other users.")
    encrypted_private_key = models.TextField(help_text="Private key encrypted with the user's password.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Key pair for {self.user.username}"
