from django.db import models
from django.utils.timezone import now
from projects.models import ModelProject
from supplier.models import ModelSupplier
from django.db import transaction
from dateutil.relativedelta import relativedelta

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
    closing_outflow = models.ForeignKey(ModelOutflow, on_delete=models.CASCADE, null=True, blank=True,  related_name='closing_outflow', verbose_name="Fechada em saída")

    def __str__(self):
        return self.expense
    @property
    def model_name(self):
        return self._meta.model_name

    @transaction.atomic
    def generate_installments(self, num_installments, types_list=None):
        """
        Gera parcelas de crédito em bulk (otimizado para Raspberry Pi).

        Args:
            num_installments (int): Número total de parcelas
            types_list (list): Lista de instâncias de OutflowTypeChoice

        Returns:
            list: Lista com todas as parcelas criadas (incluindo self como primeira)

        Regras:
            - Primeira parcela: data informada
            - Demais parcelas: dia 27 de cada mês subsequente
            - Valor dividido igualmente
        """
        if num_installments <= 1:
            # Sem parcelamento, apenas salva normalmente
            self.save()
            if types_list:
                self.type.set(types_list)
            return [self]

        # Calcula valor de cada parcela
        parcel_value = round(self.value / num_installments, 2)

        # Atualiza a primeira parcela (self)
        original_expense = self.expense
        self.expense = f"{original_expense} (1/{num_installments})"
        self.value = parcel_value
        self.save()

        # Prepara lista de parcelas para bulk_create
        installments_to_create = []

        for i in range(2, num_installments + 1):
            # Calcula data: dia 27 do mês (i-1) meses à frente
            installment_date = self.date + relativedelta(months=i - 1)
            installment_date = installment_date.replace(day=27)

            installment = ModelCreditOutflow(
                expense=f"{original_expense} ({i}/{num_installments})",
                favored=self.favored,
                date=installment_date,
                project=self.project,
                value=parcel_value,
                closing=self.closing
            )
            installments_to_create.append(installment)

        # Cria todas as parcelas em uma única query
        created_installments = ModelCreditOutflow.objects.bulk_create(installments_to_create)

        # Se há tipos, aplica de forma otimizada
        if types_list:
            # Primeira parcela: com signal (para reembolso e outros signals)
            self.type.set(types_list)

            # Demais parcelas: bulk (sem signal, mais rápido)
            if created_installments:
                m2m_relations = []
                for outflow in created_installments:
                    for type_obj in types_list:
                        m2m_relations.append(
                            ModelCreditOutflow.type.through(
                                modelcreditoutflow_id=outflow.id,
                                outflowtypechoice_id=type_obj.id
                            )
                        )

                # Cria todas as relações M2M em uma única query
                ModelCreditOutflow.type.through.objects.bulk_create(
                    m2m_relations,
                    ignore_conflicts=True
                )

        return [self] + created_installments