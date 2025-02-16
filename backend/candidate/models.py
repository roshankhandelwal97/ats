from django.db import models
from django.conf import settings

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )
    # We can store resume as structured JSON or plain text
    resume_data = models.JSONField(null=True, blank=True)
    # Additional fields if needed
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
