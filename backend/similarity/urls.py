from django.urls import path
from .views import JobCandidatesRankingView

urlpatterns = [
    path('job/<int:job_id>/ranking/', JobCandidatesRankingView.as_view(), name='job-candidates-ranking'),
]
