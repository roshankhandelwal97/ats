import os
import tempfile
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers, permissions

from .utils.openai_client import generate_embedding, extract_structured_data
from .utils.file_parser import parse_file  # hypothetical PDF/DOCX parser
from .utils.pinecone_client import create_index_resume, upsert_embedding_resume, upsert_embedding_jd, get_All_VectorId

class ResumeEmbeddingView(APIView):
    """    
    Endpoint to:
    1. Parse the uploaded resume file.
    2. Generate embeddings (store in Pinecone).
    3. Extract structured data from OpenAI.
    4. Return structured JSON response.
    """
    permission_classes = [permissions.IsAuthenticated]  # or custom permission (IsCandidateUser)
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        resume_file = request.FILES.get("resume_file")
        if not resume_file:
            return Response({"error": "No resume_file provided"}, status=status.HTTP_400_BAD_REQUEST)

        tmp_file_path = None
        try:
            # 1. Save to a temp file & parse
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.name)[1]) as tmp:
                for chunk in resume_file.chunks():
                    tmp.write(chunk)
                tmp_file_path = tmp.name
            
            raw_text = parse_file(tmp_file_path)
            
            # 2. Generate embeddings
            embedding = generate_embedding(raw_text)
            
            # Suppose we store the embedding in Pinecone with doc_id = userID-resumeID, etc.
            #doc_id = f"resume-{request.user.id}"

            #Changed the logic to create unique doc id everytime
            user = request.user
            print("User ID"+str(request.user.id))
            doc_id = f"resume-{request.user.id}-{str(uuid.uuid4())[:8]}"
            upsert_embedding_resume(user,doc_id, embedding, metadata={"role": "resume", "user_id": request.user.id})

            # 3. Extract structured JSON
            structured_output = extract_structured_data(raw_text, role="resume")
            
            return Response({
                "message": "Resume processed",
                "embedding_upserted": True,
                "structured_json": structured_output
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    #Function added by Tanmay to fetch the ids of vector embedding stored in pinecone
    def get(self, request):
        try:
            embedding_ids = get_All_VectorId()
            return Response({"embedding_ids": embedding_ids}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JDEmbeddingView(APIView):
    """
    Similar logic for Job Description files.
    """
    permission_classes = [permissions.IsAuthenticated]  # or custom permission (IsJobUser)
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        jd_file = request.FILES.get("jd_file")
        if not jd_file:
            return Response({"error": "No jd_file provided"}, status=status.HTTP_400_BAD_REQUEST)

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.name)[1]) as tmp:
                for chunk in jd_file.chunks():
                    tmp.write(chunk)
                tmp_file_path = tmp.name

            raw_text = parse_file(tmp_file_path)

            embedding = generate_embedding(raw_text)
            #doc_id = f"jd-{request.user.id}"
            doc_id = f"jd-{request.user.id}-{str(uuid.uuid4())[:8]}"
            upsert_embedding_jd(doc_id, embedding, metadata={"role": "jd", "user_id": request.user.id})

            structured_output = extract_structured_data(raw_text, role="jd")

            return Response({
                "message": "Job Description processed",
                "embedding_upserted": True,
                "structured_json": structured_output
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)


class CreateIndexView(APIView):
    """
    API Endpoint to create a new Pinecone index.
    """
    #permission_classes = [permissions.IsAdminUser]  # Restrict to admin users
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        index_name = request.data.get("index_name")
        # dimensions = request.data.get("dimensions", 1536)  # Default to OpenAI's dimension
        # metric = request.data.get("metric", "cosine")  # Default metric

        if not index_name:
            return Response({"error": "Index name is required."}, status=status.HTTP_400_BAD_REQUEST)

        result = create_index_resume(index_name)
        return Response(result, status=status.HTTP_201_CREATED)