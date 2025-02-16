# job/models.py

from django.db import models
from django.conf import settings

class Job(models.Model):
    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Store the raw JD file (PDF, DOCX, etc.)
    jd_document = models.FileField(upload_to='jd_files/', null=True, blank=True)

    # Optionally store a JSON representation once parsed.
    jd_file = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.poster.username})"
