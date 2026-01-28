from django.urls import path
from .views import ListCreateServicesView, RetriveUpdateDestroyServicesView, ListCreateTasksView, RetrieveUpdateDestroyTasksView

urlpatterns = [
    path('', ListCreateServicesView.as_view(), name='services'),
    path('<int:pk>/', RetriveUpdateDestroyServicesView.as_view(), name='retrive_update_destroy_service'),
    
    path('tasks/', ListCreateTasksView.as_view(), name='tasks-list-create'),
    path('tasks/<int:pk>/', RetrieveUpdateDestroyTasksView.as_view(), name='tasks-detail'),
]