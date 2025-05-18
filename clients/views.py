from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelClient
from .forms import FormClient



class ListClient(ListView):
    model = ModelClient
    template_name = 'clients.html'
    context_object_name = 'clients'
    def get_queryset(self):
        clients = super().get_queryset().order_by('name')
        search = self.request.GET.get('search')
        if search:
            clients = clients.filter(name__icontains=search)
        return clients

class CreateClient(CreateView):
    model = ModelClient
    form_class = FormClient
    template_name = 'new_client.html'
    success_url = '/client/'

class UpdateClient(UpdateView):
    model = ModelClient
    form_class = FormClient
    template_name = 'update_client.html'
    success_url = '/client/'

class DetailClient(DetailView):
    model = ModelClient
    template_name = 'detail_client.html'

class DeleteClient(DeleteView):
    model = ModelClient
    template_name = 'delete_client.html'
    success_url = '/client/'