from rest_framework import serializers
from .models import ModelOutflow, ModelCreditOutflow, OutflowTypeChoice

class OutflowSerializer(serializers.ModelSerializer):
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
    class Meta:
        model = ModelOutflow
        fields = [
            'id',
            'expense',
            'favored',
            'paid',
            'type',
            'date',
            'payment_method',
            'project',
            'value',
            'update_time'
        ]

        read_only_fields = ['id', 'update_time']

class OutflowCreditSerializer(serializers.ModelSerializer):
    installments = serializers.IntegerField(
        write_only=True,
        required=False,
        default=1,
        min_value=1,
        help_text="Número de parcelas (1 = à vista)",
        label='Parcelas'
    )
    value = serializers.FloatField(min_value=0.01)
    class Meta:
        model = ModelCreditOutflow
        fields = [
            'id',
            'expense',
            'favored',
            'type',
            'date',
            'project',
            'value',
            'closing',
            'installments',
            'update_time',
        ]
        read_only_fields = ['id', 'update_time', 'closing']

    def create(self, validated_data):
        # Remove installments dos dados validados
        num_installments = validated_data.pop('installments', 1)
        types_list = validated_data.pop('type', [])

        # Cria a instância (ainda não salva)
        instance = ModelCreditOutflow(**validated_data)

        # Gera parcelas (já salva tudo)
        instance.generate_installments(num_installments, types_list)

        return instance

    def to_representation(self, instance):
        """Personaliza a resposta para mostrar info de parcelamento"""
        data = super().to_representation(instance)

        # Detecta se é parcelado pelo formato do expense
        if '-' in instance.expense and '/' in instance.expense:
            try:
                # Extrai "1/3" do "Descrição (1/3)"
                parcel_info = instance.expense[instance.expense.rfind('-') + 2:]
                current, total = parcel_info.split('/')
                data['installment_info'] = {
                    'current': int(current),
                    'total': int(total),
                    'is_installment': True
                }
            except:
                data['installment_info'] = {'is_installment': False}
        else:
            data['installment_info'] = {'is_installment': False}

        return data
class OutflowTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutflowTypeChoice
        fields = [
            'id',
            'name',
        ]

        read_only_fields = ['id']

class QuerySetOutflowSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    paid = serializers.ChoiceField(choices=('paid', 'not_paid', 'all'), required=False)
    refund = serializers.ChoiceField(choices=('refund', 'not_refund', 'all'), required=False)
