from .models import ModelService
from .serializers import ServiceSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

class ListCreateServicesView(ListCreateAPIView):
    queryset = ModelService.objects.all()
    serializer_class = ServiceSerializer


class RetriveUpdateDestroyServicesView(RetrieveUpdateDestroyAPIView):
    queryset = ModelService.objects.all()
    serializer_class = ServiceSerializer
