from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelSupplier
from .forms import FormSupplier



class ListSupplier(ListView):
    model = ModelSupplier
    template_name = 'supplier.html'
    context_object_name = 'supplier'
    def get_queryset(self):
        supplier = super().get_queryset().order_by('name')
        search = self.request.GET.get('search')
        if search:
            supplier = supplier.filter(name__icontains=search)
        return supplier

class CreateSupplier(CreateView):
    model = ModelSupplier
    form_class = FormSupplier
    template_name = 'new_supplier.html'
    success_url = '/supplier/'

class UpdateSupplier(UpdateView):
    model = ModelSupplier
    form_class = FormSupplier
    template_name = 'update_supplier.html'
    success_url = '/supplier/'

class DetailSupplier(DetailView):
    model = ModelSupplier
    template_name = 'detail_supplier.html'

class DeleteSupplier(DeleteView):
    model = ModelSupplier
    template_name = 'delete_supplier.html'
    success_url = '/supplier/'