from django.db import models
from clients.models import ModelClient

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


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        projects = ModelProject.objects.filter(client=self.client)
        project_serie = int(max([project.name.removeprefix(self.client.project_prefix) for project in projects])) + 1
        self.name = f'{self.client.project_prefix}{project_serie:03}'
        super().save(*args, **kwargs)
