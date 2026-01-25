from rest_framework import serializers
from .models import ModelSupplier

class SupplierSerializer(serializers.ModelSerializer):
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