from django.urls import path
from .views import ResumeUploadView, CandidateProfileView

urlpatterns = [
    path('resume/upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('profile/', CandidateProfileView.as_view(), name='candidate-profile'),
]
