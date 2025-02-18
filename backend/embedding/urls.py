# embedding/urls.py
from django.urls import path
from .views import ResumeEmbeddingView, JDEmbeddingView, CreateIndexView


urlpatterns = [
    path("resume/", ResumeEmbeddingView.as_view(), name="embedding-resume"),
    path("jd/", JDEmbeddingView.as_view(), name="embedding-jd"),
    path("createIdx/", CreateIndexView.as_view(), name= "create-pinecone-Index"),
]
