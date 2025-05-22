from django.urls import path
from .views import ListInflow, CreateInflow,  UpdateInflow, DetailInflow, DeleteInflow

urlpatterns = [
    path('', ListInflow.as_view(), name='inflow'),
    path('new/', CreateInflow.as_view(), name='new_inflow'),
    path('update/<int:pk>/', UpdateInflow.as_view(), name='update_inflow'),
    path('detail/<int:pk>/', DetailInflow.as_view(), name='detail_inflow'),
    path('delete/<int:pk>/', DeleteInflow.as_view(), name='delete_inflow'),
]