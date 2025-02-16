from rest_framework import serializers
from .models import CandidateProfile

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['id', 'resume_data', 'updated_at']
        read_only_fields = ['id', 'updated_at']
