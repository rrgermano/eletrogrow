from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelInflow
from .forms import FormInflow


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
        if start_date:
            inflows = inflows.filter(due_date__gte=start_date)
        if end_date:
            inflows = inflows.filter(due_date__lte=end_date)
        if only_refund:
            inflows = inflows.filter(refund=True)
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
