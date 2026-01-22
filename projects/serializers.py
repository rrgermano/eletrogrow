from rest_framework import serializers
from .models import ModelProject

class ProjectSerializer(serializers.ModelSerializer):
    costumer_name = serializers.ReadOnlyField(source='client.name')

    class Meta:
        model = ModelProject
        fields = [
            'id',
            'name',
            'client',
            'costumer_name',
            'start_project',
            'start_work',
            'end_project',
            'parcel',
            'value',
            'due_date',
            'description',
        ]

        # def to_reprentation(self, instance):
        #     repr = super().to_representation(instance)
        #     repr['client'] =
