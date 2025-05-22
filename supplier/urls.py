from django.urls import path
from .views import ListSupplier, CreateSupplier, UpdateSupplier, DetailSupplier, DeleteSupplier

urlpatterns = [
    path('', ListSupplier.as_view(), name='supplier'),
    path('new/', CreateSupplier.as_view(), name='new_supplier'),
    path('update/<int:pk>/', UpdateSupplier.as_view(), name='update_supplier'),
    path('detail/<int:pk>/', DetailSupplier.as_view(), name='detail_supplier'),
    path('delete/<int:pk>/', DeleteSupplier.as_view(), name='delete_supplier'),
]