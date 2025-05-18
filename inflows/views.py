from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelInflow
from .forms import FormInflow

# Create your views here.
class ListInflow(ListView):
    model = ModelInflow
    template_name = 'inflow.html'
    context_object_name = 'inflows'
    def get_queryset(self):
        inflows = super().get_queryset().order_by('paid', 'due_date',)
        search = self.request.GET.get('search')
        if search:
            inflows = inflows.filter(income__icontains=search)
        return inflows

class CreateInflow(CreateView):
    model = ModelInflow
    form_class = FormInflow
    template_name = 'new_inflow.html'
    success_url = '/inflow/'

class UpdateInflow(UpdateView):
    model = ModelInflow
    form_class = FormInflow
    template_name = 'update_inflow.html'
    success_url = '/inflow/'

class DetailInflow(DetailView):
    model = ModelInflow
    template_name = 'detail_inflow.html'

class DeleteInflow(DeleteView):
    model = ModelInflow
    template_name = 'delete_inflow.html'
    success_url = '/inflow/'