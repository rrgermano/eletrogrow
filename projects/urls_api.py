from django.urls import path
from .views import ListCreateProjectApiView, RetrieveUpdateDeleteProjectApiView

urlpatterns = [
    path('', ListCreateProjectApiView.as_view(), name='list_create_project_api'),
    path('<pk>/', RetrieveUpdateDeleteProjectApiView.as_view(), name='retrieve_update_delete_project_api'),

]