from rest_framework import serializers
from outflows.models import ModelOutflow
from inflows.models import ModelInflow


# Assumindo que você tem um model de Task - ajuste se necessário
# from tasks.models import ModelTask

class UpcomingOutflowSerializer(serializers.ModelSerializer):
    """
    Serializer para despesas próximas do vencimento.
    Adiciona campos calculados úteis para o dashboard.
    """
    days_until_due = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    favored_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    type_names = serializers.SerializerMethodField()

    class Meta:
        model = ModelOutflow
        fields = [
            'id',
            'expense',
            'favored_name',
            'value',
            'date',
            'days_until_due',
            'paid',
            'status_label',
            'payment_method',
            'project_name',
            'type_names',
        ]

    def get_days_until_due(self, obj):
        """Calcula quantos dias faltam para o vencimento"""
        from datetime import date
        delta = obj.date - date.today()
        return delta.days

    def get_status_label(self, obj):
        """Retorna label amigável do status"""
        if obj.paid:
            return 'Pago'

        from datetime import date
        delta = obj.date - date.today()
        days = delta.days

        if days < 0:
            return 'Vencido'
        elif days == 0:
            return 'Vence hoje'
        elif days == 1:
            return 'Vence amanhã'
        else:
            return f'Vence em {days} dias'

    def get_favored_name(self, obj):
        """Retorna nome do favorecido ou None"""
        return obj.favored.name if obj.favored else None

    def get_project_name(self, obj):
        """Retorna nome do projeto ou None"""
        return obj.project.name if obj.project else None

    def get_type_names(self, obj):
        """Retorna lista de nomes dos tipos"""
        return [t.name for t in obj.type.all()]


# ============================================================================
# NOVOS SERIALIZERS PARA AS 3 VIEWS
# ============================================================================

class MaturitySerializer(serializers.Serializer):
    """Serializer para vencimentos (outflows e inflows)"""
    id = serializers.IntegerField()
    description = serializers.CharField()
    due_date = serializers.DateField()
    value = serializers.FloatField()
    type = serializers.CharField()  # "OUTFLOW" ou "INFLOW"


class TaskSerializer(serializers.Serializer):
    """Serializer para tarefas"""
    id = serializers.IntegerField()
    description = serializers.CharField()
    date = serializers.DateField()
    project_name = serializers.CharField()


class UpcomingDataSerializer(serializers.Serializer):
    """Serializer principal para /dashboard/upcoming/"""
    maturities = MaturitySerializer(many=True)
    tasks = TaskSerializer(many=True)


class MonthlySummarySerializer(serializers.Serializer):
    """Serializer para /dashboard/summary/"""
    monthly_inflow = serializers.FloatField()
    monthly_outflow = serializers.FloatField()
    credit_card_month_total = serializers.FloatField()
    approved_projects_count = serializers.IntegerField()

class ListLabelValueSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.FloatField()
class EarningsListLabelValueSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.FloatField()
    inflows_ids = serializers.ListSerializer(child=serializers.IntegerField(), required=False)
    outflows_ids = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

class EarningsPeriodSerializer(serializers.Serializer):
    """Serializer para ganhos por período (lista de pontos do gráfico)"""
    earnings = EarningsListLabelValueSerializer(many=True)
    period_average = serializers.DecimalField(max_digits=20, decimal_places=2)
    period_total = serializers.DecimalField(max_digits=20, decimal_places=2)

class ProjectStatsSerializer(serializers.Serializer):
    """Serializer para /dashboard/project-stats/"""
    project_id = serializers.IntegerField()
    project_name = serializers.CharField()
    total_income = serializers.FloatField()
    total_refunds = serializers.FloatField()
    total_expenses = serializers.FloatField()
    balance = serializers.FloatField()
    is_profit = serializers.BooleanField()
    days_worked = serializers.IntegerField()
    expense_breakdown = ListLabelValueSerializer(many=True)
    income_breakdown = ListLabelValueSerializer(many=True)