from django.urls import path
from .views import ListCreateClientApiView, RetriveDeleteUpdateClientApiView

urlpatterns = [
    path('', ListCreateClientApiView.as_view(), name='list_create_client_api'),
    path('<pk>/', RetriveDeleteUpdateClientApiView.as_view(), name='retrieve_delete_update_cliente_api'),
]