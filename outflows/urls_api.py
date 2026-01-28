from django.urls import path
from .views import ListCreateOutflowApiView, RetrieveUpdateDestroyOutflowApiView, ListCreateCreditOutflowApiView, RetrieveUpdateDestroyCreditOutflowApiView, ListCreateTypeOutflowApiView

urlpatterns = [
    path('', ListCreateOutflowApiView.as_view(), name='list-create-outflow'),
    path('<int:pk>/', RetrieveUpdateDestroyOutflowApiView.as_view(), name='retrieve-update-destroy-outflow'),
    path('credit/', ListCreateCreditOutflowApiView.as_view(), name='list-create-credit-outflow'),
    path('credit/<int:pk>/', RetrieveUpdateDestroyCreditOutflowApiView.as_view(), name='retrieve-update-destroy-credit-outflow'),
    path('types/', ListCreateTypeOutflowApiView.as_view(), name='list-create-type-outflow')
]