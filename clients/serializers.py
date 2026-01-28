from rest_framework import serializers
from .models import ModelClient
from projects.utils import project_name
from projects.models import ModelProject

class ClientSerializer(serializers.ModelSerializer):
    next_project = serializers.SerializerMethodField()
    class Meta:
        model = ModelClient
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'address',
            'neighborhood',
            'city',
            'state',
            'cep',
            'cpf',
            'cnpj',
            'next_project',
        ]
    def get_next_project(self, obj):
        return project_name(obj, ModelProject)