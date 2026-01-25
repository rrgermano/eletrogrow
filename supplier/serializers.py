from rest_framework import serializers
from .models import ModelSupplier
from rest_framework.validators import UniqueValidator

class SupplierSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[UniqueValidator(queryset=ModelSupplier.objects.all(), lookup='iexact', message='Fornecedor com este nome já existe')])
    class Meta:
        model = ModelSupplier
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'address',
            'city',
            'state',
            'cep',
            'cpf',
            'cnpj',
        ]

        only_read_fields = ['id']
    
        