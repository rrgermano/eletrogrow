from django.urls import path
from .views import ListCreateInflowApiView, RetrieveUpdateDestroyInflowApiView

urlpatterns = [
    path('', ListCreateInflowApiView.as_view(), name='list-create-inflow'),
    path('<int:pk>/', RetrieveUpdateDestroyInflowApiView.as_view(), name='retrieve-update-destroy-inflow'),
]