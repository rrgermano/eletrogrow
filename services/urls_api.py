from django.urls import path
from .views import ListCreateServicesView, RetriveUpdateDestroyServicesView

urlpatterns = [
    path('', ListCreateServicesView.as_view(), name='services'),
    path('<pk>/', RetriveUpdateDestroyServicesView.as_view(), name='retrive_update_destroy_service')
]