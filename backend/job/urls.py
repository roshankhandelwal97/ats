from django.urls import path
from .views import JobCreateView, JobListView, JobDetailView

urlpatterns = [
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('', JobListView.as_view(), name='job-list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job-detail'),
]
