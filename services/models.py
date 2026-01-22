from django.db import models
from clients.models import ModelClient
from projects.models import ModelProject

OS_TYPE_CHOICES = [
    ('COR', 'Corrido'),
    ('CONT', 'Contratado'),
]

OS_STATUS_CHOICES = [
    ('OPEN', 'Aberto'),
    ('CLOSED', 'Fechado'),
    ('APROV', 'Aprovado'),
    ('WIP', 'Em Andamento'),
    ('CANC', 'Cancelado'),
    ('WAR', 'Garantia')
]
# Create your models here.
class ModelService(models.Model):
    project = models.ForeignKey(ModelProject, on_delete=models.CASCADE, related_name='services_projects', verbose_name='Projeto')
    service_type = models.CharField(choices=OS_TYPE_CHOICES, default='COR', verbose_name='Tipo de Serviço')
    description = models.TextField(verbose_name='Descriçao do serviço')
    closing = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    last_changes = models.DateField(auto_now=True)
    status = models.CharField(choices=OS_STATUS_CHOICES, default='OPEN', verbose_name='Status')
    # hora_de_partida
    # hora_de_chegada
    # hora_de_saida
    # hora_de_chegada
    # pendencias
    # hora_saida_almoco
    # hora_chegada_almoco
