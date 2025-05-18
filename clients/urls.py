from django.urls import path
from .views import ListClient, CreateClient, UpdateClient, DetailClient, DeleteClient

urlpatterns = [
    path('', ListClient.as_view(), name='client'),
    path('new/', CreateClient.as_view(), name='new_client'),
    path('update/<int:pk>/', UpdateClient.as_view(), name='update_client'),
    path('detail/<int:pk>', DetailClient.as_view(), name='detail_client'),
    path('delete/<int:pk>', DeleteClient.as_view(), name='delete_client'),
]