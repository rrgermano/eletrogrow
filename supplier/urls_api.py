from django.urls import path
from .views import ListCreateSupplierApiView, RetrieveUpdateDestroySupplierApiView

urlpatterns = [
    path('', ListCreateSupplierApiView.as_view(), name = 'list-create-supplier'),
    path('<int:pk>/', RetrieveUpdateDestroySupplierApiView.as_view(), name = 'retrive-update-destroy-supplier')
]