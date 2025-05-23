from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelInflow
from .forms import FormInflow


class ListInflow(LoginRequiredMixin, ListView):
    model = ModelInflow
    template_name = 'inflow.html'
    context_object_name = 'inflows'
    def get_queryset(self):
        inflows = super().get_queryset().order_by('paid', 'due_date',)
        search = self.request.GET.get('search')
        if search:
            inflows = inflows.filter(income__icontains=search)
        return inflows

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
