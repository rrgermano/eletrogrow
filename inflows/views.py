from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import ModelInflow
from .forms import FormInflow
from .serializers import InflowSerializer, QuerySetInflowSerializer


class ListInflow(LoginRequiredMixin, ListView):
    model = ModelInflow
    template_name = 'inflow.html'
    context_object_name = 'inflows'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        total = sum(item.value for item in queryset) if queryset else 0
        context['total_value'] = total

        return context

    def get_queryset(self):
        inflows = super().get_queryset()
        search = self.request.GET.get('search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        only_refund = self.request.GET.get('only_refund')
        not_paied = self.request.GET.get('not_paid')
        if start_date:
            inflows = inflows.filter(due_date__gte=start_date)
        if end_date:
            inflows = inflows.filter(due_date__lte=end_date)
        if only_refund:
            inflows = inflows.filter(refund=True)
        if not_paied:
            inflows = inflows.filter(paid=False)
        if search:
            incomes = inflows.filter(income__icontains=search)
            projects = inflows.filter(project__name__icontains=search)
            inflows = incomes.union(projects)
        return inflows.order_by('paid', 'due_date', )
    # def get_queryset(self):
    #     inflows = super().get_queryset().order_by('paid', '-due_date',)
    #     search = self.request.GET.get('search')
    #     if search:
    #         inflows = inflows.filter(income__icontains=search)
    #     return inflows

class CreateInflow(LoginRequiredMixin, CreateView):
    model = ModelInflow
    form_class = FormInflow
    template_name = 'new_inflow.html'
    success_url = '/inflow/'

class UpdateInflow(LoginRequiredMixin, UpdateView):
    model = ModelInflow
    form_class = FormInflow
    template_name = 'update_inflow.html'
    success_url = '/inflow/'

class DetailInflow(LoginRequiredMixin, DetailView):
    model = ModelInflow
    template_name = 'detail_inflow.html'

class DeleteInflow(LoginRequiredMixin, DeleteView):
    model = ModelInflow
    template_name = 'delete_inflow.html'
    success_url = '/inflow/'

class ListCreateInflowApiView(ListCreateAPIView):
    #queryset = ModelInflow.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InflowSerializer

    def get_queryset(self):
        serializer = QuerySetInflowSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refund = data.get('refund', None)
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        paid = data.get('paid', None)
        queryset = ModelInflow.objects.all()
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
        return queryset.order_by('-id', '-due_date')


class RetrieveUpdateDestroyInflowApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelInflow.objects.all().order_by('-id', '-due_date')
    serializer_class = InflowSerializer