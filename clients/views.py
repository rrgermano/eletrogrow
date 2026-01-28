from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelClient
from .forms import FormClient
from .serializers import ClientSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated



class ListClient(LoginRequiredMixin, ListView):
    model = ModelClient
    template_name = 'clients.html'
    context_object_name = 'clients'
    def get_queryset(self):
        clients = super().get_queryset().order_by('name')
        search = self.request.GET.get('search')
        if search:
            clients = clients.filter(name__icontains=search)
        return clients

class CreateClient(LoginRequiredMixin, CreateView):
    model = ModelClient
    form_class = FormClient
    template_name = 'new_client.html'
    success_url = '/client/'

class UpdateClient(LoginRequiredMixin, UpdateView):
    model = ModelClient
    form_class = FormClient
    template_name = 'update_client.html'
    success_url = '/client/'

class DetailClient(LoginRequiredMixin, DetailView):
    model = ModelClient
    template_name = 'detail_client.html'

class DeleteClient(LoginRequiredMixin, DeleteView):
    model = ModelClient
    template_name = 'delete_client.html'
    success_url = '/client/'

class ListCreateClientApiView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelClient.objects.all()
    serializer_class = ClientSerializer

class RetriveDeleteUpdateClientApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelClient.objects.all()
    serializer_class = ClientSerializer