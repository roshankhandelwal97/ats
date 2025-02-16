import os
import tempfile
from rest_framework import generics, status, parsers, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Job
from .serializers import JobSerializer
from user.permissions import IsJobUser  # We'll create a custom permission

from user.permissions import IsJobUser
from .models import Job
from .serializers import JobSerializer

from embedding.utils.file_parser import parse_file
from embedding.utils.openai_client import generate_embedding, extract_structured_data
from embedding.utils.pinecone_client import upsert_embedding


class JobCreateView(generics.CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        # Save the job with basic data first.
        serializer.save(poster=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Overriding create() so we can handle the JD file + embedding logic.
        """
        jd_file = request.FILES.get("jd_file")
        if not jd_file:
            # If your logic requires an actual file, throw an error or fallback.
            return Response({"error": "No jd_file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        tmp_file_path = None
        try:
            # Save job basic fields (title, description, etc.)
            response = super().create(request, *args, **kwargs)
            job_id = response.data.get("id")
            if not job_id:
                return response  # Some error occurred in serializer validation
            
            # 1. Save JD file to temp
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.name)[1]) as tmp:
                for chunk in jd_file.chunks():
                    tmp.write(chunk)
                tmp_file_path = tmp.name

            # 2. Parse raw text
            raw_text = parse_file(tmp_file_path)

            # 3. Generate embeddings
            embedding = generate_embedding(raw_text)

            # 4. Upsert embedding
            doc_id = f"job-{job_id}-jd"
            upsert_embedding(doc_id, embedding, metadata={"type": "jd", "job_id": job_id})

            # 5. Extract structured JSON
            structured_json = extract_structured_data(raw_text, role="jd")

            # 6. Update job record with structured data
            job_instance = Job.objects.get(pk=job_id)
            job_instance.jd_file = structured_json
            job_instance.save()

            # Merge the original response data with the structured JD
            merged_data = response.data
            merged_data["structured_jd"] = structured_json

            return Response(merged_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        # The job poster is the currently authenticated user
        serializer.save(poster=self.request.user)

    def create(self, request, *args, **kwargs):
        # We override create() if we want custom responses or extra logic
        response = super().create(request, *args, **kwargs)
        job_id = response.data.get("id")
        if job_id:
            # Optionally, you can do post-processing like generating a "token" or additional fields
            pass
        return response

class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobUser]

    def get_queryset(self):
        # Return only the jobs posted by the current user
        return Job.objects.filter(poster=self.request.user)

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobUser]
    queryset = Job.objects.all()

    def get_queryset(self):
        # The job user can only access their own jobs
        return Job.objects.filter(poster=self.request.user)


class JDUploadView(APIView):
    """
    Upload a Job Description (JD) file.
    - If job_id is provided, attach JD to existing job (must belong to the current user).
    - Otherwise, create a new job record with minimal fields (title/description can be blank).
    
    Future logic can parse the JD file and store structured data in jd_file.
    """
    permission_classes = [permissions.IsAuthenticated, IsJobUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        job_id = request.data.get("job_id", None)
        jd_file = request.FILES.get("jd_file", None)

        if not jd_file:
            return Response({"error": "No JD file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Retrieve or create a Job instance
        if job_id:
            # Ensure the job belongs to the current user
            job = get_object_or_404(Job, pk=job_id, poster=request.user)
        else:
            # Create a new job with blank title/description
            job = Job.objects.create(poster=request.user, title="", description="")

        temp_file_path = None
        try:
            # Step 2: Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.name)[1]) as tmp:
                for chunk in jd_file.chunks():
                    tmp.write(chunk)
                temp_file_path = tmp.name

            # Step 3: (Future) Parse the JD file → structured JSON
            # raw_text = parse_file(temp_file_path)
            # structured_data = jd_formatter.format_jd_text(raw_text)
            # For now, just store minimal info (like file name)
            structured_data = {
                "filename": jd_file.name,
                "size": jd_file.size,
                # "content": raw_text (if you want)
            }

            # Step 4: Save to the job’s jd_file field
            job.jd_file = structured_data
            job.save()

            # Return updated job info
            serializer = JobSerializer(job)
            return Response(
                {"message": "JD file uploaded", "job": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

