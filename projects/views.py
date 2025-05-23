from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import ModelProject
from .forms import FormProject

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