from rest_framework import serializers
from .models import ModelInflow

class InflowSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    class Meta:
        model = ModelInflow
        fields = [
            'id',
            'income',
            'paid',
            'project',
            'project_name',
            'due_date',
            'payment_method',
            'value',
            'refund',
            'paid_date',
        ]

    read_only_fields = ['paid_date']
    ordering = ['id']