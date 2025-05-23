from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelSupplier
from .forms import FormSupplier



class ListSupplier(LoginRequiredMixin, ListView):
    model = ModelSupplier
    template_name = 'supplier.html'
    context_object_name = 'supplier'
    def get_queryset(self):
        supplier = super().get_queryset().order_by('name')
        search = self.request.GET.get('search')
        if search:
            supplier = supplier.filter(name__icontains=search)
        return supplier

class CreateSupplier(LoginRequiredMixin, CreateView):
    model = ModelSupplier
    form_class = FormSupplier
    template_name = 'new_supplier.html'
    success_url = '/supplier/'

class UpdateSupplier(LoginRequiredMixin, UpdateView):
    model = ModelSupplier
    form_class = FormSupplier
    template_name = 'update_supplier.html'
    success_url = '/supplier/'

class DetailSupplier(LoginRequiredMixin, DetailView):
    model = ModelSupplier
    template_name = 'detail_supplier.html'

class DeleteSupplier(LoginRequiredMixin, DeleteView):
    model = ModelSupplier
    template_name = 'delete_supplier.html'
    success_url = '/supplier/'