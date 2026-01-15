from django.db import models
from clients.models import ModelClient
from projects.models import ModelProject

OS_CHOICES = [
    ('COR', 'Corrido'),
    ('CONT', 'Contratado'),
]
# Create your models here.
class ModelService(models.Model):
    project = models.ForeignKey(ModelProject, on_delete=models.CASCADE, related_name='services-projects', verbose_name='Projeto')
    service_type = models.CharField(choices=OS_CHOICES, default='COR', verbose_name='Tipo de Serviço')
    description = models.TextField(verbose_name='Descriçao do serviço')
    closing = None