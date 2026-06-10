from __future__ import annotations

from django.db import models


class StudentRegistration(models.Model):
    full_name = models.CharField(max_length=120)
    roll_number = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=120, blank=True)
    college = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.full_name} ({self.roll_number})"


class ExecutionLog(models.Model):
    algorithm = models.CharField(max_length=120)
    dataset = models.CharField(max_length=120)
    rows_executed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.algorithm} on {self.dataset}"
