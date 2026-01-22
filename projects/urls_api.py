from django.urls import path
from .views import ListCreateProjectApiView, RetrieveUpdateDeleteProjectApiView, get_project_name

urlpatterns = [
    path('', ListCreateProjectApiView.as_view(), name='list_create_project_api'),
    path('<pk>/', RetrieveUpdateDeleteProjectApiView.as_view(), name='retrieve_update_delete_project_api'),
#    path('project_name/<pk>/', get_project_name, name='get_project_name'),
]