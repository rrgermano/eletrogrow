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
    income = models.CharField(max_length=15, verbose_name='Receita')
    paid = models.BooleanField(default=False, verbose_name='Pago')
    project = models.ForeignKey(ModelProject, on_delete=models.CASCADE, related_name='inflows', verbose_name='Projeto', blank=True, null=True)
    due_date = models.DateField(verbose_name='Data vencimento', default=now)
    payment_method = models.CharField(choices=METHOD_CHOICES, default='PIX', verbose_name='Método de pagamento')
    value = models.FloatField(verbose_name='Valor')
    refund = models.BooleanField(default=False, verbose_name='Reembolso')
    paid_date = models.DateField(verbose_name='Data pagamento', blank=True,  null=True)


    def __str__(self):
        return self.income

    def save(self, *args, **kwargs):
        if self.paid:
            if self.pk:
                original = type(self).objects.get(pk=self.pk)
                if not original.paid:
                    self.paid_date = now()
            else:
                self.paid_date = now()
        super().save(*args, **kwargs)
