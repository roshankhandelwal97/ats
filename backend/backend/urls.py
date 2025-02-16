from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),            # Registration, login, profile
    path('api/job/', include('job.urls')),              # Job creation, listing, detail
    path('api/candidate/', include('candidate.urls')),  # Resume upload, candidate profile
    path('api/similarity/', include('similarity.urls')),# Ranking, matching
    path("api/embedding/", include("embedding.urls")),
]
