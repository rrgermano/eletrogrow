from django.db import models
from projects.models import ModelProject
from django.utils.timezone import now

METHOD_CHOICES = [
    ('PIX', 'PIX'),
    ('CRED', 'Cartão de crédito'),
    ('DEB', 'Cartão de débito'),
    ('BOL', 'Boleto'),
]

class ModelInflow(models.Model):
    income = models.CharField(max_length=15, unique=True, verbose_name='Receita')
    paid = models.BooleanField(default=False, verbose_name='Pago')
    project = models.ForeignKey(ModelProject, on_delete=models.CASCADE, related_name='inflows', verbose_name='Projeto', blank=True, null=True)
    due_date = models.DateField(verbose_name='Data', default=now)
    payment_method = models.CharField(choices=METHOD_CHOICES, default='PIX', verbose_name='Método de pagamento')
    value = models.FloatField(verbose_name='Valor')

    def __str__(self):
        return self.income
