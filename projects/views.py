from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ModelProject
from .forms import FormProject
from .serializers import ProjectSerializer
from .utils import project_name
from clients.models import ModelClient

# Create your views here.
class ListProject(LoginRequiredMixin, ListView):
    model = ModelProject
    template_name = 'project.html'
    context_object_name = 'projects'
    def get_queryset(self):
        projects = super().get_queryset().order_by('-due_date')
        search = self.request.GET.get('search')
        if search:
            projects = projects.filter(name__icontains=search)
        return projects

class CreateProject(LoginRequiredMixin, CreateView):
    model = ModelProject
    form_class = FormProject
    template_name = 'new_project.html'
    success_url = '/project/'

class UpdateProject(LoginRequiredMixin, UpdateView):
    model = ModelProject
    form_class = FormProject
    template_name = 'update_project.html'
    success_url = '/project/'

class DetailProject(LoginRequiredMixin, DetailView):
    model = ModelProject
    template_name = 'detail_project.html'

class DeleteProject(LoginRequiredMixin, DeleteView):
    model = ModelProject
    template_name = 'delete_project.html'
    success_url = '/project/'

class ListCreateProjectApiView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelProject.objects.all()
    serializer_class = ProjectSerializer

class RetrieveUpdateDeleteProjectApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ModelProject.objects.all()
    serializer_class = ProjectSerializer


