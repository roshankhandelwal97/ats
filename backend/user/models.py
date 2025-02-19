from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('job', 'Job'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')

    def __str__(self):
        return f"{self.username} ({self.role})"


#New Models to store resume and jd information
#Author Tanmay

class ResumeEmbedding(models.Model):
    """
    Stores resume embeddings with a reference to the user.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resumes')
    resume_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)  # Unique ID (stored in Pinecone)
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"Resume {self.resume_id} of {self.user.username}"


class JobEmbedding(models.Model):
    """
    Stores job description embeddings with a reference to the user.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_embeddings')
    job_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)  # Unique ID (stored in Pinecone)
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"Job {self.job_id} of {self.user.username}"