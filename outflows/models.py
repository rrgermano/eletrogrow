from django.db import models
from django.utils.timezone import now
from projects.models import ModelProject
from supplier.models import ModelSupplier

METHOD_CHOICES = [
    ('PIX', 'PIX'),
    ('DEB', 'Cartão de débito'),
    ('REF', 'Reembolso'),
    ('AUT', 'Débito Automático'),
    ('BOL', 'Boleto'),
]
class OutflowTypeChoice(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @property
    def model_name(self):
        return self._meta.model_name

class ModelOutflow(models.Model):
    expense = models.CharField(max_length=50, verbose_name='Despesa')
    favored = models.ForeignKey(ModelSupplier, on_delete=models.PROTECT, blank=True, null=True, related_name='outflow', verbose_name='Favorecido')
    paid = models.BooleanField(default=False, verbose_name='Pago')
    type = models.ManyToManyField(OutflowTypeChoice, related_name='outflows', blank=True, verbose_name='Tipo')
    date = models.DateField(verbose_name='Data', default=now)
    payment_method = models.CharField(choices=METHOD_CHOICES, default='PIX', verbose_name='Método de pagamento')
    project = models.ForeignKey(ModelProject, blank=True, null=True, on_delete=models.PROTECT, related_name='outflow', verbose_name='Projeto')
    value = models.FloatField(verbose_name='Valor')
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.expense
    
    @property
    def model_name(self):
        return self._meta.model_name

class ModelCreditOutflow(models.Model):
    expense = models.CharField(max_length=50, verbose_name='Despesa')
    favored = models.ForeignKey(ModelSupplier, on_delete=models.PROTECT, blank=True, null=True, related_name='credit', verbose_name='Favorecido')
    type = models.ManyToManyField(OutflowTypeChoice, related_name='credit', blank=True, verbose_name='Tipo')
    date = models.DateField(verbose_name='Data', default=now)
    project = models.ForeignKey(ModelProject, blank=True, null=True, on_delete=models.PROTECT, related_name='credit', verbose_name='Projeto')
    value = models.FloatField(verbose_name='Valor')
    closing = models.BooleanField(default=False, verbose_name='Fechamento')
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.expense
    @property
    def model_name(self):
        return self._meta.model_name