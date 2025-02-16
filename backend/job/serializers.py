# job/serializers.py

from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    # This field allows uploading a JD file along with other job data
    jd_document = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'jd_document', 'jd_file', 'created_at']
        read_only_fields = ['id', 'created_at', 'jd_file']

    def create(self, validated_data):
        jd_doc = validated_data.pop('jd_document', None)
        job = Job.objects.create(**validated_data)
        
        if jd_doc:
            job.jd_document = jd_doc
            job.save()
        
        return job
