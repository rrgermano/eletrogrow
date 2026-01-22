from rest_framework import serializers
from .models import ModelService

class ServiceSerializer(serializers.ModelSerializer):
    costumer_name = serializers.ReadOnlyField(source='project.client.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    value = serializers.ReadOnlyField(source='project.value')

    class Meta:
        model = ModelService
        fields = [
            'id',
            'project',
            'project_name',
            'costumer_name',
            'service_type',
            'description',
            'closing',
            'date',
            'last_changes',
            'status',
            'value',
        ]