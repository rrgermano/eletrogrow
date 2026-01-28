from rest_framework import serializers
from .models import ModelInflow

class InflowSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
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

class QuerySetInflowSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, )
    end_date = serializers.DateField(required=False)
    paid = serializers.ChoiceField(choices=('paid', 'not_paid', 'all'), required=False)
    refund = serializers.ChoiceField(choices=('refund', 'not_refund', 'all'), required=False)
