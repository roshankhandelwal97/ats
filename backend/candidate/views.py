import os, tempfile
from rest_framework import generics, status, permissions, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CandidateProfile
from .serializers import CandidateProfileSerializer
from user.permissions import IsCandidateUser
from candidate.models import CandidateProfile
from candidate.serializers import CandidateProfileSerializer
from embedding.utils.file_parser import parse_file
from embedding.utils.openai_client import generate_embedding, extract_structured_data
from embedding.utils.pinecone_client import upsert_embedding



class ResumeUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCandidateUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        resume_file = request.FILES.get("resume_file")
        if not resume_file:
            return Response({"error": "No resume file provided."}, status=status.HTTP_400_BAD_REQUEST)

        tmp_file_path = None
        try:
            # 1. Save file to temp
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.name)[1]) as tmp:
                for chunk in resume_file.chunks():
                    tmp.write(chunk)
                tmp_file_path = tmp.name
            
            # 2. Parse raw text from file
            raw_text = parse_file(tmp_file_path)
            
            # 3. Generate embeddings
            embedding = generate_embedding(raw_text)

            # 4. Upsert embedding to vector DB (e.g., Pinecone)
            doc_id = f"candidate-{request.user.id}-resume"
            upsert_embedding(doc_id, embedding, metadata={"type": "resume", "candidate_id": request.user.id})

            # 5. Extract structured JSON from OpenAI (resume fields)
            structured_json = extract_structured_data(raw_text, role="resume")

            # 6. Store in candidate profile model (create if needed)
            profile, created = CandidateProfile.objects.get_or_create(user=request.user)
            # For a single resume, you can just store it in a JSONField:
            profile.resume_data = structured_json
            profile.save()

            return Response({
                "message": "Resume uploaded and processed successfully",
                "structured_resume": structured_json
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    permission_classes = [permissions.IsAuthenticated, IsCandidateUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        if not request.FILES.get('resume_file'):
            return Response({"error": "No resume file provided."}, status=status.HTTP_400_BAD_REQUEST)

        resume_file = request.FILES['resume_file']

        # Save to temp file, parse, convert to JSON, etc.
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.name)[1]) as tmp:
                for chunk in resume_file.chunks():
                    tmp.write(chunk)
                temp_file_path = tmp.name
            
            # Parse the resume (using hypothetical util)
            # raw_text = parse_file(temp_file_path)
            # structured_data = format_resume_text(raw_text)

            # For now, we'll just simulate
            structured_data = {"skills": ["Python", "Django"], "experience": "3+ years"}

            # Save or update candidate profile
            profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
            profile.resume_data = structured_data
            profile.save()

            return Response({"message": "Resume uploaded and parsed", "resume_data": structured_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

class CandidateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidateUser]

    def get_object(self):
        profile, created = CandidateProfile.objects.get_or_create(user=self.request.user)
        return profile

# Additional logic to see job listings might go here or in the similarity app.
