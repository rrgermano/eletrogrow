from datetime import datetime
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from django.db.models import Sum
from outflows.models import ModelOutflow, ModelCreditOutflow, ModelProject
from inflows.models import ModelInflow
from .serializers import (
    UpcomingOutflowSerializer,
    UpcomingDataSerializer,
    MonthlySummarySerializer,
    ProjectStatsSerializer,
    EarningsPeriodSerializer
)


class UpcomingOutflowsAPIView(generics.ListAPIView):
    """
    GET /api/dashboard/upcoming-outflows/

    Retorna as 5 despesas NÃO PAGAS que vencem nos próximos 5 dias,
    ordenadas por data de vencimento (mais próxima primeiro).

    Query params opcionais:
        - days: número de dias à frente (padrão: 5)
        - limit: quantidade de resultados (padrão: 5)
        - include_paid: incluir despesas já pagas (padrão: false)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpcomingOutflowSerializer

    def get_queryset(self):
        days = int(self.request.query_params.get('days', 5))
        limit = int(self.request.query_params.get('limit', 5))
        include_paid = self.request.query_params.get('include_paid', 'false').lower() == 'true'

        today = date.today()
        end_date = today + timedelta(days=days)

        queryset = ModelOutflow.objects.filter(
            date__gte=today,
            date__lte=end_date
        )

        if not include_paid:
            queryset = queryset.filter(paid=False)

        queryset = queryset.select_related('favored', 'project').prefetch_related('type')
        queryset = queryset.order_by('date', 'id')[:limit]

        return queryset


# ============================================================================
# NOVA VIEW 1: /dashboard/upcoming/
# ============================================================================

class UpcomingMaturitiesAndTasksAPIView(APIView):
    """
    GET /api/dashboard/upcoming/

    Retorna vencimentos (outflows + inflows) e serviços dos próximos dias.

    Query params:
        - days: número de dias à frente (padrão: 7)
        - limit_maturities: limite de vencimentos (padrão: 10)
        - limit_services: limite de serviços (padrão: 5)

    Response:
    {
        "maturities": [
            {
                "id": 1,
                "description": "Fornecedor Cabos",
                "due_date": "2024-05-20",
                "value": 1500.0,
                "type": "OUTFLOW"
            },
            {
                "id": 2,
                "description": "Entrada Obra Silva",
                "due_date": "2024-05-21",
                "value": 8000.0,
                "type": "INFLOW"
            }
        ],
        "tasks": [
            {
                "id": 101,
                "description": "Instalação Inversor",
                "date": "2024-05-19",
                "project_name": "Solar A"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        days = int(request.query_params.get('days', 7))
        limit_maturities = int(request.query_params.get('limit_maturities', 10))
        limit_services = int(request.query_params.get('limit_services', 5))

        today = date.today()
        end_date = today + timedelta(days=days)

        # Busca outflows não pagos (máximo 5)
        outflows = ModelOutflow.objects.filter(
            date__gte=today,
            date__lte=end_date,
            paid=False
        ).select_related('favored', 'project').order_by('date')[:5].values('id', 'expense', 'date', 'value')

        # Busca inflows não recebidos (máximo 5)
        inflows = ModelInflow.objects.filter(
            due_date__gte=today,
            due_date__lte=end_date,
            # received=False  # Descomente se existir
        ).select_related('project').order_by('due_date')[:5].values('id', 'income', 'due_date', 'value')

        # Monta lista de vencimentos
        maturities = []

        for outflow in outflows:
            maturities.append({
                'id': outflow['id'],
                'description': outflow['expense'],
                'due_date': outflow['date'],
                'value': outflow['value'],
                'type': 'OUTFLOW'
            })

        for inflow in inflows:
            maturities.append({
                'id': inflow['id'],
                'description': inflow['income'],
                'due_date': inflow['due_date'],
                'value': inflow['value'],
                'type': 'INFLOW'
            })

        # Ordena por data (já limitado em 5+5=10 no máximo)
        maturities = sorted(maturities, key=lambda x: x['due_date'])

        # Busca serviços (ModelService) dos próximos dias
        from services.models import ModelService  # Ajuste o import conforme seu app

        services_qs = ModelService.objects.filter(
            date__gte=today,
            date__lte=end_date,
            status__in=['OPEN', 'WIP']  # Apenas abertos e em andamento
        ).select_related('project').order_by('date')[:limit_services]

        tasks = [
            {
                'id': service.id,
                'description': service.description,
                'date': service.date,
                'project_name': service.project.name if service.project else None
            }
            for service in services_qs
        ]

        data = {
            'maturities': maturities,
            'tasks': tasks
        }

        serializer = UpcomingDataSerializer(data)
        return Response(serializer.data)


# ============================================================================
# NOVA VIEW 2: /dashboard/summary/
# ============================================================================

class MonthlySummaryAPIView(APIView):
    """
    GET /api/dashboard/summary/

    Retorna resumo mensal: entradas, saídas, cartão de crédito e projetos aprovados.

    Query params:
        - month: mês no formato YYYY-MM (padrão: mês atual)

    Response:
    {
        "monthly_inflow": 25400.00,
        "monthly_outflow": 12850.50,
        "credit_card_month_total": 4200.00,
        "approved_projects_count": 8
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parâmetro de mês (padrão: mês atual)
        month_param = request.query_params.get('month')

        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                start_date = date(year, month, 1)
            except:
                return Response(
                    {'error': 'Formato de mês inválido. Use YYYY-MM'},
                    status=400
                )
        else:
            today = date.today()
            start_date = date(today.year, today.month, 1)

        # Calcula último dia do mês
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)

        # Total de entradas (inflows) do mês
        monthly_inflow = ModelInflow.objects.filter(
            due_date__gte=start_date,
            due_date__lte=end_date
        ).aggregate(total=Sum('value'))['total'] or 0.0

        # Total de saídas (outflows) do mês
        monthly_outflow = ModelOutflow.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total=Sum('value'))['total'] or 0.0

        # Total do cartão de crédito do mês
        credit_card_month_total = ModelCreditOutflow.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total=Sum('value'))['total'] or 0.0

        # Projetos aprovados (ajuste conforme seu critério de "aprovado")
        # Exemplo: projetos que têm inflows (entradas)
        approved_projects_count = ModelProject.objects.filter(
            inflows__isnull=False  # ← Corrigido: 'inflows' (plural)
        ).distinct().count()

        data = {
            'monthly_inflow': float(f"{monthly_inflow:.2f}"),
            'monthly_outflow': float(f"{monthly_outflow:.2f}"),
            'credit_card_month_total': float(f"{credit_card_month_total:.2f}"),
            'approved_projects_count': approved_projects_count
        }

        serializer = MonthlySummarySerializer(data)
        return Response(serializer.data)


# ============================================================================
# NOVA VIEW 3: /dashboard/project-stats/
# ============================================================================

class ProjectStatsAPIView(APIView):
    """
    GET /api/dashboard/project-stats/?project_id=123

    Retorna estatísticas detalhadas de um projeto específico.

    Query params:
        - project_id: ID do projeto (obrigatório)

    Response:
    {
        "project_id": 123,
        "project_name": "Residencial Solar ABC",
        "total_income": 50000.00,
        "total_expenses": 32000.00,
        "balance": 18000.00,
        "is_profit": true,
        "days_worked": 14,
        "expense_breakdown": [
            {"label": "Materiais", "value": 20000.0, "color": "#ef4444"},
            {"label": "Logística", "value": 5000.0, "color": "#f59e0b"}
        ],
        "income_breakdown": [
            {"label": "Reembolso", "value": 25000.0},
            {"label": "Projeto", "value": 25000.0}
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {'error': 'project_id é obrigatório'},
                status=400
            )

        try:
            project = ModelProject.objects.get(id=project_id)
        except ModelProject.DoesNotExist:
            return Response(
                {'error': 'Projeto não encontrado'},
                status=404
            )

        # ====================================================================
        # TOTAL DE ENTRADAS - Exclui reembolsos (não são receita real)
        # ====================================================================
        total_income = ModelInflow.objects.filter(
            project=project,
        #    refund=False  # ← Apenas entradas reais (não reembolsos)
        ).aggregate(total=Sum('value'))['total'] or 0.0

        # Total de reembolsos (separado, para referência)
        total_refunds = ModelInflow.objects.filter(
            project=project,
            refund=True
        ).aggregate(total=Sum('value'))['total'] or 0.0

        # ====================================================================
        # TOTAL DE DESPESAS - TODOS Outflows + CreditOutflows
        # ====================================================================
        total_outflows = ModelOutflow.objects.filter(
            project=project
        ).aggregate(total=Sum('value'))['total'] or 0.0

        total_credit = ModelCreditOutflow.objects.filter(
            project=project
        ).aggregate(total=Sum('value'))['total'] or 0.0

        # Total gasto = TODOS outflows + TODOS credits (valor absoluto dos gastos)
        total_spent = total_outflows + total_credit

        # Para o cálculo do balance:
        # Balance = (Entradas do projeto + Reembolsos recebidos) - Gastos totais
        balance = total_income - total_spent
        is_profit = balance > 0

        # ====================================================================
        # DIAS TRABALHADOS - Baseado em quantidade de serviços executados
        # ====================================================================
        from services.models import ModelService  # Ajuste o import conforme seu app

        # Conta serviços concluídos ou em andamento (não cancelados/abertos)
        days_worked = ModelService.objects.filter(
            project=project,
            status__in=['CLOSED', 'APROV', 'WIP']  # Apenas serviços executados
        ).count()

        # Alternativa: Se quiser contar apenas os fechados/aprovados:
        # days_worked = ModelService.objects.filter(
        #     project=project,
        #     status__in=['CLOSED', 'APROV']
        # ).count()

        # ====================================================================
        # BREAKDOWN DE DESPESAS - 1 TIPO POR DESPESA (SEM DUPLICAÇÃO)
        # Prioridade: Material > Alimentação > Transporte > Ferramenta > Outros
        # ====================================================================

        # Define ordem de prioridade dos tipos
        TYPE_PRIORITY = {
            'Material': 1,
            'Materiais': 1,
            'Alimentação': 2,
            'Alimentacao': 2,
            'Transporte': 3,
            'Logística': 3,
            'Logistica': 3,
            'Ferramenta': 4,
            'Ferramentas': 4,
        }

        # Busca despesas com seus tipos (Outflow + CreditOutflow)
        from django.db.models import Prefetch

        # Outflows do projeto
        outflows_with_types = ModelOutflow.objects.filter(
            project=project
        ).prefetch_related('type')

        # Credit outflows do projeto
        credit_with_types = ModelCreditOutflow.objects.filter(
            project=project
        ).prefetch_related('type')

        # Dicionário para acumular valores por tipo
        expense_by_type = {}

        def get_best_type(types_list):
            """
            Retorna o tipo mais prioritário da lista.
            Ignora "Reembolso" e escolhe baseado na ordem de prioridade.
            """
            # Remove reembolso da lista
            valid_types = [t for t in types_list if t.name != 'Reembolso']

            if not valid_types:
                return None

            # Se só tem 1 tipo, usa ele
            if len(valid_types) == 1:
                return valid_types[0].name

            # Se tem múltiplos, escolhe o mais prioritário
            best_type = None
            best_priority = 999

            for t in valid_types:
                priority = TYPE_PRIORITY.get(t.name, 99)  # Outros = 99
                if priority < best_priority:
                    best_priority = priority
                    best_type = t.name

            return best_type if best_type else valid_types[0].name

        # Processa outflows (1 tipo por despesa)
        for outflow in outflows_with_types:
            types_list = list(outflow.type.all())
            best_type = get_best_type(types_list)

            if best_type:  # Se não for só "Reembolso"
                if best_type not in expense_by_type:
                    expense_by_type[best_type] = 0.0
                expense_by_type[best_type] += outflow.value

        # Processa credit outflows (1 tipo por despesa)
        for credit in credit_with_types:
            types_list = list(credit.type.all())
            best_type = get_best_type(types_list)

            if best_type:  # Se não for só "Reembolso"
                if best_type not in expense_by_type:
                    expense_by_type[best_type] = 0.0
                expense_by_type[best_type] += credit.value

        # Monta breakdown ordenado por valor (maior primeiro)
        expense_breakdown = [
            {
                'label': type_name,
                'value': float(f"{value:.2f}")
            }
            for type_name, value in sorted(
                expense_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]

        # ====================================================================
        # BREAKDOWN DE ENTRADAS - SEPARADO POR TIPO (Reembolso, Projeto, etc)
        # ====================================================================

        # Busca inflows agrupados por tipo
        # Assumindo que você tem lógica para diferenciar tipos de inflow
        # Opção 1: Se ModelInflow tem campo 'refund' (boolean)
        income_reembolso = ModelInflow.objects.filter(
            project=project,
            refund=True
        ).aggregate(total=Sum('value'))['total'] or 0.0

        income_projeto = ModelInflow.objects.filter(
            project=project,
            refund=False
        ).aggregate(total=Sum('value'))['total'] or 0.0

        income_breakdown = []

        if income_reembolso > 0:
            income_breakdown.append({
                'label': 'Reembolso',
                'value': float(f"{income_reembolso:.2f}")
            })

        if income_projeto > 0:
            income_breakdown.append({
                'label': 'Projeto',
                'value': float(f"{income_projeto:.2f}")
            })

        # Opção 2: Se você quer agrupar por descrição (income field)
        # Descomente isso e comente o código acima se preferir
        """
        income_by_desc = ModelInflow.objects.filter(
            project=project
        ).values('income').annotate(
            total=Sum('value')
        ).order_by('-total')

        income_breakdown = [
            {
                'label': item['income'],
                'value': round(item['total'], 2)
            }
            for item in income_by_desc
        ]
        """

        data = {
            'project_id': project.id,
            'project_name': project.name,  # Ajuste conforme campo do seu model
            'total_income': float(f"{total_income:.2f}"),
            'total_refunds': float(f"{total_refunds:.2f}"),
            'total_expenses': float(f"{total_spent:.2f}"),
            'balance': float(f"{balance:.2f}"),
            'is_profit': is_profit,
            'days_worked': days_worked,
            'expense_breakdown': expense_breakdown,
            'income_breakdown': income_breakdown
        }

        serializer = ProjectStatsSerializer(data)
        #print(serializer.data)
        return Response(serializer.data)


# ============================================================================
# NOVA VIEW 4: /dashboard/charts/earnings-period/
# ============================================================================

class EarningsPeriodChartAPIView(APIView):
    """
    Retorna ganhos líquidos (inflows - outflows) por período,
    incluindo IDs por ponto do gráfico.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # ======================================================
        # PARAMETROS DE DATA
        # ======================================================
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            today = date.today()
            start_date = date(today.year, today.month, 1)

            if today.month == 12:
                end_date = date(today.year, 12, 31)
            else:
                end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                    status=400
                )

            if start_date > end_date:
                return Response(
                    {'error': 'start_date não pode ser maior que end_date'},
                    status=400
                )

        # ======================================================
        # AGRUPAMENTO
        # ======================================================
        group_by = request.query_params.get('group_by', 'day')
        if group_by not in ['day', 'month']:
            return Response(
                {'error': 'group_by deve ser "day" ou "month"'},
                status=400
            )

        def get_period(dt):
            if group_by == 'day':
                return dt.strftime('%Y-%m-%d')
            return dt.strftime('%Y-%m-01')

        # ======================================================
        # BUSCA BASE
        # ======================================================
        base_inflows = ModelInflow.objects.filter(
            paid_date__gte=start_date,
            paid_date__lte=end_date,
            paid_date__isnull=False
        ).order_by('value')

        base_outflows = ModelOutflow.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('value')

        # ======================================================
        # CONSOLIDA DADOS
        # ======================================================
        earnings_dict = {}

        # Inflows
        for inflow in base_inflows:
            period = get_period(inflow.paid_date)

            if period not in earnings_dict:
                earnings_dict[period] = {
                    'value': 0.0,
                    'inflows_ids': [],
                    'outflows_ids': []
                }

            earnings_dict[period]['value'] += float(inflow.value)
            earnings_dict[period]['inflows_ids'].append(inflow.id)

        # Outflows
        for outflow in base_outflows:
            period = get_period(outflow.date)

            if period not in earnings_dict:
                earnings_dict[period] = {
                    'value': 0.0,
                    'inflows_ids': [],
                    'outflows_ids': []
                }

            earnings_dict[period]['value'] -= float(outflow.value)
            earnings_dict[period]['outflows_ids'].append(outflow.id)

        # ======================================================
        # FORMATA RESPOSTA
        # ======================================================
        result = []

        for period_str in sorted(earnings_dict.keys()):
            data = earnings_dict[period_str]
            period = datetime.strptime(period_str, '%Y-%m-%d').date()

            label = (
                period.strftime('%d/%m')
                if group_by == 'day'
                else period.strftime('%m/%Y')
            )

            result.append({
                'label': label,
                'value': round(data['value'], 2),
                'inflows_ids': data['inflows_ids'],
                'outflows_ids': data['outflows_ids'],
            })

        # ======================================================
        # TOTAIS
        # ======================================================
        values = [item['value'] for item in result]
        period_total = round(sum(values), 2)
        period_average = round(period_total / len(values), 2) if values else 0

        payload = {
            'earnings': result,
            'period_total': period_total,
            'period_average': period_average,
        }

        serializer = EarningsPeriodSerializer(payload)
        return Response(serializer.data)

