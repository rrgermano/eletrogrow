from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .forms import FormOutflow, FormUpdateOutflow, FormOutflowTypeChoice
from .models import ModelOutflow, ModelCreditOutflow, OutflowTypeChoice
from .serializers import OutflowCreditSerializer, OutflowSerializer, OutflowTypeSerializer, QuerySetOutflowSerializer
from supplier.models import ModelSupplier
from projects.models import ModelProject
from dateutil.relativedelta import relativedelta
import threading
from time import sleep
from django.http import JsonResponse


class ListOutflow(LoginRequiredMixin, ListView):
    model = ModelOutflow
    template_name = 'outflow.html'
    context_object_name = 'outflows'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        total = sum(item.value for item in queryset) if queryset else 0
        context['total_value'] = total

        return context
    def get_queryset(self):
        outflows = super().get_queryset()
        search = self.request.GET.get('search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            outflows = outflows.filter(date__gte=start_date)
        if end_date:
            outflows = outflows.filter(date__lte=end_date)
        if search:
            expenses = outflows.filter(expense__icontains=search)
            projects = outflows.filter(project__name__icontains=search)
            outflows = expenses.union(projects)

        return outflows.order_by('paid', 'date', )

class CreateOutflow(LoginRequiredMixin, View):

    def get(self, request):
        form = FormOutflow()
        return render(request, 'new_outflow.html', {'form': form})

    def post(self, request):
        form_posted = FormOutflow(request.POST)
        print(form_posted)
        if form_posted.is_valid():
            cleaned_data = form_posted.cleaned_data
            if cleaned_data['payment_method'] == 'CRED':
                threading.Thread(
                    target=self.__credit_parcel_creation,
                    args=(cleaned_data.copy(),)
                ).start()
                return redirect('outflow_credit')
                
            else:
                outflow = ModelOutflow(
                    expense=cleaned_data['expense'],
                    favored=cleaned_data['favored'],
                    paid=cleaned_data['paid'],
                    date=cleaned_data['date'].strftime('%Y-%m-%d'),
                    payment_method=cleaned_data['payment_method'],
                    project=cleaned_data['project'],
                    value=cleaned_data['value'],
                )
                outflow.save()
                outflow.type.set(cleaned_data['type'])
                return redirect('outflow')
        return render(request, 'new_outflow.html', {'form': form_posted})
    def __credit_parcel_creation(self, form):
        parcel_value = form['value']/form['parcel']
        sleep(2)
        for parcel in range(form['parcel']):
            date = form['date']
            date = (date + relativedelta(months=parcel)).strftime('%Y-%m-%d')
            outflow = ModelCreditOutflow(
                expense=f"{form['expense']} - {parcel+1}/{form['parcel']}" if form['parcel']>1 else form['expense'],
                favored=form['favored'],
                date=date,
                project=form['project'],
                value=round(parcel_value, 2)
            )
            outflow.save()
            outflow.type.set(form['type'])

class DetailOutflow(LoginRequiredMixin, DetailView):
    model = ModelOutflow
    template_name = "detail_outflow.html"

class DeleteOutflow(LoginRequiredMixin, DeleteView):
    model = ModelOutflow
    template_name = 'delete_outflow.html'
    success_url = '/outflow/'

class UpdateOutflow(LoginRequiredMixin, UpdateView):
    model = ModelOutflow
    form_class = FormUpdateOutflow
    template_name = 'update_outflow.html'
    success_url = '/outflow/'

    def get_form_class(self):
        # Criar uma classe temporária que herda do seu Form
        original_form = super().get_form_class()
        
        class TempModelForm(original_form):
            def save(self, commit=True):
                # Pegar o objeto da view
                obj = self.instance if hasattr(self, 'instance') else None
                if obj:
                    for field_name in self.cleaned_data:
                        if hasattr(obj, field_name) and field_name != 'type':
                            setattr(obj, field_name, self.cleaned_data[field_name])
                        elif hasattr(obj, field_name) and field_name == 'type':
                            getattr(obj, field_name).set(self.cleaned_data[field_name])
                    if commit:
                        obj.save()
                    return obj
                return None
        
        return TempModelForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Passa o objeto para o form
        return kwargs

class ListCreditOutflow(LoginRequiredMixin, ListView):
    model = ModelCreditOutflow
    template_name = 'outflow.html'
    context_object_name = 'outflows'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Usando annotate para calcular a soma manualmente
        total = sum(item.value for item in queryset) if queryset else 0
        context['total_value'] = total

        return context
    def get_queryset(self):
        outflows = super().get_queryset()
        search = self.request.GET.get('search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if search:
            expenses = outflows.filter(expense__icontains=search)
            projects = outflows.filter(project__name__icontains=search)
            outflows = expenses.union(projects)
        if start_date:
            outflows = outflows.filter(date__gte=start_date)
        if end_date:
            outflows = outflows.filter(date__lte=end_date)
        return outflows.order_by('date', )

class DetailCreditOutflow(LoginRequiredMixin, DetailView):
    model = ModelCreditOutflow
    template_name = "detail_outflow.html"

class DeleteCreditOutflow(LoginRequiredMixin, DeleteView):
    model = ModelCreditOutflow
    template_name = 'delete_outflow.html'
    success_url = '/outflow/credit/'

class UpdateCreditOutflow(LoginRequiredMixin, UpdateView):
    model = ModelCreditOutflow
    form_class = FormUpdateOutflow
    template_name = 'update_outflow.html'
    success_url = '/outflow/credit/'

    def get_form_class(self):
        # Criar uma classe temporária que herda do seu Form
        original_form = super().get_form_class()
        
        class TempModelForm(original_form):
            def save(self, commit=True):
                # Pegar o objeto da view
                obj = self.instance if hasattr(self, 'instance') else None
                if obj:
                    for field_name in self.cleaned_data:
                        if hasattr(obj, field_name) and field_name != 'type':
                            setattr(obj, field_name, self.cleaned_data[field_name])
                        elif hasattr(obj, field_name) and field_name == 'type':
                            getattr(obj, field_name).set(self.cleaned_data[field_name])
                    if commit:
                        obj.save()
                    return obj
                return None
        
        return TempModelForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Passa o objeto para o form
        return kwargs

class CreateOutflowTypeChoice(LoginRequiredMixin, CreateView):
    model = OutflowTypeChoice
    form_class = FormOutflowTypeChoice
    template_name = 'new_outflow.html'
    success_url = '/outflow/new/'

class UpdateOutflowTypeChoice(LoginRequiredMixin, UpdateView):
    model = OutflowTypeChoice
    form_class = FormOutflowTypeChoice
    template_name = 'update_outflow.html'
    success_url = '/outflow/new/'

class DeleteOutflowTypeChoice(LoginRequiredMixin, DeleteView):
    model = OutflowTypeChoice
    template_name = 'delete_outflow.html'
    success_url = '/outflow/new/'

def favored_autocomplete(request):
    if request.user.is_authenticated:
        query = request.GET.get('q', '')

        suppliers = ModelSupplier.objects.filter(name__icontains=query).order_by('name')[:20]
        results = [{"id": supplier.id, "text": supplier.name} for supplier in suppliers]
    else:
        results = {}
    return JsonResponse({"results": results})

def project_autocomplete(request):
    if request.user.is_authenticated:
        query = request.GET.get('q', '')

        projects = ModelProject.objects.filter(name__icontains=query).order_by('name')[:20]
        results = [{"id": project.id, "text": project.name} for project in projects]
    else:
        results = {}
    return JsonResponse({"results": results})

class ListCreateOutflowApiView(ListCreateAPIView):
    #queryset = ModelOutflow.objects.all().order_by('-date')
    permission_classes = [IsAuthenticated]
    serializer_class = OutflowSerializer

    def get_queryset(self):
        serializer = QuerySetOutflowSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refund = data.get('refund', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        paid = data.get('paid', None)
        queryset = ModelOutflow.objects.all()
        match refund:
            case 'refund':
                queryset = queryset.filter(refund=True)
            case 'not_refund':
                queryset = queryset.exclude(refund=True)
        match paid:
            case 'paid':
                queryset = queryset.filter(paid=True)
            case 'not_paid':
                queryset = queryset.filter(paid=False)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

class RetrieveUpdateDestroyOutflowApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelOutflow.objects.all()
    serializer_class = OutflowSerializer
class ListCreateCreditOutflowApiView(ListCreateAPIView):
    """
    GET  /api/credit-outflows/     → Lista todas as despesas de crédito
    POST /api/credit-outflows/     → Cria nova despesa (com parcelamento opcional)

    Exemplo POST:
    {
        "expense": "Notebook Dell",
        "favored": 1,
        "value": 3600.00,
        "installments": 12,
        "type": [1, 2],
        "date": "2026-01-26",
        "project": 3
    }
    """
    #queryset = ModelCreditOutflow.objects.all().order_by('-date')
    permission_classes = [IsAuthenticated]
    serializer_class = OutflowCreditSerializer

    def get_queryset(self):
        serializer = QuerySetOutflowSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refund = data.get('refund', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        paid = data.get('paid', None)
        queryset = ModelOutflow.objects.all()
        match refund:
            case 'refund':
                queryset = queryset.filter(refund=True)
            case 'not_refund':
                queryset = queryset.exclude(refund=True)
        match paid:
            case 'paid':
                queryset = queryset.filter(paid=True)
            case 'not_paid':
                queryset = queryset.filter(paid=False)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset
    def create(self, request, *args, **kwargs):
        """Override para retornar mensagem customizada"""
        #print(f'create credit {request.data}')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        num_installments = request.data.get('installments', 1)
        instance = serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(
            {
                'message': f'Despesa criada com sucesso! {num_installments} parcela(s) gerada(s).',
                'installments_count': num_installments,
                'first_installment': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class RetrieveUpdateDestroyCreditOutflowApiView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/credit-outflows/{id}/   → Detalhes de uma despesa
    PUT    /api/credit-outflows/{id}/   → Atualiza despesa completa
    PATCH  /api/credit-outflows/{id}/   → Atualiza parcialmente
    DELETE /api/credit-outflows/{id}/   → Deleta despesa

    ATUALIZAÇÃO INTELIGENTE:
    - Se a despesa for parcelada (ex: "Compra (2/12)"), atualiza TODAS as parcelas
    - Respeita parcelas com closing=True (não modifica se já fechadas)
    - Atualiza datas a partir da data informada (primeira parcela = data informada, demais = dia 27)
    """
    #queryset = ModelCreditOutflow.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OutflowCreditSerializer

    def get_queryset(self):
        serializer = QuerySetOutflowSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refund = data.get('refund', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        paid = data.get('paid', None)
        queryset = ModelCreditOutflow.objects.all()
        match refund:
            case 'refund':
                queryset = queryset.filter(refund=True)
            case 'not_refund':
                queryset = queryset.exclude(refund=True)
        match paid:
            case 'paid':
                queryset = queryset.filter(paid=True)
            case 'not_paid':
                queryset = queryset.filter(paid=False)
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__lte=end_date)
        return queryset
    def _find_all_installments(self, instance):
        """
        Encontra todas as parcelas relacionadas baseado no padrão do expense.

        Returns:
            tuple: (expense_base, current_installment, total_installments, all_installments_queryset)
                   ou (None, None, None, None) se não for parcelado
        """
        expense = instance.expense

        # Verifica se é parcelado: "Descrição (X/Y)"
        if '(' not in expense or '/' not in expense:
            return None, None, None, None

        try:
            # Extrai "Descrição" e "X/Y"
            expense_base = expense[:expense.rfind('(')].strip()
            parcel_info = expense[expense.rfind('(') + 1:expense.rfind(')')]
            current, total = map(int, parcel_info.split('/'))

            # Busca todas as parcelas com o mesmo padrão
            all_installments = ModelCreditOutflow.objects.filter(
                expense__startswith=expense_base
            ).filter(
                expense__contains=f'/{total})'
            ).order_by('date')

            return expense_base, current, total, all_installments

        except (ValueError, IndexError):
            return None, None, None, None

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Atualização inteligente de parcelas"""
        #print(f'update credit {request.data}')
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Verifica se é parcelado
        expense_base, current, total, all_installments = self._find_all_installments(instance)

        # Se não for parcelado, atualização normal
        if not expense_base:
            return super().update(request, *args, **kwargs)

        # Verifica se alguma parcela já foi fechada
        closed_installments = all_installments.filter(closing=True).order_by('date')

        if closed_installments.exists():
            first_closed = closed_installments.first()
            first_closed_expense = first_closed.expense

            try:
                closed_number = int(
                    first_closed_expense[first_closed_expense.rfind('(') + 1:first_closed_expense.rfind('/')].strip()
                )

                return Response(
                    {
                        'error': f'Não é possível atualizar. A parcela {closed_number}/{total} já está com closing=True.',
                        'closed_installment_id': first_closed.id,
                        'closed_installment_date': first_closed.date
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            except:
                return Response(
                    {
                        'error': 'Não é possível atualizar. Há parcelas com closing=True.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Pega dados para atualização
        update_data = request.data.copy()
        new_date = update_data.get('date', instance.date)
        new_value_total = update_data.get('value')
        new_expense = update_data.get('expense', expense_base)
        new_types = update_data.get('type')

        # Se informou valor, divide pelas parcelas
        if new_value_total:
            parcel_value = round(float(new_value_total) / total, 2)
        else:
            # Mantém o valor atual da parcela
            parcel_value = instance.value

        # Atualiza todas as parcelas
        updated_count = 0

        for i, installment in enumerate(all_installments, start=1):
            # Calcula nova data
            if i == 1:
                installment_date = new_date
            else:
                installment_date = new_date + relativedelta(months=i - 1)
                installment_date = installment_date.replace(day=27)

            # Atualiza campos
            installment.expense = f"{new_expense} ({i}/{total})"
            installment.date = installment_date
            installment.value = parcel_value

            # Atualiza outros campos se fornecidos
            if 'favored' in update_data:
                installment.favored_id = update_data['favored']
            if 'project' in update_data:
                installment.project_id = update_data['project']
            if 'closing' in update_data:
                installment.closing = update_data['closing']

            installment.save()

            # Atualiza tipos se fornecidos
            if new_types is not None:
                installment.type.set(new_types)

            updated_count += 1

        # Retorna a primeira parcela atualizada
        first_installment = all_installments.first()
        serializer = self.get_serializer(first_installment)

        return Response(
            {
                'message': f'{updated_count} parcelas atualizadas com sucesso.',
                'total_installments': total,
                'first_installment': serializer.data
            },
            status=status.HTTP_200_OK
        )

class ListCreateTypeOutflowApiView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = OutflowTypeChoice.objects.all()
    serializer_class = OutflowTypeSerializer

