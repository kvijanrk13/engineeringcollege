from __future__ import annotations

from django.db import models


class ExecutionLog(models.Model):
    algorithm = models.CharField(max_length=120)
    dataset = models.CharField(max_length=120)
    rows_executed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.algorithm} on {self.dataset}"
