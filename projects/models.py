from django.db import models
from clients.models import ModelClient
from .utils import project_name

# Create your models here.
class ModelProject(models.Model):
    name = models.CharField(max_length=6, unique=True, verbose_name='Nome')
    client = models.ForeignKey(ModelClient, on_delete=models.CASCADE, related_name='projects', verbose_name='Cliente')
    start_project = models.DateField(blank=True, null=True, verbose_name='Início do projeto')
    start_work = models.DateField(blank=True, null=True, verbose_name='Início da obra')
    end_project = models.DateField(blank=True, null=True, verbose_name='Fim de projeto/obra')
    parcel = models.PositiveIntegerField(default=1, verbose_name='Parcelas')
    value = models.FloatField(blank=True, null=True, verbose_name='Valor')
    due_date = models.DateField(blank=True, null=True, verbose_name='Data de vencimento')
    description = models.TextField(verbose_name='Descrição')
    #tasks = models.JSONField(verbose_name='Tarefas')


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = project_name(self.client, ModelProject)
        super().save(*args, **kwargs)
