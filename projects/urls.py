from django.urls import path
from .views import ListProject, CreateProject,  UpdateProject, DetailProject, DeleteProject

urlpatterns = [
    path('', ListProject.as_view(), name='project'),
    path('new/', CreateProject.as_view(), name='new_project'),
    path('update/<int:pk>/', UpdateProject.as_view(), name='update_project'),
    path('detail/<int:pk>', DetailProject.as_view(), name='detail_project'),
    path('delete/<int:pk>', DeleteProject.as_view(), name='delete_project'),
]