from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from user.permissions import IsCandidateUser, IsJobUser
from candidate.models import CandidateProfile
from job.models import Job
from .utils import compute_similarity

class JobCandidatesRankingView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsJobUser]
    
    def get(self, request, job_id):
        # Ensure the job belongs to the current user
        try:
            job = Job.objects.get(pk=job_id, poster=request.user)
        except Job.DoesNotExist:
            return Response({"error": "Job not found or not yours"}, status=status.HTTP_404_NOT_FOUND)
        
        # Suppose we have an ApplicationMapping or something to show which candidates applied
        # For simplicity, we rank all candidate profiles
        candidates = CandidateProfile.objects.select_related('user').all()
        results = []
        for c in candidates:
            sim = compute_similarity(c.resume_data, job.jd_file)
            results.append({
                "candidate_id": c.user.id,
                "candidate_username": c.user.username,
                "similarity_score": sim
            })
        # Sort descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return Response(results, status=status.HTTP_200_OK)
